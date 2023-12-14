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
from pyshacl import validate
import pytest
from rdflib import Graph

from gimie.project import Project


OUT_TTL = (
    Project("https://github.com/sdsc-ordes/gimie", git_provider="github")
    .extract()
    .serialize(format="ttl")
)


def test_validate_output_is_linked_data():
    """Is output valid RDF?"""
    g = Graph().parse(format="ttl", data=OUT_TTL)
    assert g is not None


@pytest.mark.skip("not yet implemented")
def test_output_conforms_shapes():
    """Does graph conform SHACL shapes graph?"""
    with open("shaclgraph.ttl") as shapes:
        shapes_graph = Graph().parse(shapes.read())
    valid_graph, _, _ = validate(
        data_graph=Graph().parse(data=OUT_TTL),
        shacl_graph=shapes_graph,
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
