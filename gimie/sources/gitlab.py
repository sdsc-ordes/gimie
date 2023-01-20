from rdflib import Graph
from gimie.sources.abstract import Extractor


class GitlabExtractor(Extractor):
    def __init__(self, path: str):
        raise NotImplementedError

    def extractor(self):
        raise NotImplementedError

    def to_graph(self) -> Graph:
        """Generate an RDF graph from the instance"""
        raise NotImplementedError
