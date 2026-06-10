import pytest
from rdflib import Graph, URIRef, Literal, RDF, XSD
from gimie.graph.namespaces import SDO
from gimie.converters.publiccode_converter import convert_to_publiccode

REPO = URIRef("https://github.com/example/repo")


def _base_graph():
    """Minimal graph with a SoftwareSourceCode node."""
    g = Graph()
    g.add((REPO, RDF.type, SDO.SoftwareSourceCode))
    g.add((REPO, SDO.name, Literal("org/my-project")))
    return g


class TestMinimal:
    def test_required_fields(self):
        result = convert_to_publiccode(_base_graph())
        assert result["publiccodeYmlVersion"] == "0.5.0"
        assert result["name"] == "my-project"
        assert result["url"] == str(REPO)

    def test_optional_fields_absent_when_no_data(self):
        result = convert_to_publiccode(_base_graph())
        assert "description" not in result
        assert "legal" not in result
        assert result["maintenance"] == {"type": "none"}
        assert "softwareVersion" not in result
        assert "releaseDate" not in result

    def test_no_software_source_code_raises(self):
        with pytest.raises(
            ValueError, match="No node of type"
        ):
            convert_to_publiccode(Graph())


class TestDescription:
    def test_short_description(self):
        g = _base_graph()
        g.add((REPO, SDO.description, Literal("A short description")))
        result = convert_to_publiccode(g)
        assert (
            result["description"]["en"]["shortDescription"]
            == "A short description"
        )
        assert "longDescription" not in result["description"]["en"]

    def test_long_description(self):
        g = _base_graph()
        long_text = "A" * 200
        g.add((REPO, SDO.description, Literal(long_text)))
        result = convert_to_publiccode(g)
        assert result["description"]["en"]["longDescription"] == long_text
        assert "shortDescription" not in result["description"]["en"]

    def test_too_short_excluded(self):
        g = _base_graph()
        g.add((REPO, SDO.description, Literal("tiny")))
        assert "description" not in convert_to_publiccode(g)


class TestLicense:
    def test_single_license(self):
        g = _base_graph()
        g.add(
            (REPO, SDO.license, URIRef("https://spdx.org/licenses/MIT.html"))
        )
        assert convert_to_publiccode(g)["legal"]["license"] == "MIT"

    def test_multiple_licenses(self):
        g = _base_graph()
        g.add(
            (REPO, SDO.license, URIRef("https://spdx.org/licenses/MIT.html"))
        )
        g.add(
            (
                REPO,
                SDO.license,
                URIRef("https://spdx.org/licenses/Apache-2.0.html"),
            )
        )
        license_str = convert_to_publiccode(g)["legal"]["license"]
        assert set(license_str.split(",")) == {"MIT", "Apache-2.0"}

    def test_no_license_omits_legal(self):
        assert "legal" not in convert_to_publiccode(_base_graph())


class TestVersion:
    def test_software_version(self):
        g = _base_graph()
        g.add((REPO, SDO.version, Literal("1.2.3")))
        assert convert_to_publiccode(g)["softwareVersion"] == "1.2.3"

    def test_release_date_from_date_published(self):
        g = _base_graph()
        g.add(
            (REPO, SDO.datePublished, Literal("2024-03-15", datatype=XSD.date))
        )
        assert convert_to_publiccode(g)["releaseDate"] == "2024-03-15"

    def test_release_date_falls_back_to_date_modified(self):
        g = _base_graph()
        g.add(
            (REPO, SDO.dateModified, Literal("2024-06-01", datatype=XSD.date))
        )
        assert convert_to_publiccode(g)["releaseDate"] == "2024-06-01"

    def test_release_date_prefers_date_published(self):
        g = _base_graph()
        g.add(
            (REPO, SDO.datePublished, Literal("2024-03-15", datatype=XSD.date))
        )
        g.add(
            (REPO, SDO.dateModified, Literal("2024-06-01", datatype=XSD.date))
        )
        assert convert_to_publiccode(g)["releaseDate"] == "2024-03-15"


class TestMaintenance:
    def test_internal_type_from_authors(self):
        g = _base_graph()
        person = URIRef("https://example.com/alice")
        g.add((REPO, SDO.author, person))
        g.add((person, SDO.name, Literal("Alice")))
        result = convert_to_publiccode(g)
        assert result["maintenance"]["type"] == "internal"
        assert result["maintenance"]["contacts"] == [{"name": "Alice"}]

    def test_no_authors_defaults_to_none_type(self):
        assert (
            convert_to_publiccode(_base_graph())["maintenance"]["type"]
            == "none"
        )

    def test_contact_with_email(self):
        g = _base_graph()
        person = URIRef("https://example.com/alice")
        g.add((REPO, SDO.author, person))
        g.add((person, SDO.name, Literal("Alice")))
        g.add((person, SDO.email, Literal("alice@example.com")))
        contact = convert_to_publiccode(g)["maintenance"]["contacts"][0]
        assert contact["email"] == "alice@example.com"


class TestFullGraph:
    def test_all_fields(self):
        g = _base_graph()
        g.add((REPO, SDO.description, Literal("A decent project description")))
        g.add(
            (REPO, SDO.license, URIRef("https://spdx.org/licenses/MIT.html"))
        )
        g.add((REPO, SDO.version, Literal("2.0.0")))
        g.add(
            (REPO, SDO.datePublished, Literal("2024-01-01", datatype=XSD.date))
        )
        person = URIRef("https://example.com/alice")
        g.add((REPO, SDO.author, person))
        g.add((person, SDO.name, Literal("Alice")))
        g.add((person, SDO.email, Literal("alice@example.com")))

        result = convert_to_publiccode(g)
        assert result["name"] == "my-project"
        assert result["softwareVersion"] == "2.0.0"
        assert result["releaseDate"] == "2024-01-01"
        assert (
            result["description"]["en"]["shortDescription"]
            == "A decent project description"
        )
        assert result["legal"]["license"] == "MIT"
        assert result["maintenance"]["type"] == "internal"
        assert result["maintenance"]["contacts"][0] == {
            "name": "Alice",
            "email": "alice@example.com",
        }
