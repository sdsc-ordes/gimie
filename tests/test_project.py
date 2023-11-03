"""Test the project module."""
import pytest

from gimie.extractors import GIT_PROVIDERS
from gimie.project import get_extractor


def test_get_extractor():
    repo = "https://example.org/group/project"
    for prov, extractor in GIT_PROVIDERS.items():
        assert type(get_extractor(repo, prov)) == extractor

    with pytest.raises(ValueError):
        get_extractor(repo, "bad_provider")
