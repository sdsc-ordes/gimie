from abc import ABC, abstractmethod
from typing import Optional


from rdflib import Graph


class Extractor(ABC):
    """Extractor is an Abstract Base Class. It is only meant
    to define a standard interface for all extractors.

    All subclasses must implement extract() and to_graph() methods
    they are free to override the default serialize() and jsonld()
    """

    def __init__(self, path: str, _id: Optional[str] = None):
        self.path = path

    @abstractmethod
    def extract(self):
        """Extract metadata"""
        ...

    @abstractmethod
    def to_graph(self) -> Graph:
        """Generate an RDF graph from the instance"""
        return Graph()

    def serialize(self, format: str = "ttl") -> str:
        """Serialize the RDF graph representing the instance."""
        return self.to_graph().serialize(format=format)  # type: ignore

    def jsonld(self) -> str:
        """Alias for jsonld serialization."""
        return self.serialize(format="json-ld")
