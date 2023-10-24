from gimie.io import RemoteResource
from gimie.sources.gitlab import GitlabExtractor
import pytest

TEST_REPOS = [
    "https://gitlab.com/inkscape/inkscape",  # Owned by multiple persons, has releases
    "https://gitlab.com/openrgb-pvazny/OpenRGB",  # No user owner so group owner, no releases
    "https://gitlab.com/gitlab-org/gitlab-runner",  # No user owner so group owner, has releases
    "https://gitlab.com/commonground/haven/haven",  # Nested groups
    "https://gitlab.com/edouardklein/falsisign",  # owned by user
    "https://gitlab.com/rmfranken/test-licenses",  # Contains 2 license files
]


@pytest.mark.parametrize("repo", TEST_REPOS)
def test_gitlab_extract(repo):
    extractor = GitlabExtractor(repo)
    meta = extractor.extract()
    meta.serialize(format="ttl")


@pytest.mark.parametrize("repo", TEST_REPOS)
def test_gitlab_list_files(repo):
    files = GitlabExtractor(repo).list_files()
    assert all(isinstance(f, RemoteResource) for f in files)
