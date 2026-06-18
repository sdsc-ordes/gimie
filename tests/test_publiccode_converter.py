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
    def test_required_fields_only(self):
        assert convert_to_publiccode(_base_graph()) == {
            "publiccodeYmlVersion": "0.5.0",
            "name": "my-project",
            "url": str(REPO),
            "maintenance": {"type": "none"},
        }

    def test_no_software_source_code_raises(self):
        with pytest.raises(ValueError, match="No node of type"):
            convert_to_publiccode(Graph())


class TestDescription:
    @pytest.mark.parametrize(
        "text,expected",
        [
            (
                "A short description",
                {"en": {"shortDescription": "A short description"}},
            ),
            ("A" * 200, {"en": {"longDescription": "A" * 200}}),
            ("tiny", None),
        ],
        ids=["short", "long", "too-short-omitted"],
    )
    def test_description(self, text, expected):
        g = _base_graph()
        g.add((REPO, SDO.description, Literal(text)))
        assert convert_to_publiccode(g).get("description") == expected


class TestLicense:
    @pytest.mark.parametrize(
        "license_ids,expected",
        [
            (["MIT"], {"MIT"}),
            (["MIT", "Apache-2.0"], {"MIT", "Apache-2.0"}),
            ([], None),
        ],
        ids=["single", "multiple", "none"],
    )
    def test_license(self, license_ids, expected):
        g = _base_graph()
        for lic in license_ids:
            g.add(
                (
                    REPO,
                    SDO.license,
                    URIRef(f"https://spdx.org/licenses/{lic}.html"),
                )
            )
        legal = convert_to_publiccode(g).get("legal")
        found = set(legal["license"].split(",")) if legal else None
        assert found == expected


class TestVersion:
    def test_software_version(self):
        g = _base_graph()
        g.add((REPO, SDO.version, Literal("1.2.3")))
        assert convert_to_publiccode(g)["softwareVersion"] == "1.2.3"

    @pytest.mark.parametrize(
        "dates,expected",
        [
            ({"datePublished": "2024-03-15"}, "2024-03-15"),
            ({"dateModified": "2024-06-01"}, "2024-06-01"),
            (
                {"datePublished": "2024-03-15", "dateModified": "2024-06-01"},
                "2024-03-15",
            ),
        ],
        ids=["published-only", "modified-only", "prefers-published"],
    )
    def test_release_date(self, dates, expected):
        g = _base_graph()
        for predicate, value in dates.items():
            g.add((REPO, SDO[predicate], Literal(value, datatype=XSD.date)))
        assert convert_to_publiccode(g)["releaseDate"] == expected


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

        assert convert_to_publiccode(g) == {
            "publiccodeYmlVersion": "0.5.0",
            "name": "my-project",
            "url": str(REPO),
            "softwareVersion": "2.0.0",
            "releaseDate": "2024-01-01",
            "description": {
                "en": {"shortDescription": "A decent project description"}
            },
            "legal": {"license": "MIT"},
            "maintenance": {
                "type": "internal",
                "contacts": [{"name": "Alice", "email": "alice@example.com"}],
            },
        }
