from rdflib import Graph, URIRef, parser
import hashlib
from calamus import fields
from calamus.schema import JsonLDSchema

schema = fields.Namespace("http://schema.org/")


class Software:
    def __init__(self, repo_uri: str):
        self._id = repo_uri
        self.license_url = "http://example.com/books/1"  # LicenseMetadata(self.path).get_licenses() TODO rm
        self.language = (
            "python"  # FilesMetadata(self.path).get_programming_lang() TODO rm
        )


class SoftwareSchema(JsonLDSchema):
    _id = fields.Id()
    license_url = fields.String(schema.license)
    language = fields.String(schema.progLang)

    class Meta:
        rdf_type = schema.SoftwareApplication
        model = Software


def to_graph(repository_location, output_format="ttl"):
    software_instance = Software(repository_location)
    jsonld_dict = SoftwareSchema().dump(software_instance)
    g = Graph()
    g.parse(format="json-ld", data=jsonld_dict)

    # prefix assignment, still have to code the automation of this
    g.bind("schema", schema)
    print(g.serialize(format=output_format))


# TODO add function and class descriptions, write tests, see how license_to graph and fair uri functions fit into this


def generate_fair_uri(repository_name):
    # Compute the SHA-256 hash of the repository name
    hash = hashlib.sha256(repository_name.encode()).hexdigest()

    # Return the FAIR URI in the form "fair:sha256-HASH, truncated to 5 characters to promote readability"
    fair_uri = f"fair:{repository_name}_" + hash[:5]
    return fair_uri


def license_to_graph(location: str, license: list):
    g = Graph()
    if "http://" or "https://" in location:
        fair_uri = location
    else:
        fair_uri = generate_fair_uri(location)
    for element in license:
        g.add(
            (
                URIRef(fair_uri),
                URIRef("https://schema.org/license"),
                URIRef(str(element)),
            )
        )
