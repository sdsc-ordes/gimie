import os
import re
from typing import List

from gimie.graph.namespaces import GIMIE


def locate_licenses(path: str, recurse: bool = False) -> List[str]:
    """Returns valid potential paths to license files in the project.
    This uses pattern-matching on file names.

    Parameters
    ----------
    path:
        The root path to search for license files.
    recurse:
        Whether to look into subdirectories.

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

        # The first root of os.walk is the current dir
        if not recurse:
            return license_files

    return license_files


def get_spdx_url(name: str) -> str:
    """Given an SPDX license identifier, return the full URL."""
    return f"https://spdx.org/licenses/{name}"
