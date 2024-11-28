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
from functools import reduce
from typing import Iterable, Set
from rdflib import Graph, URIRef
from gimie.graph import Property


class Parser(ABC):
    """
    Parser is an Abstract Base Class. It is only meant
    to define a standard interface for all parsers.

    All subclasses must implement parse(). A parser parses
    bytes data into a set of predicate-object tuples.

    Parameters
    ----------
    subject:
        The subject of a triple (subject - predicate - object) to be used for writing parsed properties to.
    """

    def __init__(self, subject: str):
        self.subject = URIRef(subject)

    @abstractmethod
    def parse(self, data: bytes) -> Graph:
        """Extract rdf graph from a source."""
        ...

    def parse_all(self, docs: Iterable[bytes]) -> Graph:
        """Parse multiple sources and return the union of
        triples."""

        properties = map(self.parse, docs)
        return reduce(lambda p1, p2: p1 | p2, properties)
