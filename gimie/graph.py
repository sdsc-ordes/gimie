from functools import reduce

from calamus import fields
from calamus.schema import JsonLDSchema
from rdflib import Graph

from gimie.utils import generate_fair_uri

schema = fields.Namespace("http://schema.org/")


def combine_graphs(*graphs: Graph) -> Graph:
    """Combines an arbitrary number of input graphs
    into a single graph."""
    return reduce(lambda g1, g2: g1 | g2, graphs)
