import os
import re
from spdx_license_list import LICENSES
from scancode.api import get_licenses
from typing import Iterable, List, Optional
from gimie.io import Resource
import tempfile

SPDX_IDS = list(LICENSES.keys())


def get_license_url(license_file: Resource) -> Optional[str]:
    """Takes the path of a text file containing a license text, and matches this
    using the scancode API to get possible license matches. The best match is
    then returned as a spdx license URL"""
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
    """

    lower_spdx_ids = {spdx.lower(): spdx for spdx in spdx_ids}

    return lower_spdx_ids.get(license_id.lower(), None)


def is_license_path(filename: str) -> bool:
    """Given an input filename, returns a boolean indicating whether the filename path looks like a license."""
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
    This is used to select among multiple license matches from a single file."""
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
