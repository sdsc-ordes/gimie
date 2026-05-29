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
from dateutil.parser import isoparse
from functools import cached_property
import os
import requests
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
from dotenv import load_dotenv

from gimie.extractors.abstract import Extractor
from gimie.models import (
    Organization,
    Person,
    Repository,
)

from gimie.io import RemoteResource
from gimie.extractors.common.queries import (
    send_rest_query,
    send_graphql_query,
)

GH_API = "https://api.github.com"
load_dotenv()

NON_MAINTAINER_ASSOCIATIONS = frozenset(
    {"NONE", "FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER"}
)

_PR_AUTHORS_QUERY = """
query prAuthors($owner: String!, $name: String!, $after: String) {
    repository(owner: $owner, name: $name) {
        pullRequests(
            first: 100
            after: $after
            states: [OPEN, CLOSED, MERGED]
            orderBy: {field: CREATED_AT, direction: DESC}
        ) {
            pageInfo { hasNextPage endCursor }
            nodes {
                authorAssociation
                author {
                    __typename
                    ... on User { login }
                    ... on Bot { login }
                    ... on Organization { login }
                }
            }
        }
    }
}
"""


def is_non_maintainer_pr_author(association: str) -> bool:
    """True when GitHub marks the PR author as external to the repo team."""
    return association in NON_MAINTAINER_ASSOCIATIONS


def distinct_non_maintainer_pr_author_count(
    authors: List[tuple[str, str]],
) -> int:
    """Count unique logins with a non-maintainer authorAssociation."""
    return len(
        {
            login
            for login, association in authors
            if is_non_maintainer_pr_author(association)
        }
    )


def query_contributors(
    url: str, headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Queries the list of contributors of target repository
    using GitHub's REST and GraphQL APIs. Returns a list of GraphQL User nodes.
    NOTE: This is a workaround for the lack of a contributors field in the GraphQL API.
    """
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
    max_pr_pages: int = 10

    def list_files(self) -> List[RemoteResource]:
        """takes the root repository folder and returns the list of files present"""
        file_list = []
        file_dict = self._repo_data["object"]["entries"]
        repo_url = self._repo_data["url"]
        defaultbranchref = self._repo_data["defaultBranchRef"]["name"]

        for item in file_dict:
            file = RemoteResource(
                path=item["name"],
                url=f'{repo_url}/raw/{defaultbranchref}/{item["path"]}',
                headers=self._headers,
            )
            file_list.append(file)
        return file_list

    def extract(self) -> Repository:
        """Extract metadata from target GitHub repository."""
        data = self._repo_data

        repo_meta = dict(
            authors=[self._get_author(data["owner"])],
            contributors=self._fetch_contributors(),
            date_created=isoparse(data["createdAt"][:-1]),
            date_modified=isoparse(data["updatedAt"][:-1]),
            description=data["description"],
            name=self.path,
            keywords=self._get_keywords(*data["repositoryTopics"]["nodes"]),
            url=self.url,
        )
        if data["parent"]:
            repo_meta["parent_repository"] = data["parent"]["url"]

        if data["latestRelease"]:
            repo_meta["date_published"] = isoparse(
                data["latestRelease"]["publishedAt"]
            )

        if data["primaryLanguage"] is not None:
            repo_meta["prog_langs"] = [data["primaryLanguage"]["name"]]

        if data["latestRelease"]:
            version = data["latestRelease"]["name"]
            download_url = f"{self.url}/archive/refs/tags/{version}.tar.gz"
            repo_meta["download_url"] = download_url
            repo_meta["version"] = version

        pr_authors = self.fetch_pr_authors(max_pages=self.max_pr_pages)
        repo_meta["distinct_pr_authors"] = len(
            {login for login, _ in pr_authors}
        )
        repo_meta["distinct_non_maintainer_pr_authors"] = (
            distinct_non_maintainer_pr_author_count(pr_authors)
        )

        return Repository(**repo_meta)  # type: ignore

    @cached_property
    def _repo_data(self) -> Dict[str, Any]:
        """Repository metadata fetched from GraphQL endpoint."""
        owner, name = self.path.split("/")
        data = {"owner": owner, "name": name}
        repo_query = """
        query repo($owner: String!, $name: String!) {
            repository(name: $name, owner: $owner) {
                url
                parent {url}
                createdAt
                description
                latestRelease {
                    publishedAt
                    name
                }
                defaultBranchRef {
                    name
                }
                object(expression: "HEAD:") {
                    ... on Tree {

                        entries {
                            name
                            path
                            }
                        }
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
        response = send_graphql_query(GH_API, repo_query, data, self._headers)

        if "errors" in response:
            raise ValueError(response["errors"])

        return response["data"]["repository"]

    def fetch_pr_authors(self, max_pages: int = 10) -> List[tuple[str, str]]:
        """Fetch PR authors as (login, authorAssociation) pairs.

        Paginates up to ``max_pages`` (100 PRs each). Bots and PRs without
        an author login are skipped.
        """
        owner, name = self.path.split("/")
        cursor: Optional[str] = None
        authors: List[tuple[str, str]] = []

        for _ in range(max_pages):
            response = send_graphql_query(
                GH_API,
                _PR_AUTHORS_QUERY,
                {"owner": owner, "name": name, "after": cursor},
                self._headers,
            )
            if "errors" in response:
                raise ValueError(response["errors"])

            pull_requests = response["data"]["repository"]["pullRequests"]
            for node in pull_requests["nodes"]:
                author = node.get("author") or {}
                login = author.get("login")
                if not login:
                    continue
                if author.get("__typename") == "Bot" or login.endswith(
                    "[bot]"
                ):
                    continue
                authors.append((login, node["authorAssociation"]))

            page_info = pull_requests["pageInfo"]
            if not page_info["hasNextPage"]:
                break
            cursor = page_info["endCursor"]

        return authors

    def _fetch_contributors(self) -> List[Person]:
        """Queries the GitHub GraphQL API to extract contributors through the commit list.
        NOTE: This is a workaround for the lack of a contributors field in the GraphQL API.
        """
        contributors = []
        resp = query_contributors(self.url, self._headers)
        for user in resp:
            contributors.append(self._get_user(user))
        return list(contributors)

    @cached_property
    def _headers(self) -> Any:
        """Set authentication headers for GitHub API requests."""
        try:
            if not self.token:
                self.token = os.environ.get("GITHUB_TOKEN")
                if not self.token:
                    raise ValueError(
                        "GitHub token not found. Please set the GITHUB_TOKEN environment variable "
                        "with your GitHub personal access token."
                    )
            headers = {"Authorization": f"token {self.token}"}

            login = requests.get(f"{GH_API}/user", headers=headers)
            if not login.ok or not login.json().get("login"):
                raise ValueError(
                    "GitHub authentication failed. Please check that your GITHUB_TOKEN is valid."
                )
            return headers
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to GitHub API: {str(e)}")

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
