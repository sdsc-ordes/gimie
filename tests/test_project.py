"""Test the project module."""
import pytest

from gimie.extractors import GIT_PROVIDERS
from gimie.project import check_parser_names, get_extractor
from gimie.parsers import PARSERS


def test_check_parser_names():
    check_parser_names(PARSERS.keys())

    # Should raise error if parser not found
    with pytest.raises(ValueError):
        check_parser_names(["bad_parser"])


def test_get_extractor():
    repo = "https://example.org/group/project"
    for prov, extractor in GIT_PROVIDERS.items():
        assert type(get_extractor(repo, prov)) == extractor

    with pytest.raises(ValueError):
        get_extractor(repo, "bad_provider")
