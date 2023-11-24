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
    >>> validate_url('https://www.github.com/SDSC-ORD/gimie')
    True
    >>> validate_url('github.com/SDSC-ORD/gimie')
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
    'https://sdsc-ord.github.io/gimie/abc'
    """
    return str(GIMIE[ref])
