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
import os
import requests
from datetime import datetime
from dateutil.parser import isoparse
from functools import cached_property
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
from dotenv import load_dotenv
from gimie.io import RemoteResource
from gimie.models import (
    Organization,
    Person,
    Repository,
)
from gimie.extractors.abstract import Extractor
from gimie.extractors.common.queries import send_graphql_query, send_rest_query

load_dotenv()


@dataclass
class GitlabExtractor(Extractor):
    """Extractor for Gitlab repositories. Uses the Gitlab GraphQL API to
    extract metadata into linked data.
    url: str
        The url of the git repository.
    base_url: Optional[str]
        The base url of the git remote.

    """

    url: str
    base_url: Optional[str] = None
    local_path: Optional[str] = None

    token: Optional[str] = None

    def list_files(self) -> List[RemoteResource]:
        """takes the root repository folder and returns the list of files present"""
        file_list = []
        file_dict = self._repo_data["repository"]["tree"]["blobs"]["nodes"]
        defaultbranchref = self._repo_data["repository"]["rootRef"]
        for item in file_dict:
            file = RemoteResource(
                path=item["name"],
                url=f'{self.url}/-/raw/{defaultbranchref}/{item["name"]}',
                headers=self._headers,
            )
            file_list.append(file)
        return file_list

    def extract(self) -> Repository:
        """Extract metadata from target Gitlab repository."""

        # fetch metadata
        data = self._repo_data

        # NOTE(identifier): Each Gitlab project has a unique identifier (integer)
        # NOTE(author): Fetches only the group directly related to the project
        # the group takes the form: parent/subgroup

        # NOTE(contributors): contributors = project members
        # who are not owners + those that have written merge requests
        # owners are either multiple individuals or a group. If no user
        # is marked as owner, contributors are project members or merge
        # request authors
        repo_meta = dict(
            authors=self._safe_extract_author(data),
            contributors=self._safe_extract_contributors(data),
            date_created=isoparse(data["createdAt"][:-1]),
            date_modified=isoparse(data["lastActivityAt"][:-1]),
            description=data["description"],
            identifier=urlparse(data["id"]).path.split("/")[2],
            keywords=data["topics"],
            name=self.path,
            prog_langs=[lang["name"] for lang in data["languages"]],
            url=self.url,
        )

        if data["releases"]["edges"]:
            repo_meta["date_published"] = isoparse(
                data["releases"]["edges"][0]["node"]["releasedAt"]
            )

        if data["releases"] and (len(data["releases"]["edges"]) > 0):
            # go into releases and take the name from the first node (most recent)
            version = data["releases"]["edges"][0]["node"]["name"]
            repo_meta["version"] = version
            repo_meta[
                "download_url"
            ] = f"{self.url}/-/archive/{version}/{self.path.split('/')[-1]}-{version}.tar.gz"
        return Repository(**repo_meta)  # type: ignore

    def _safe_extract_author(
        self, repo: Dict[str, Any]
    ) -> List[Union[Person, Organization]]:
        """Extract the author from a GraphQL repository node.
        projectMembers is used if available, otherwise the author
        is inferred from the project url."""
        members = repo["projectMembers"]["edges"]
        if len(members) > 0:
            owners = filter(
                lambda m: m["node"]["accessLevel"]["stringValue"] == "OWNER",
                members,
            )
            return [
                self._get_author(owner["node"]["user"]) for owner in owners
            ]

        if repo["group"] is not None:
            return [self._get_author(repo["group"])]

        # If the author is absent from the GraphQL response (permission bug),
        # fallback to the REST API
        return [self._user_from_rest(self.path.split("/")[0])]

    def _safe_extract_contributors(
        self, repo: dict[str, Any]
    ) -> List[Person] | None:
        members = [
            user["node"]["user"]
            for user in repo["projectMembers"]["edges"]
            if user["node"]["accessLevel"]["stringValue"] != "OWNER"
        ]
        merge_request_authors = [
            author["node"]["author"]
            for author in repo["mergeRequests"]["edges"]
        ]
        contributors = members + merge_request_authors
        # Drop duplicate (unhashable) dicts by "id" key
        uniq_contrib = list({c["id"]: c for c in contributors}.values())
        return [self._get_user(contrib) for contrib in uniq_contrib]

    @cached_property
    def _repo_data(self) -> Dict[str, Any]:
        """Fetch repository metadata from GraphQL endpoint."""
        data = {"path": self.path}
        project_query = """
        query project_query($path: ID!) {
            project(fullPath: $path) {
                name
                id
                description
                createdAt
                lastActivityAt
                group {
                    id
                    name
                    description
                    avatarUrl
                    webUrl
                }
                languages {
                    name
                    share
                }
                topics
                projectMembers {
                    edges {
                        node {
                        id
                        accessLevel {
                            stringValue
                        }
                        user {
                            id
                            name
                            username
                            publicEmail
                            webUrl
                        }
                        }
                    }
                }
                mergeRequests{
                    edges {
                    node {
                        author {
                        id
                        name
                        username
                        publicEmail
                        webUrl
                        }
                    }
                    }
                }
                repository {
                    rootRef
                    tree{
                        blobs{
                            nodes {
                                name
                                webUrl
                            }
                        }
                    }
                }
                releases {
                    edges {
                    node {
                        name
                        releasedAt
                    }
                    }
                }
        }
        }
        """
        response = send_graphql_query(
            self.graphql_endpoint, project_query, data, self._headers
        )
        if "errors" in response:
            raise ValueError(response["errors"])

        return response["data"]["project"]

    @cached_property
    def _headers(self) -> Any:
        """Set authentication headers for Gitlab API requests."""
        try:
            if not self.token:
                self.token = os.environ.get("GITLAB_TOKEN")
                assert self.token
            headers = {"Authorization": f"token {self.token}"}

            login = requests.get(f"{self.rest_endpoint}/user", headers=headers)
            assert login.json().get("login")
        except AssertionError:
            return {}
        else:
            return headers

    def _get_author(self, node: Dict[str, Any]) -> Union[Organization, Person]:
        """Given the GraphQL node for a repository owner,
        return the author as a Person or Organization object."""
        # Is this the best test?
        if "username" in node:
            return self._get_user(node)
        return self._get_organization(node)

    def _get_organization(self, node: Dict[str, Any]) -> Organization:
        """Extract details from a GraphQL organization node."""
        return Organization(
            _id=node["webUrl"],
            name=node["name"],
            description=node.get("description"),
            logo=node.get("avatarUrl"),
        )

    def _get_user(self, node: Dict[str, Any]) -> Person:
        """Extract details from a GraphQL user node."""
        return Person(
            _id=node["webUrl"],
            identifier=node["username"],
            name=node.get("name"),
            email=node.get("publicEmail"),
        )

    def _user_from_rest(self, username: str) -> Person:
        """Given a username, use the REST API to retrieve the Person object."""

        author = send_rest_query(
            self.rest_endpoint,
            f"/users?username={username}",
            self._headers,
        )
        if isinstance(author, list):
            author = author[0]

        return Person(
            _id=author["web_url"],
            identifier=author["username"],
            name=author.get("name"),
        )

    @property
    def rest_endpoint(self) -> str:
        return f"{self.base}/api/v4/"

    @property
    def graphql_endpoint(self) -> str:
        return f"{self.base}/api"
