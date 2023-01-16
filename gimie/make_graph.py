from rdflib import Graph, URIRef, parser
import hashlib
from gimie.utils import validate_url
from calamus import fields
from calamus.schema import JsonLDSchema

schema = fields.Namespace("http://schema.org/")


class ProjectGraph:
    """A class to represent a GIT repository

    Parameters
    ----------
    path: str
        The path to the git repository.

    Attributes
    ----------
    license_url (conform SPDX)
    programming_language
    """

    def __init__(self, path: str):
        self._id = generate_fair_uri(path)
        self.license_url = "http://example.com/license/1"  # LicenseMetadata(self.path).get_licenses() TODO replace
        self.programming_language = "python"  # FilesMetadata(self.path).get_programming_lang() TODO replace

    def to_graph(self, format: str = "ttl") -> str:
        """A function which turns a given path into a graph in a desired rdfLib supported rdf serialization"""
        jsonld_dict = RepositorySchema().dump(self)
        g = Graph()
        g.parse(format="json-ld", data=jsonld_dict)

        g.bind(
            "schema", schema
        )  # TODO prefix assignment, still have to figure out code for automation of this
        # print(g.serialize(format=format))
        return g.serialize(format=format)


class RepositorySchema(JsonLDSchema):
    """A Class which indicates how the attributes of Repository map to schema.org properties conform Calamus"""

    _id = fields.Id()
    license_url = fields.String(schema.license)
    programming_language = fields.String(schema.programmingLanguage)

    class Meta:
        """a metaclass which indicates how the repository should be rdf:typed conform Calamus"""

        rdf_type = schema.SoftwareApplication
        model = ProjectGraph
