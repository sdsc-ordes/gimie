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
import yaml

from rdflib.term import URIRef

from gimie import logger
from gimie.graph.namespaces import SDO
from gimie.parsers.abstract import Parser, Property


class CffParser(Parser):
    """Parse DOI from CITATION.cff into schema:citation <doi>."""

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


def doi_to_url(doi: str) -> str:
    """Formats a doi to an https URL to doi.org.

    Parameters
    ----------
    doi
        doi where the scheme (e.g. https://) and
        hostname (e.g. doi.org) may be missing.

    Returns
    -------
    str
        doi formatted as a valid url. Base url
        is set to https://doi.org when missing.

    Examples
    --------
    >>> doi_to_url("10.xxxx/example.abcd")
    'https://doi.org/10.xxxx/example.abcd'
    >>> doi_to_url("doi.org/10.xxxx/example.abcd")
    'https://doi.org/10.xxxx/example.abcd'
    >>> doi_to_url("https://doi.org/10.xxxx/example.abcd")
    'https://doi.org/10.xxxx/example.abcd'
    """
    prefix = ""

    if not doi.startswith("http"):
        prefix += "https://"

    if not "doi.org/" in doi:
        prefix += "doi.org/"

    return prefix + doi


def get_cff_doi(data: bytes) -> Optional[str]:
    """Given a CFF file, returns the DOI, if any.

    Parameters
    ----------
    data
        The cff file body as bytes.

    Returns
    -------
    str, optional
        doi formatted as a valid url

    Examples
    --------
    >>> get_cff_doi(bytes("doi:   10.5281/zenodo.1234", encoding="utf8"))
    'https://doi.org/10.5281/zenodo.1234'
    >>> get_cff_doi(bytes("abc: def", encoding="utf8"))

    """

    try:
        cff = yaml.safe_load(data.decode())
    except yaml.scanner.ScannerError:
        logger.warn("cannot read CITATION.cff, skipped.")
        return None

    try:
        doi = cff["doi"]
    except (KeyError, TypeError):
        return None

    return doi_to_url(doi)
