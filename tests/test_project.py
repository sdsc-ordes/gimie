"""Test the project module."""
import pytest

from gimie.extractors import GIT_PROVIDERS
from gimie.project import get_parsers, get_extractor
from gimie.parsers import PARSERS


def test_get_parsers():

    repo = "https://example.org/group/project"
    for name, parser in PARSERS.items():
        assert type(get_parsers(repo, [name])[0]) == parser

    # Should raise error if parser not found
    with pytest.raises(ValueError):
        get_parsers(repo, ["bad_parser"])


def test_get_extractor():

    repo = "https://example.org/group/project"
    for prov, extractor in GIT_PROVIDERS.items():
        assert type(get_extractor(repo, prov)) == extractor

    with pytest.raises(ValueError):
        get_extractor(repo, "bad_provider")
