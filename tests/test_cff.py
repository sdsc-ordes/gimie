from gimie.io import LocalResource
from gimie.parsers import CffParser
from gimie.parsers.cff import get_cff_authors
from rdflib import URIRef, Literal
import pytest


def test_parse_cff():
    cff_file = LocalResource("CITATION.cff")
    with open(cff_file.path, "rb") as f:
        cff_content = f.read()
    authors = get_cff_authors(cff_content)
    assert authors is not None


@pytest.mark.parametrize(
    "cff_file",
    [
        (
            b"""
    cff-version: 1.2.0
    message: "This is a CFF devoid authors or DOI"
    """
        ),
        (
            b"""
    cff-version: 1.2.0
    title: gimie :
    authors:
      family-names: Doe
        given-names: John
        - family-names: Smith
    given-names:
    Jane
        orcid: 0000-0001-2345-6789
    """
        ),
        (
            b"""
    cff-version: 1.2.0
    title: gimie
    authors:
      - family-names: Doe
        given-names: John
        orcid: 0000-0001-2345-6789
      - family-names: Smith
        given-names: Jane
        orcid: http://www.orcid.org/0000-0001-2345-6789
    """
        ),
        (
            b"""
    cff-version: 1.2.0
    title: gimie
    authors:
      - family-names: Doe
        given-names: John
    """
        ),
    ],
)
def test_broken_cff(cff_file):
    assert (
        len(
            CffParser(subject=URIRef("https://example.org/")).parse(
                data=cff_file
            )
        )
        == 0
    )


def test_parse_doi():
    cff_file = b"""
    cff-version: 1.2.0
    message: If you use this software, please cite it using these metadata.
    title: 'napari: a multi-dimensional image viewer for Python'
    identifiers:
    - type: doi
      value: 10.5281/zenodo.3555620
    """
    obj = next(
        CffParser(subject=URIRef("https://example.org/"))
        .parse(data=cff_file)
        .objects()
    )
    assert URIRef("https://doi.org/10.5281/zenodo.3555620") == obj
