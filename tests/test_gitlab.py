from gimie.sources.gitlab import GitlabExtractor

TEST_REPOS = [
    "https://gitlab.com/inkscape/inkscape",  # Owned by multiple persons, has releases
    "https://gitlab.com/openrgb-pvazny/OpenRGB",  # No user owner so group owner, no releases
    "https://gitlab.com/gitlab-org/gitlab-runner",  # No user owner so group owner, has releases
]


@pytest.mark.parametrize("repo", TEST_REPOS)
def test_gitlab_extractor(repo):
    meta = GitlabExtractor(repo)
    meta.extract()
    meta.serialize(format="ttl")
