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
"""Abstract for graph converters."""

from abc import ABC, abstractmethod
from typing import Any

from rdflib import Graph


class Converter(ABC):
    """Converter is an Abstract Base Class. It is only meant
    to define a standard interface for all graph converters.

    All subclasses must implement convert(). A converter transforms
    an RDF graph into a specialized serialization format.

    Parameters
    ----------
    g:
        The RDF graph to convert.
    """

    def __init__(self, g: Graph):
        self.g = g

    @abstractmethod
    def convert(self) -> Any:
        """Convert the RDF graph to the target format."""
        ...
