from unittest.mock import patch

import pytest

from gimie.extractors.github import (
    GithubExtractor,
    distinct_non_maintainer_pr_author_count,
    is_non_maintainer_pr_author,
)

REPO_URL = "https://github.com/o/r"


def _pr_page(nodes, has_next=False, end_cursor="cursor1"):
    return {
        "data": {
            "repository": {
                "pullRequests": {
                    "pageInfo": {
                        "hasNextPage": has_next,
                        "endCursor": end_cursor,
                    },
                    "nodes": nodes,
                }
            }
        }
    }


def _pr_node(login, association, typename="User"):
    return {
        "authorAssociation": association,
        "author": {"__typename": typename, "login": login},
    }


def test_is_non_maintainer_pr_author():
    assert is_non_maintainer_pr_author("NONE") is True
    assert is_non_maintainer_pr_author("FIRST_TIME_CONTRIBUTOR") is True
    assert is_non_maintainer_pr_author("MEMBER") is False
    assert is_non_maintainer_pr_author("CONTRIBUTOR") is False


def test_distinct_non_maintainer_pr_author_count():
    authors = [
        ("alice", "NONE"),
        ("alice", "NONE"),
        ("bob", "FIRST_TIMER"),
        ("carol", "MEMBER"),
        ("dave", "CONTRIBUTOR"),
    ]
    assert distinct_non_maintainer_pr_author_count(authors) == 2


@patch.object(GithubExtractor, "fetch_pr_authors")
@patch.object(GithubExtractor, "_fetch_contributors")
def test_extract_includes_pr_author_counts(mock_contributors, mock_fetch):
    mock_contributors.return_value = []
    mock_fetch.return_value = [
        ("alice", "NONE"),
        ("bob", "FIRST_TIMER"),
        ("owner", "OWNER"),
    ]

    extractor = GithubExtractor(REPO_URL, token="fake")
    extractor.__dict__["_repo_data"] = {
        "owner": {
            "avatarUrl": "https://github.com/o.png",
            "login": "o",
            "url": "https://github.com/o",
            "name": "Org",
            "description": "An org",
        },
        "createdAt": "2020-01-01T00:00:00Z",
        "updatedAt": "2021-01-01T00:00:00Z",
        "description": "A repo",
        "repositoryTopics": {"nodes": []},
        "parent": None,
        "latestRelease": None,
        "primaryLanguage": None,
    }

    repo = extractor.extract()

    assert repo.distinct_pr_authors == 3
    assert repo.distinct_non_maintainer_pr_authors == 2
    ttl = repo.serialize(format="ttl")
    assert "distinctPRAuthors" in ttl
    assert "distinctNonMaintainerPRAuthors" in ttl


@patch("gimie.extractors.github.send_graphql_query")
def test_fetch_pr_authors_paginates_and_skips_bots(mock_query):
    mock_query.side_effect = [
        _pr_page(
            [
                _pr_node("alice", "NONE"),
                _pr_node("dependabot[bot]", "NONE", typename="Bot"),
                _pr_node("owner", "OWNER"),
            ],
            has_next=True,
        ),
        _pr_page([_pr_node("bob", "FIRST_TIME_CONTRIBUTOR")]),
    ]

    extractor = GithubExtractor(REPO_URL, token="fake")
    extractor.__dict__["_headers"] = {"Authorization": "token fake"}

    authors = extractor.fetch_pr_authors()

    assert authors == [
        ("alice", "NONE"),
        ("owner", "OWNER"),
        ("bob", "FIRST_TIME_CONTRIBUTOR"),
    ]
    assert distinct_non_maintainer_pr_author_count(authors) == 2
    assert mock_query.call_count == 2
    assert mock_query.call_args_list[1][0][2]["after"] == "cursor1"


@patch("gimie.extractors.github.send_graphql_query")
def test_fetch_pr_authors_raises_on_graphql_errors(mock_query):
    mock_query.return_value = {"errors": [{"message": "nope"}]}

    extractor = GithubExtractor(REPO_URL, token="fake")
    extractor.__dict__["_headers"] = {"Authorization": "token fake"}

    with pytest.raises(ValueError, match="nope"):
        extractor.fetch_pr_authors()
