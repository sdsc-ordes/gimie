from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from gimie.source.local import GitExtractor
from gimie.source.remote import (
    GithubExtractor,
    GitlabExtractor,
)
from rdflib import Graph

REMOTE_SOURCES: Dict[str, Any] = {
    "gitlab": GitlabExtractor,
    "github": GithubExtractor,
}
LOCAL_SOURCES: Dict[str, Any] = {
    "git": GitExtractor,
}

SOURCES: Dict[str, Any] = LOCAL_SOURCES | REMOTE_SOURCES


def get_local_extractor(path: str, source: str) -> Extractor:
    return LOCAL_SOURCES[source](path=path)


def get_remote_extractor(path: str, source: str) -> Extractor:
    return REMOTE_SOURCES[source](path=path)


def is_local_source(source: str) -> bool:
    return source in LOCAL_SOURCES


def is_remote_source(source: str) -> bool:
    return source in REMOTE_SOURCES


def is_valid_source(source: str) -> bool:
    return source in SOURCES


class Extractor(ABC):
    """Extractor is an Abstract Base Class. It is only meant
    to define a standard interface for all extractors.

    All subclasses must implement extract() and to_graph() methods
    they are free to override the default serialize() and jsonld()
    """

    def __init__(self, path: str):
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
