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
import requests
from typing import Any, Dict, List, Union


def send_rest_query(
    api: str, query: str, headers: Dict[str, str]
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Generic function to send a query to the GitHub/GitLab rest API."""
    resp = requests.get(
        url=f"{api}/{query}",
        headers=headers,
    )

    if resp.status_code != 200:
        error_msg = resp.json().get("message", "")
        if "API rate limit exceeded" in error_msg:
            raise ConnectionError(
                "Authentication failed: API rate limit exceeded. Please check that you have added "
                "your GITHUB_TOKEN or GITLAB_TOKEN to your environment variables."
            )
        raise ConnectionError(f"API request failed: {error_msg}")
    return resp.json()


def send_graphql_query(
    api: str, query: str, data: Dict[str, Any], headers: Dict[str, str]
) -> Dict[str, Any]:
    """Generic function to send a GraphQL query to the GitHub/GitLab API."""
    resp = requests.post(
        url=f"{api}/graphql",
        json={
            "query": query,
            "variables": data,
        },
        headers=headers,
    )

    if resp.status_code != 200:
        error_msg = resp.json().get("message", "")
        if "API rate limit exceeded" in error_msg:
            raise ConnectionError(
                "Authentication failed: API rate limit exceeded. Please check that you have added "
                "your GITHUB_TOKEN or GITLAB_TOKEN to your environment variables."
            )
        raise ConnectionError(f"API request failed: {error_msg}")
    return resp.json()
