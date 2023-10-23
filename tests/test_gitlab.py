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
def test_gitlab_extractor(repo):
    extractor = GitlabExtractor(repo)
    meta = extractor.extract()
    meta.serialize(format="ttl")
