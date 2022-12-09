"""Test the command line interface of gimie"""
import pytest

TEST_GIT_URLS = [
        "https://example.org/git-repo1.git", 
        "https://example.org/git-repo2.git", 
        "https://example.org/git-repo3.git", 
]

@pytest.mark.parametrize("url", TEST_GIT_URLS)
def test_simple_git_repo(url):
    """Extract git metadata only."""
    ...
