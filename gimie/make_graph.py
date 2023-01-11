from rdflib import Graph, URIRef, parser
import hashlib
from calamus import fields
from calamus.schema import JsonLDSchema

schema = fields.Namespace("http://schema.org/")


def generate_fair_uri(
    repository_path: str = "https://example.com/Repository/",
):
    """given a repository_path, returns a URI with a hash for uniqueness, or the repository URL if it's online"""
    # Compute the SHA-256 hash of the repository name
    hash = hashlib.sha256(repository_path.encode()).hexdigest()
    # TODO https://www.github.com/repoX should return the same result as github.com/repoX
    if (
        False
    ):  # repository_path.is_online(): #we need a method that checks whether the repopath is online or a foldername
        fair_uri = repository_path
    else:
        # Return the FAIR URI in the form "fair:sha256-HASH, truncated to 5 characters to promote readability"
        fair_uri = (
            f"gimie:{repository_path}/" + hash[:5]
        )  # TODO decide on URI we want to use for non online repos
    return fair_uri


class Repository:
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
        self.license_url = "http://example.com/books/1"  # LicenseMetadata(self.path).get_licenses() TODO replace
        self.programming_language = "python"  # FilesMetadata(self.path).get_programming_lang() TODO replace


class RepositorySchema(JsonLDSchema):
    """A Class which indicates how the attributes of Repository map to schema.org properties conform Calamus"""

    _id = fields.Id()
    license_url = fields.String(schema.license)
    programming_language = fields.String(schema.programmingLanguage)

    class Meta:
        """a metaclass which indicates how the repository should be rdf:typed conform Calamus"""

        rdf_type = schema.SoftwareApplication
        model = Repository


def to_graph(path: str, output_format: str = "ttl"):
    """A function which turns a given path into a graph in a desired rdfLib supported rdf serialization"""
    software_instance = Repository(path)
    jsonld_dict = RepositorySchema().dump(software_instance)
    g = Graph()
    g.parse(format="json-ld", data=jsonld_dict)

    g.bind(
        "schema", schema
    )  # TODO prefix assignment, still have to figure out code for automation of this
    print(g.serialize(format=output_format))


# to_graph("https://wwww.gimie.com") #Test functionality
