from rdflib import Graph, URIRef, parser
import hashlib
from calamus import fields
from calamus.schema import JsonLDSchema
from urllib.parse import urlparse

schema = fields.Namespace("http://schema.org/")


def validate_url(url: str):
    """Checks if input is a valid URL.
    credits: https://stackoverflow.com/a/38020041

    Examples
    -------------
    >>> validate_url('/data/my_repo')
    False
    >>> validate_url(532)
    False
    >>> validate_url('https://www.github.com/SDSC-ORD/gimie')
    True
    >>> validate_url('github.com/SDSC-ORD/gimie')
    False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def generate_fair_uri(repository_path: str):
    """given a repository_path, returns a URI with a hash for uniqueness, or the repository URL if it's online
    Example input:  -> https://www.github.com/SDSC-ORD/gimie (online)
                    -> my repository (local)"""
    # Compute the SHA-256 hash of the repository name
    hash = hashlib.sha256(repository_path.encode()).hexdigest()
    if validate_url(repository_path):
        fair_uri = repository_path
    else:
        # Return the FAIR URI in the form "sha256-HASH, truncated to 5 characters to promote readability"
        fair_uri = (
            f"gimie:{repository_path}/" + hash[:5]
        )  # TODO decide on URI+prefix we want to use for non online repos
    return fair_uri


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
