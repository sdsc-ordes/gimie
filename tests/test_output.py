"""Test the gimie output"""
from pathlib import Path
from pyshacl import validate
from rdflib import Graph


out_graph_path = Path("output.jsonld")  # will become run_gimie() when functional
validation_graph_path = Path("shaclgraph.ttl")


def test_validate_output_is_linked_data():
    """Is output valid RDF?"""
    g = Graph()
    with open(out_graph_path) as output_graph:
        g.parse(output_graph, format='json-ld')


def test_output_conforms_shapes():
    """Does graph conform SHACL shapes graph?"""
    g = Graph()
    shapes = Graph()
    with open(validation_graph_path) as validation_graph, open(
        out_graph_path
    ) as output_graph:
        g.parse(output_graph, format='json-ld')
        shapes.parse(validation_graph)
        valid_graph, validation_report, _ = validate(
            data_graph=g,
            shacl_graph=shapes,
            ont_graph=None,
            inference="rdfs",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            meta_shacl=False,
            advanced=False,
            js=False,
            debug=False,
        )
        assert valid_graph


