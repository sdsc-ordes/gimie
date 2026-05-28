from rdflib import URIRef, Literal
from rdflib.namespace import RDF

from gimie.graph.namespaces import SDO
from gimie.parsers.publiccode import (
    PublicCodeParser,
    _sanitize_identifier,
)

SUBJECT = "https://example.org/repo"

FULL_PUBLICCODE = b"""
publiccodeYmlVersion: "0.5"
name: example-app
url: https://github.com/org/example-app
softwareVersion: "2.1.0"
releaseDate: "2024-06-15"
platforms:
  - web
developmentStatus: stable
softwareType: standalone/web
isBasedOn: https://github.com/org/upstream
description:
  en:
    shortDescription: A short description of the app.
    longDescription: >
      This is a much longer description of the application
      that goes into more detail about what it does and why.
    features:
      - Feature one
      - Feature two
legal:
  license: Apache-2.0 OR MIT
  mainCopyrightOwner: Example Corp
maintenance:
  type: community
  contacts:
    - name: Jane Doe
      email: jane@example.org
      affiliation: Example Corp
    - name: John Smith
localisation:
  localisationReady: true
  availableLanguages:
    - en
    - it
"""


def test_sanitize_identifier():
    assert _sanitize_identifier("Jane Doe") == "jane_doe"
    assert _sanitize_identifier("Alice") == "alice"


def test_parse_extracts_is_based_on():
    graph = PublicCodeParser(subject=SUBJECT).parse(FULL_PUBLICCODE)
    parents = list(graph.objects(URIRef(SUBJECT), SDO.isBasedOn))
    assert URIRef("https://github.com/org/upstream") in parents


def test_parse_extracts_contacts():
    graph = PublicCodeParser(subject=SUBJECT).parse(FULL_PUBLICCODE)
    authors = list(graph.objects(URIRef(SUBJECT), SDO.author))
    assert len(authors) == 2

    jane_uri = URIRef(f"{SUBJECT}/jane_doe")
    assert (jane_uri, RDF.type, SDO.Person) in graph
    assert (jane_uri, SDO.name, Literal("Jane Doe")) in graph
    assert (jane_uri, SDO.email, Literal("jane@example.org")) in graph
    assert (jane_uri, SDO.affiliation, Literal("Example Corp")) in graph

    john_uri = URIRef(f"{SUBJECT}/john_smith")
    assert (john_uri, SDO.name, Literal("John Smith")) in graph
    assert not list(graph.objects(john_uri, SDO.email))


def test_parse_does_not_add_extractor_fields():
    """Fields already covered by extractors/parsers are not duplicated."""
    graph = PublicCodeParser(subject=SUBJECT).parse(FULL_PUBLICCODE)
    assert not list(graph.objects(URIRef(SUBJECT), SDO.description))
    assert not list(graph.objects(URIRef(SUBJECT), SDO.version))
    assert not list(graph.objects(URIRef(SUBJECT), SDO.datePublished))
    assert not list(graph.objects(URIRef(SUBJECT), SDO.license))


def test_parse_no_contacts():
    data = b"""
publiccodeYmlVersion: "0.5"
name: test
url: https://example.org/test
legal:
  license: MIT
"""
    graph = PublicCodeParser(subject=SUBJECT).parse(data)
    assert not list(graph.objects(URIRef(SUBJECT), SDO.author))


def test_parse_invalid_yaml():
    graph = PublicCodeParser(subject=SUBJECT).parse(b"{{invalid yaml")
    assert len(graph) == 0


def test_parse_empty():
    graph = PublicCodeParser(subject=SUBJECT).parse(b"")
    assert len(graph) == 0
