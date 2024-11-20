import pytest

from gimie.io import LocalResource
from gimie.parsers import get_parser, list_parsers, parse_files
from rdflib import URIRef
from rdflib import Graph, URIRef, Literal


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
    graph = parse_files(
        subject=URIRef("https://exmaple.org/"), files=[license_file]
    )
    assert "https://spdx.org" in graph.serialize(format="ttl")


def test_parse_nothing():
    folder = LocalResource("tests")
    graph = parse_files(subject=URIRef("https://example.org/"), files=[folder])
    assert len(graph) == 0
