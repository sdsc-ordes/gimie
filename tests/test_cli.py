"""Test the command line interface of gimie"""
import pytest

TEST_GIT_URLS = [
        "https://example.org/git-repo1.git", 
        "https://example.org/git-repo2.git", 
        "https://example.org/git-repo3.git", 
]

@pytest.mark.parametrize("url", TEST_GIT_URLS)
def test_git_remote(url):
    """Returns correct git metadata from target URL."""
    ...

def test_git_local():
    """Returns correct git metadata from local repo path."""
    ...

def test_invalid_url():
    """Fails gracefully on invalid URL."""
    invalid_url = "https://github.com/SDSC-ORD/not-exist"
    ...

#test