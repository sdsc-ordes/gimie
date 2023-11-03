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
from typing import Iterable, Set, Tuple, TypeAlias, Union

from rdflib.term import Literal, URIRef

Property: TypeAlias = Tuple[URIRef, Union[URIRef, Literal]]


class Parser(ABC):
    """Parser is an Abstract Base Class. It is only meant
    to define a standard interface for all parsers.

    All subclasses must implement parse(). A parser parses
    bytes data into a set of property-object tuples.
    """

    def __init__(self):
        pass

    @abstractmethod
    def parse(self, data: bytes) -> Set[Property]:
        """Extract property-object tuples from a source."""
        ...

    def parse_all(self, docs: Iterable[bytes]) -> Set[Property]:
        """Parse multiple sources and return the union of
        property-object tuples."""
        properties = map(self.parse, docs)
        return reduce(lambda p1, p2: p1 | p2, properties)
