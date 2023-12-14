# Tests fetching metadata from GitHub repositories with different setups.
import pytest

from gimie.extractors.github import GithubExtractor
from gimie.io import RemoteResource


TEST_REPOS = [
    "https://github.com/sdsc-ordes/gimie",  # Owned by organization, has releases
    "https://github.com/apache/openoffice",  # Owned by organization, no releases
    "https://github.com/ishepard/pydriller",  # Owned by user, has releases
    "https://github.com/rmfranken/license_test",  # Contains 2 license files
]


@pytest.mark.parametrize("repo", TEST_REPOS)
def test_github_extract(repo):
    meta = GithubExtractor(repo).extract()
    meta.serialize(format="ttl")


@pytest.mark.parametrize("repo", TEST_REPOS)
def test_github_list_files(repo):
    files = GithubExtractor(repo).list_files()
    assert all(isinstance(f, RemoteResource) for f in files)
