import pytest

from gimie.io import LocalResource
from gimie.parsers import get_parser, list_parsers, parse_files


def test_get_parser():
    # All parsers are available
    for name in list_parsers():
        get_parser(name)


def test_get_bad_parser():
    # Should raise error if parser not found
    with pytest.raises(ValueError):
        get_parser("bad_parser")


def test_parse_license():
    license_file = LocalResource("LICENSE")
    properties = parse_files([license_file])
    assert "license" in next(iter(properties))[0]


def test_parse_nothing():
    folder = LocalResource("tests")
    properties = parse_files([folder])
    assert len(properties) == 0
