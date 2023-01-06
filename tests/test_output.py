# Gimie
# Copyright 2022 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test the gimie output"""
from pathlib import Path
from pyshacl import validate
import pytest
from rdflib import Graph


out_graph_path = Path(
    "output.jsonld"
)  # will become run_gimie() when functional
validation_graph_path = Path("shaclgraph.ttl")


@pytest.mark.skip("not yet implemented")
def test_validate_output_is_linked_data():
    """Is output valid RDF?"""
    g = Graph()
    with open(out_graph_path) as output_graph:
        g.parse(output_graph, format="json-ld")


@pytest.mark.skip("not yet implemented")
def test_output_conforms_shapes():
    """Does graph conform SHACL shapes graph?"""
    g = Graph()
    shapes = Graph()
    with open(validation_graph_path) as validation_graph, open(
        out_graph_path
    ) as output_graph:
        g.parse(output_graph, format="json-ld")
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
