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
import requests
import os
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
    IRI,
)
from gimie.graph.namespaces import SDO
from gimie.utils import get_spdx_url

GH_API = "https://api.github.com"
load_dotenv()


def send_graphql_query(
    query: str, data: Dict[str, Any], headers: Dict[str, str]
) -> Dict[str, Any]:
    """Generic function to send a GraphQL query to the GitHub API."""
    resp = requests.post(
        url=f"{GH_API}/graphql",
        json={
            "query": query,
            "variables": data,
        },
        headers=headers,
    )

    if resp.status_code != 200:
        raise ConnectionError(resp.json()["message"])
    return resp.json()


def query_user_graphql(login: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Use GitHub GraphQL API to extract metadata about a user."""
    user_query = """
    query user($login: String!){
        user(login: $login) {
            avatarUrl
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
            company
        }
    }"""
    user = send_graphql_query(
        user_query, data={"login": login}, headers=headers
    )
    return user


def query_contributors_graphql(url: str, headers: Dict[str, str]) -> Set[str]:
    """Queries the list of contributor usernames of target repository
    using the Github GraphQL API.
    NOTE: This is a workaround for the lack of a contributors field in the GraphQL API."""
    owner, name = urlparse(url).path.strip("/").split("/")
    # Get commits by batches of 100
    commits_query = """
    query repo($owner: String!, $name: String!, $cursor: String) {
        repository(name: $name, owner: $owner) {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: 100, after: $cursor) {
                            nodes {
                                author {
                                    user {
                                        login
                                    }
                                }
                            }
                            pageInfo {
                                hasNextPage
                                endCursor
                            }
                        }
                    }
                }
            }
        }
    }"""

    has_next_page, cursor = True, None
    contributors = set()
    while has_next_page:
        commits = send_graphql_query(
            commits_query,
            data={"owner": owner, "name": name, "cursor": cursor},
            headers=headers,
        )
        commits = commits["data"]["repository"]["defaultBranchRef"]["target"][
            "history"
        ]

        cursor = commits["pageInfo"]["endCursor"]
        has_next_page = commits["pageInfo"]["hasNextPage"]

        # We skip commits which are not authored by a github user
        contributors |= {
            commit["author"]["user"]["login"]
            for commit in commits["nodes"]
            if commit["author"]["user"] is not None
        }
    return contributors


def query_repo_graphql(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Queries the GitHub GraphQL API to extract metadata about
    target repository.

    Parameters
    ----------
    url:
        URL of the repository to query.
    """
    owner, name = urlparse(url).path.strip("/").split("/")
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
    repo = send_graphql_query(
        repo_query, data={"owner": owner, "name": name}, headers=headers
    )
    return repo


@dataclass
class GithubExtractor(Extractor):
    """Extractor for GitHub repositories. Uses the GitHub GraphQL API to
    extract metadata into linked data."""

    path: str
    github_token: Optional[str] = None

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
        response = query_repo_graphql(url, self._set_auth())
        if "errors" in response:
            raise ValueError(response["errors"])

        return response["data"]["repository"]

    def _fetch_contributors(self, url: str) -> List[Person]:
        """Queries the GitHub GraphQL API to extract contributors through the commit list.
        NOTE: This is a workaround for the lack of a contributors field in the GraphQL API."""
        headers = self._set_auth()
        contributors = []
        for username in query_contributors_graphql(url, headers):
            user = query_user_graphql(username, headers)
            contributors.append(self._get_user(user["data"]["user"]))
        return list(contributors)

    def _set_auth(self) -> Any:
        """Set authentication headers for GitHub API requests."""
        try:
            if not self.github_token:
                self.github_token = os.environ.get("ACCESS_TOKEN")
                assert self.github_token
            headers = {"Authorization": f"token {self.github_token}"}

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
    license = IRI(SDO.license)
    path = IRI(SDO.CodeRepository)
    keywords = fields.List(SDO.keywords, fields.String)
    version = fields.String(SDO.version)

    class Meta:
        rdf_type = SDO.SoftwareSourceCode
        model = GithubExtractor
        add_value_types = False
