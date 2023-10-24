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
import os
import re
import tempfile
from typing import Iterable, List, Optional

from rdflib import Graph
from rdflib.term import URIRef
from scancode.api import get_licenses
from spdx_license_list import LICENSES

from gimie.graph.namespaces import SDO
from gimie.io import Resource
from gimie.parsers.abstract import Parser

SPDX_IDS = list(LICENSES.keys())


class LicenseParser(Parser):
    """Parse LICENSE file(s) into schema:license."""

    def __init__(self, uri: URIRef, max_size_kb: Optional[int] = 2048):
        super().__init__(uri, max_size_kb)

    def _parse(self, resource: Resource) -> Graph:
        """Extracts an spdx URL from a license file and returns a
        triple of the form <input uri> <schema:license> <spdx_url>.
        If no matching URL is found, an empty graph is returned.
        """
        g = Graph()
        license_url = get_license_url(resource)
        if license_url:
            g.add((self.uri, SDO.license, URIRef(license_url)))
        return g

    def can_parse(self, resource: Resource) -> bool:
        """Match based on filename  (and size?)"""
        return is_license_path(
            resource.name
        )  # & (resource.size < self.max_size_kb)


def get_license_url(license_file: Resource) -> Optional[str]:
    """Takes a file-like resource containing a license text, and matches its content
    using the scancode API to get possible license matches. The best match is
    then returned as a spdx license URL.

    Examples
    --------
    >>> from gimie.io import LocalResource
    >>> get_license_url(LocalResource('LICENSE'))
    'https://spdx.org/licenses/Apache-2.0.html'
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(license_file.open().read())
    temp_file.close()

    license_detections = get_licenses(temp_file.name, include_text=True)[
        "license_detections"
    ]
    license_id = get_license_with_highest_coverage(license_detections)  # type: ignore
    if license_id is None:
        return None
    spdx_license_id = get_spdx_license_id(license_id)
    os.remove(temp_file.name)
    if spdx_license_id:
        return f"https://spdx.org/licenses/{str(spdx_license_id)}.html"

    return None


def get_spdx_license_id(
    license_id: str,
    spdx_ids: Iterable[str] = SPDX_IDS,
) -> Optional[str]:
    """Given a scancode API license ID also known as a license detection, returns the correctly capitalized
    spdx id corresponding to it.

    Parameters
    ----------
    license_id:
        A license id to match with SPDX licenses.
    spdx_ids:
        An iterable of (reference) SPDX license ids.

    Examples
    --------
    >>> get_spdx_license_id('apache-2.0')
    'Apache-2.0'
    >>> get_spdx_license_id('gpl-3.0')
    'GPL-3.0'
    """

    lower_spdx_ids = {spdx.lower(): spdx for spdx in spdx_ids}

    return lower_spdx_ids.get(license_id.lower(), None)


def is_license_path(filename: str) -> bool:
    """Given an input filename, returns a boolean indicating whether the filename path looks like a license.

    Parameters
    ----------
    filename:
        A filename to check.

    Examples
    --------
    >>> is_license_path('LICENSE.txt')
    True
    >>> is_license_path('LICENSE-APACHE')
    True
    >>> is_license_path('README.md')
    False
    """
    if filename.startswith("."):
        return False
    pattern = r".*(license(s)?.*|lizenz|reus(e|ing).*|copy(ing)?.*)(\.(txt|md|rst))?$"
    if re.match(pattern, filename, flags=re.IGNORECASE):
        return True
    return False


def get_license_with_highest_coverage(
    license_detections: List[dict],
) -> Optional[str]:
    """Filters a list of "license detections" (the output of scancode.api.get_licenses)
    to return the one with the highest match percentage.
    This is used to select among multiple license matches from a single file.

    Parameters
    ----------
    license_detections:
        A list of license detections, as returned by scancode.api.get_licenses.

    Examples
    --------
    >>> from scancode.api import get_licenses
    >>> license_detections = get_licenses('LICENSE')['license_detections']
    >>> get_license_with_highest_coverage(license_detections)
    'apache-2.0'
    """
    highest_coverage = 0.0
    highest_license = None

    for detection in license_detections:

        matches = detection["matches"] if "matches" in detection else []
        for match in matches:
            match_coverage = match.get("score", 0)
            if match_coverage > highest_coverage:
                highest_coverage = match_coverage
                highest_license = match.get("license_expression", None)
    return highest_license
