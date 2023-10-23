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
