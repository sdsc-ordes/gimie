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

from gimie.project import Project


OUT_GRAPH = Project("https://github.com/SDSC-ORD/gimie", sources=["github"]).serialize(
    format="ttl"
)
SHAPES_GRAPH = Graph().parse(Path("shaclgraph.ttl"))


def test_validate_output_is_linked_data():
    """Is output valid RDF?"""
    g = Graph().parse(OUT_GRAPH)


@pytest.mark.skip("not yet implemented")
def test_output_conforms_shapes():
    """Does graph conform SHACL shapes graph?"""
    valid_graph, _, _ = validate(
        data_graph=OUT_GRAPH,
        shacl_graph=SHAPES_GRAPH,
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
