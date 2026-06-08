import pytest
from rdflib import Graph, URIRef, Literal, RDF, XSD
from gimie.graph.namespaces import SDO
from gimie.converters.publiccode_converter import (
    convert_to_publiccode,
    get_contacts,
    get_licenses,
    get_maintenance,
    get_property_value,
)

REPO = URIRef("https://github.com/example/repo")


def _base_graph():
    """Create a minimal graph with a SoftwareSourceCode node."""
    g = Graph()
    g.add((REPO, RDF.type, SDO.SoftwareSourceCode))
    g.add((REPO, SDO.name, Literal("org/my-project")))
    return g


class TestGetPropertyValue:
    def test_returns_value(self):
        g = Graph()
        g.add((REPO, SDO.name, Literal("hello")))
        assert get_property_value(g, REPO, SDO.name) == "hello"

    def test_returns_empty_string_when_missing(self):
        g = Graph()
        assert get_property_value(g, REPO, SDO.name) == ""


class TestGetLicenses:
    def test_single_license(self):
        g = Graph()
        g.add((REPO, SDO.license, URIRef("https://spdx.org/licenses/MIT.html")))
        assert get_licenses(g, REPO) == "MIT"

    def test_multiple_licenses(self):
        g = Graph()
        g.add((REPO, SDO.license, URIRef("https://spdx.org/licenses/MIT.html")))
        g.add((REPO, SDO.license, URIRef("https://spdx.org/licenses/Apache-2.0.html")))
        result = get_licenses(g, REPO)
        assert set(result.split(",")) == {"MIT", "Apache-2.0"}

    def test_no_license_returns_none(self):
        g = Graph()
        assert get_licenses(g, REPO) is None


class TestGetContacts:
    def test_extracts_name_and_email(self):
        g = Graph()
        person = URIRef("https://example.com/person")
        g.add((REPO, SDO.author, person))
        g.add((person, SDO.name, Literal("Alice")))
        g.add((person, SDO.email, Literal("alice@example.com")))
        contacts = get_contacts(g, REPO, SDO.author)
        assert len(contacts) == 1
        assert contacts[0]["name"] == "Alice"
        assert contacts[0]["email"] == "alice@example.com"

    def test_name_only(self):
        g = Graph()
        person = URIRef("https://example.com/person")
        g.add((REPO, SDO.author, person))
        g.add((person, SDO.name, Literal("Bob")))
        contacts = get_contacts(g, REPO, SDO.author)
        assert contacts == [{"name": "Bob"}]

    def test_empty_when_no_contacts(self):
        g = Graph()
        assert get_contacts(g, REPO, SDO.author) == []


class TestGetMaintenance:
    def test_internal_when_authors(self):
        g = Graph()
        person = URIRef("https://example.com/person")
        g.add((REPO, SDO.author, person))
        g.add((person, SDO.name, Literal("Alice")))
        result = get_maintenance(g, REPO)
        assert result["type"] == "internal"
        assert len(result["contacts"]) == 1

    def test_community_when_contributors_only(self):
        g = Graph()
        person = URIRef("https://example.com/person")
        g.add((REPO, SDO.contributor, person))
        g.add((person, SDO.name, Literal("Bob")))
        result = get_maintenance(g, REPO)
        assert result["type"] == "community"

    def test_empty_when_no_people(self):
        g = Graph()
        assert get_maintenance(g, REPO) == {}


class TestConvertToPubliccode:
    def test_minimal(self):
        g = _base_graph()
        result = convert_to_publiccode(g)
        assert result["publiccodeYmlVersion"] == "0.5.0"
        assert result["name"] == "my-project"
        assert result["url"] == str(REPO)
        assert "description" not in result
        assert "legal" not in result
        assert "maintenance" not in result

    def test_short_description(self):
        g = _base_graph()
        g.add((REPO, SDO.description, Literal("A short description")))
        result = convert_to_publiccode(g)
        assert result["description"]["en"]["shortDescription"] == "A short description"
        assert "longDescription" not in result["description"]["en"]

    def test_long_description(self):
        g = _base_graph()
        long_text = "A" * 200
        g.add((REPO, SDO.description, Literal(long_text)))
        result = convert_to_publiccode(g)
        assert result["description"]["en"]["longDescription"] == long_text
        assert "shortDescription" not in result["description"]["en"]

    def test_too_short_description_excluded(self):
        g = _base_graph()
        g.add((REPO, SDO.description, Literal("tiny")))
        result = convert_to_publiccode(g)
        assert "description" not in result

    def test_no_software_source_code_raises(self):
        g = Graph()
        with pytest.raises(ValueError, match="No SoftwareSourceCode node found"):
            convert_to_publiccode(g)

    def test_software_version(self):
        g = _base_graph()
        g.add((REPO, SDO.version, Literal("1.2.3")))
        result = convert_to_publiccode(g)
        assert result["softwareVersion"] == "1.2.3"

    def test_release_date_from_date_published(self):
        g = _base_graph()
        g.add((REPO, SDO.datePublished, Literal("2024-03-15", datatype=XSD.date)))
        result = convert_to_publiccode(g)
        assert result["releaseDate"] == "2024-03-15"

    def test_release_date_falls_back_to_date_modified(self):
        g = _base_graph()
        g.add((REPO, SDO.dateModified, Literal("2024-06-01", datatype=XSD.date)))
        result = convert_to_publiccode(g)
        assert result["releaseDate"] == "2024-06-01"

    def test_release_date_prefers_date_published(self):
        g = _base_graph()
        g.add((REPO, SDO.datePublished, Literal("2024-03-15", datatype=XSD.date)))
        g.add((REPO, SDO.dateModified, Literal("2024-06-01", datatype=XSD.date)))
        result = convert_to_publiccode(g)
        assert result["releaseDate"] == "2024-03-15"

    def test_full_graph(self):
        g = _base_graph()
        g.add((REPO, SDO.description, Literal("A decent project description")))
        g.add((REPO, SDO.license, URIRef("https://spdx.org/licenses/MIT.html")))
        g.add((REPO, SDO.version, Literal("2.0.0")))
        g.add((REPO, SDO.datePublished, Literal("2024-01-01", datatype=XSD.date)))
        person = URIRef("https://example.com/alice")
        g.add((REPO, SDO.author, person))
        g.add((person, SDO.name, Literal("Alice")))
        g.add((person, SDO.email, Literal("alice@example.com")))

        result = convert_to_publiccode(g)
        assert result["name"] == "my-project"
        assert result["softwareVersion"] == "2.0.0"
        assert result["releaseDate"] == "2024-01-01"
        assert result["description"]["en"]["shortDescription"] == "A decent project description"
        assert result["legal"]["license"] == "MIT"
        assert result["maintenance"]["type"] == "internal"
        assert result["maintenance"]["contacts"][0]["name"] == "Alice"
        assert result["maintenance"]["contacts"][0]["email"] == "alice@example.com"
