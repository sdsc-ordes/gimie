#!/usr/bin/env python3
"""Validate RDF data against gimie's SHACL shapes."""

import argparse
import sys
from pathlib import Path

import pyshacl
from rdflib import Graph

DEFAULT_SHAPES = (
    Path(__file__).resolve().parent.parent / "gimie/shacl/gimie_shacl.ttl"
)


def validate(data_path: Path, shapes_path: Path) -> tuple[bool, str]:
    data_graph = Graph().parse(data_path)
    shapes_graph = Graph().parse(shapes_path)
    conforms, results_graph, _ = pyshacl.validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
    )
    return conforms, results_graph.serialize(format="turtle")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, help="RDF data file to validate")
    parser.add_argument(
        "--shapes",
        "-s",
        type=Path,
        default=DEFAULT_SHAPES,
        help=f"SHACL shapes file (default: {DEFAULT_SHAPES})",
    )
    args = parser.parse_args()

    conforms, report = validate(args.data, args.shapes)
    print("PASSED" if conforms else "FAILED")
    print(report)
    sys.exit(0 if conforms else 1)


if __name__ == "__main__":
    main()
