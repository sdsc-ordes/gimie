from gimie.io import LocalResource
from gimie.parsers import CffParser
from gimie.parsers.cff import get_cff_authors
from rdflib import URIRef


def test_parse_cff():
    cff_file = LocalResource("CITATION.cff")
    with open(cff_file.path, "rb") as f:
        cff_content = f.read()
    authors = get_cff_authors(cff_content)
    assert authors is not None


def test_broken_cff():
    cff_file_emptyish = b"""
    cff-version: 1.2.0
    message: "This is a CFF devoid authors or DOI"
    """
    cff_file_bad_syntax = b"""
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
    cff_file_broken_orcid = b"""
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
    cff_file_author_without_orcid = b"""
    cff-version: 1.2.0
    title: gimie
    authors:
      - family-names: Doe
        given-names: John
    """

    # empty graph = \n according to rdflib
    assert (
        CffParser(subject=URIRef("https://example.org/"))
        .parse(data=cff_file_emptyish)
        .serialize(format="ttl")
        == "\n"
    )
    assert (
        CffParser(subject=URIRef("https://example.org/"))
        .parse(data=cff_file_bad_syntax)
        .serialize(format="ttl")
        == "\n"
    )
    assert (
        CffParser(subject=URIRef("https://example.org/"))
        .parse(data=cff_file_broken_orcid)
        .serialize(format="ttl")
        == "\n"
    )
    assert (
        CffParser(subject=URIRef("https://example.org/"))
        .parse(data=cff_file_author_without_orcid)
        .serialize(format="ttl")
        == "\n"
    )


def test_doi():
    cff_file = b"""
    cff-version: 1.2.0
    title: gimie
    doi: 10.5281/zenodo.1234567
    """
    assert "https://doi.org/10.5281/zenodo.1234567" in CffParser(
        subject=URIRef("https://example.org/")
    ).parse(data=cff_file).serialize(format="ttl")
