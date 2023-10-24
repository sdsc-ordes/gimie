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
from abc import ABC, abstractmethod
from typing import Iterable, Optional

from rdflib import Graph
from rdflib.term import URIRef

from gimie.graph.operations import combine_graphs
from gimie.io import Resource


class Parser(ABC):
    """Parser is an Abstract Base Class. It is only meant
    to define a standard interface for all parsers.

    All subclasses must implement _parse() and can_parse().
    A parser receives a subject URI and a resource, and returns
    a graph of triples using the input URI as subject.
    """

    def __init__(self, uri: URIRef, max_size_kb: Optional[int] = 2048):
        self.max_size_kb = max_size_kb
        self.uri = uri

    @abstractmethod
    def _parse(self, resource: Resource) -> Graph:
        """Extract triples"""
        ...

    @abstractmethod
    def can_parse(self, resource: Resource) -> bool:
        """Match based on filename (possibly also content and size)"""
        ...

    def parse(self, resource: Resource) -> Graph:
        """Parse if parsable, otherwise return an empty graph."""
        if self.can_parse(resource):
            return self._parse(resource)
        return Graph()

    def parse_multiple(self, resources: Iterable[Resource]) -> Graph:
        """Parse multiple resources and return the union of the graphs.
        Unparsable resources are ignored."""
        g = Graph()
        graphs = map(self.parse, resources)
        return combine_graphs(*graphs)
