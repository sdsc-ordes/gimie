
import requests
from typing import Any, Dict

def send_rest_query(api: str, query: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Generic function to send a query to the GitHub/GitLab rest API."""
    resp = requests.get(
        url=f"{api}/{query}",
        headers=headers,
    )

    if resp.status_code != 200:
        raise ConnectionError(resp.json()["message"])
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
        raise ConnectionError(resp.json()["message"])
    return resp.json()


def query_graphql(api: str, repo_query: str, data: dict, headers: Dict[str, str]) -> Dict[str, Any]:
    """Queries the GitHub GraphQL API to extract metadata about
    target repository.

    Parameters
    ----------
    api:
        URL for GraphQL API
    repo_query:
        query defining what information should be retrieved from the GraphQL API.
    data:
        parameters of the query
    """
    repo = send_graphql_query(
        api, repo_query, data=data, headers=headers
    )
    return repo