from rdflib import URIRef, Literal
from rdflib.namespace import RDF

from gimie.graph.namespaces import SDO
from gimie.parsers.publiccode import (
    PublicCodeParser,
    get_publiccode_contacts,
    get_publiccode_is_based_on,
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


def test_get_is_based_on():
    assert get_publiccode_is_based_on(
        {"isBasedOn": "https://github.com/org/upstream"}
    ) == ["https://github.com/org/upstream"]


def test_get_is_based_on_list():
    assert get_publiccode_is_based_on(
        {"isBasedOn": ["https://a.com", "https://b.com"]}
    ) == ["https://a.com", "https://b.com"]


def test_get_is_based_on_missing():
    assert get_publiccode_is_based_on({"name": "test"}) is None


def test_get_contacts():
    pc = {
        "maintenance": {
            "contacts": [
                {
                    "name": "Jane Doe",
                    "email": "jane@example.org",
                    "affiliation": "Example Corp",
                },
                {"name": "John Smith"},
            ]
        }
    }
    contacts = get_publiccode_contacts(pc)
    assert contacts is not None
    assert len(contacts) == 2
    assert contacts[0] == {
        "name": "Jane Doe",
        "email": "jane@example.org",
        "affiliation": "Example Corp",
    }
    assert contacts[1] == {"name": "John Smith"}


def test_get_contacts_missing():
    assert get_publiccode_contacts({"name": "test"}) is None


def test_parse_builds_graph():
    graph = PublicCodeParser(subject=SUBJECT).parse(FULL_PUBLICCODE)

    assert URIRef("https://github.com/org/upstream") in list(
        graph.objects(URIRef(SUBJECT), SDO.isBasedOn)
    )

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


def test_parse_invalid_yaml():
    graph = PublicCodeParser(subject=SUBJECT).parse(b"{{invalid yaml")
    assert len(graph) == 0


def test_parse_empty():
    graph = PublicCodeParser(subject=SUBJECT).parse(b"")
    assert len(graph) == 0
