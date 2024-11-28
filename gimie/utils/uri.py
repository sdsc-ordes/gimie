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
"""Utility functions used throughout gimie."""

from typing import List, Literal
from urllib.parse import urlparse
import re

from gimie.graph.namespaces import GIMIE


def validate_url(url: str):
    """Checks if input is a valid URL.
    credits: https://stackoverflow.com/a/38020041

    Examples
    -------------
    >>> validate_url('/data/my_repo')
    False
    >>> validate_url(532)
    False
    >>> validate_url('https://www.github.com/sdsc-ordes/gimie')
    True
    >>> validate_url('github.com/sdsc-ordes/gimie')
    False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False


def generate_uri(ref: str):
    """Given a reference (e.g. commit sha), return a URI.

    Parameters
    ----------
    path:
        Path to the repository, either local or a URL.


    Returns
    -------
    fair_uri:
        A unique resource identifier (URI) for the repository path.

    Examples
    --------
    >>> generate_uri("abc")
    'https://sdsc-ordes.github.io/gimie/abc'
    """
    return str(GIMIE[ref])


def is_valid_orcid(orcid):
    """Check if the input is a valid ORCID according to definition from orcid.org [1]_.
    .. [1] [https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier)

    Parameters
    ----------
    orcid:
        The ORCID to validate.

    Returns
    -------
    bool:
        True if the ORCID is valid, False otherwise.

    Examples
    --------
    >>> is_valid_orcid("https://orcid.org/0000-0001-2345-6789")
    True
    >>> is_valid_orcid("0000-0001-2345-6789")
    False
    >>> is_valid_orcid("http://orcid.org/0000-0001-2345-6789")
    False

    """
    return bool(
        re.match(
            r"(https:\/\/)?orcid.org\/\d{4}-\d{4}-\d{4}-\d{4}", str(orcid)
        )
    )


def extract_doi_match(doi):
    """Extracts doi from the input if it contains a valid DOI according to definition from crossref.org [1]_.
    .. [1] [https://www.crossref.org/blog/dois-and-matching-regular-expressions](https://www.crossref.org/blog/dois-and-matching-regular-expressions)

    Parameters
    ----------
    doi:
        The DOI to validate.

    Returns
    -------
    str:
        The extracted short DOI if it is valid, None otherwise.

    Examples
    --------
    >>> extract_doi_match("10.5281/zenodo.1234567")
    '10.5281/zenodo.1234567'
    >>> extract_doi_match("https://doi.org/10.5281/zenodo.1234567")
    '10.5281/zenodo.1234567'
    """
    match = re.search(
        r"10.\d{4,9}/[-._;()/:A-Z0-9]+$", doi, flags=re.IGNORECASE
    )
    if match:
        return match.group()
