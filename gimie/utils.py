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
import os
import re
import hashlib
from typing import List
from urllib.parse import urlparse


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


def generate_fair_uri(path: str):
    """Given a repository path, returns a URI with a
    hash for uniqueness, or the repository URL if it's online.
    The URI format for local paths is "gimie:{basename}/{md5sum(abspath)}".

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
    >>> generate_fair_uri("https://www.github.com/SDSC-ORD/gimie")
    'https://www.github.com/SDSC-ORD/gimie'
    >>> generate_fair_uri("/data/org/project")
    'gimie:project/93db0'
    """

    # We only need to craft a URI for a local path.
    if validate_url(path):
        fair_uri = path
    else:
        hashed = hashlib.md5(path.encode()).hexdigest()
        name = os.path.basename(path)
        fair_uri = f"gimie:{name}/{hashed[:5]}"
    return fair_uri


def locate_licenses(path: str) -> List[str]:
    """Returns valid potential paths to license files in the project.
    This uses pattern-matching on file names.

    Parameters
    ----------
    path:
        The root path to search for license files.

    Returns
    -------
    license_files:
        The list of relative paths (from input path) to files which
        potentially contain license text.

    Examples
    --------
    >>> locate_licenses('.')
    ['./LICENSE']
    """
    license_files = []
    pattern = r".*(license(s)?|reus(e|ing)|copy(ing)?)(\.(txt|md|rst))?$"
    for root, _, files in os.walk(path):
        # skip toplevel hidden dirs (e.g. .git/)
        subdir = os.path.relpath(root, path)
        if subdir.startswith(".") and subdir != ".":
            continue
        for file in files:
            # skip hidden files
            if file.startswith("."):
                continue

            if re.match(pattern, file, flags=re.IGNORECASE):
                license_path = os.path.join(root, file)
                license_files.append(license_path)

    return license_files
