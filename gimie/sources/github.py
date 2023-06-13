# Gimie
# Copyright 2022 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
import requests
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse
from dotenv import load_dotenv

from calamus import fields
from calamus.schema import JsonLDSchema
from rdflib import Graph

from gimie.sources.abstract import Extractor
from gimie.models import (
    Organization,
    OrganizationSchema,
    Person,
    PersonSchema,
)
from gimie.graph.namespaces import SDO
from gimie.sources.common.license import get_spdx_url
from gimie.sources.common.queries import (
    send_rest_query,
    send_graphql_query,
)

GH_API = "https://api.github.com"
load_dotenv()


def query_contributors(
    url: str, headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Queries the list of contributors of target repository
    using Github's REST and GraphQL APIs. Returns a list of GraphQL User nodes.
    NOTE: This is a workaround for the lack of a contributors field in the GraphQL API."""
    owner, name = urlparse(url).path.strip("/").split("/")
    # Get contributors (available in the REST API but not GraphQL)
    data = f"repos/{owner}/{name}/contributors"
    contributors = send_rest_query(GH_API, data, headers=headers)
    ids = [contributor["node_id"] for contributor in contributors]
    # Get all contributors' metadata in 1 GraphQL query
    users_query = """
    query users($ids: [ID!]!) {
        nodes(ids: $ids) {
            ... on User {
                avatarUrl
                company
                login
                name
                organizations(first: 100) {
                    nodes {
                        avatarUrl
                        description
                        login
                        name
                        url
                    }
                }
                url
            }
        }
    }"""

    contributors = send_graphql_query(
        GH_API, users_query, data={"ids": ids}, headers=headers
    )
    # Drop empty users (e.g. dependabot)
    return [user for user in contributors["data"]["nodes"] if user]


@dataclass
class GithubExtractor(Extractor):
    """Extractor for GitHub repositories. Uses the GitHub GraphQL API to
    extract metadata into linked data."""

    path: str
    _id: Optional[str] = None
    token: Optional[str] = None

    name: Optional[str] = None
    author: Optional[Union[Organization, Person]] = None
    contributors: Optional[List[Person]] = None
    prog_langs: Optional[List[str]] = None
    download_url: Optional[str] = None
    description: Optional[str] = None
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    keywords: Optional[List[str]] = None
    license: Optional[str] = None
    software_version: Optional[str] = None

    def to_graph(self) -> Graph:
        """Convert repository to RDF graph."""
        jd = GithubExtractorSchema().dumps(self)
        g: Graph = Graph().parse(format="json-ld", data=str(jd))
        g.bind("schema", SDO)
        return g

    def extract(self):
        """Extract metadata from target GitHub repository."""
        if self._id is None:
            self._id = self.path
        self.name = urlparse(self.path).path.strip("/")
        data = self._fetch_repo_data(self.path)
        self.author = self._get_author(data["owner"])
        self.contributors = self._fetch_contributors(self.path)
        self.description = data["description"]
        self.date_created = datetime.fromisoformat(data["createdAt"][:-1])
        self.date_modified = datetime.fromisoformat(data["updatedAt"][:-1])
        # If license is available, convert to standard SPDX URL
        if data["licenseInfo"] is not None:
            self.license = get_spdx_url(data["licenseInfo"]["spdxId"])
        if data["primaryLanguage"] is not None:
            self.prog_langs = [data["primaryLanguage"]["name"]]
        self.keywords = self._get_keywords(*data["repositoryTopics"]["nodes"])
        last_release = data["latestRelease"]
        if last_release is not None:
            self.version = last_release["name"]
            self.download_url = (
                f"{self.path}/archive/refs/tags/{self.version}.tar.gz"
            )

    def _fetch_repo_data(self, url: str) -> Dict[str, Any]:
        """Fetch repository metadata from GraphQL endpoint."""
        owner, name = urlparse(url).path.strip("/").split("/")
        data = {"owner": owner, "name": name}
        repo_query = """
        query repo($owner: String!, $name: String!) {
            repository(name: $name, owner: $owner) {
                createdAt
                description
                latestRelease {
                    name
                }
                licenseInfo {
                    spdxId
                }
                mentionableUsers(first: 100) {
                    nodes {
                        login
                        name
                        avatarUrl
                        company
                        organizations(first: 100) {
                            nodes {
                                avatarUrl
                                description
                                login
                                name
                                url
                            }
                        }
                        url
                    }
                }
                name
                owner {
                    avatarUrl
                    login
                    url
                    ... on User {
                        company
                        name
                        organizations(first: 100) {
                            nodes {
                                avatarUrl
                                description
                                login
                                name
                                url
                            }
                        }
                    }
                    ... on Organization {
                        name
                        description
                    }
                }
                primaryLanguage {
                    name
                }
                repositoryTopics(first: 10) {
                    nodes {
                        topic {
                            name
                        }
                    }
                }
                updatedAt
                url
            }
        }
        """
        response = send_graphql_query(
            GH_API, repo_query, data, self._set_auth()
        )
        if "errors" in response:
            raise ValueError(response["errors"])

        return response["data"]["repository"]

    def _fetch_contributors(self, url: str) -> List[Person]:
        """Queries the GitHub GraphQL API to extract contributors through the commit list.
        NOTE: This is a workaround for the lack of a contributors field in the GraphQL API."""
        headers = self._set_auth()
        contributors = []
        resp = query_contributors(url, headers)
        for user in resp:
            contributors.append(self._get_user(user))
        return list(contributors)

    def _set_auth(self) -> Any:
        """Set authentication headers for GitHub API requests."""
        try:
            if not self.token:
                self.token = os.environ.get("GITHUB_TOKEN")
                assert self.token
            headers = {"Authorization": f"token {self.token}"}

            login = requests.get(f"{GH_API}/user", headers=headers)
            assert login.json().get("login")
        except AssertionError:
            return {}
        else:
            return headers

    def _get_keywords(self, *nodes: Dict[str, Any]) -> List[str]:
        """Extract names from GraphQL topic nodes."""
        return [node["topic"]["name"] for node in nodes]

    def _get_organization(self, node: Dict[str, Any]) -> Organization:
        """Extract details from a GraphQL organization node."""
        return Organization(
            _id=node["url"],
            name=node["login"],
            description=node["description"],
            legal_name=node["name"],
            logo=node["avatarUrl"],
        )

    def _get_author(self, node: Dict[str, Any]) -> Union[Organization, Person]:
        """Given the GraphQL node for a repository owner,
        return the author as a Person or Organization object."""

        if "organizations" in node:
            return self._get_user(node)

        return self._get_organization(node)

    def _get_user(self, node: Dict[str, Any]) -> Person:
        """Extract details from a GraphQL user node."""
        # Get user's affiliations
        orgs = [
            self._get_organization(org)
            for org in node["organizations"]["nodes"]
        ]
        return Person(
            _id=node["url"],
            identifier=node["login"],
            name=node["name"],
            affiliations=orgs,
        )


class GithubExtractorSchema(JsonLDSchema):
    """This defines the schema used for json-ld serialization."""

    _id = fields.Id()
    name = fields.String(SDO.name)
    author = fields.Nested(SDO.author, [PersonSchema, OrganizationSchema])
    contributors = fields.Nested(SDO.contributor, PersonSchema, many=True)
    prog_langs = fields.List(SDO.programmingLanguage, fields.String)
    download_url = fields.Raw(SDO.downloadUrl)
    description = fields.String(SDO.description)
    date_created = fields.Date(SDO.dateCreated)
    date_modified = fields.Date(SDO.dateModified)
    license = fields.IRI(SDO.license)
    path = fields.IRI(SDO.CodeRepository)
    keywords = fields.List(SDO.keywords, fields.String)
    version = fields.String(SDO.version)

    class Meta:
        rdf_type = SDO.SoftwareSourceCode
        model = GithubExtractor
        add_value_types = False
