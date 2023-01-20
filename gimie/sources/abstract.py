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
"""Abstract classes for gimie objects."""
from abc import ABC, abstractmethod
from typing import Optional


from rdflib import Graph


class Extractor(ABC):
    """Extractor is an Abstract Base Class. It is only meant
    to define a standard interface for all extractors.

    All subclasses must implement extract() and to_graph() methods
    they are free to override the default serialize() and jsonld()
    """

    def __init__(self, path: str, _id: Optional[str] = None):
        self.path = path

    @abstractmethod
    def extract(self):
        """Extract metadata"""
        ...

    @abstractmethod
    def to_graph(self) -> Graph:
        """Generate an RDF graph from the instance"""
        return Graph()

    def serialize(self, format: str = "ttl") -> str:
        """Serialize the RDF graph representing the instance."""
        return self.to_graph().serialize(format=format)  # type: ignore

    def jsonld(self) -> str:
        """Alias for jsonld serialization."""
        return self.serialize(format="json-ld")
