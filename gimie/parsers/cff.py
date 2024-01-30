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
from io import BytesIO
import re
from typing import List, Optional, Set

from rdflib.term import URIRef

from gimie.graph.namespaces import SDO
from gimie.parsers.abstract import Parser, Property


class CffParser(Parser):
    """Parse cff file to extract the doi into schema:citation <doi>."""

    def __init__(self):
        super().__init__()

    def parse(self, data: bytes) -> Set[Property]:
        """Extracts a DOI link from a CFF file and returns a
        set with a single tuple <schema:citation> <doi>.
        If no DOI is found, an empty set is returned.
        """
        props = set()
        doi = get_cff_doi(data)

        if doi:
            props.add((SDO.citation, URIRef(doi)))
        return props


def get_cff_doi(data: bytes) -> Optional[str]:
    """Given a CFF file, returns the DOI, if any.

    Parameters
    ----------
    data:
        The cff file body as bytes.

    """

    matches = re.search(r"^doi: *(.*)$", str(data), flags=re.MULTILINE)
    doi = matches.groups()[0]

    return doi
