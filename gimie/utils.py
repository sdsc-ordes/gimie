from urllib.parse import urlparse
from typing import List
import os
import re


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
    except:
        return False


def generate_fair_uri(path: str):

    # We only need to craft a URI for a local path.
    if validate_url(path):
        fair_uri = path
    else:
        hashed = hashlib.md5(path.encode()).hexdigest()
        name = os.path.basename(path)
        fair_uri = f"gimie:{name}/{hashed[:5]}"
    return fair_uri


def locate_licenses(path) -> List[str]:
    """Returns valid potential paths to license files in the project.
    This uses pattern-matching on file names.

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
