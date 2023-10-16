import re
from spdx_license_list import LICENSES, License
from scancode.api import get_licenses
from typing import Iterable, List, Optional
from gimie.io import Resource, iterable_to_stream, RemoteResource


def _get_license_url(temp_file_path: str) -> str:
    """Takes the path of a text file containing a license text, and matches this
    using the scancode API to get possible license matches. The best match is
    then returned as a spdx license URL"""
    license_detections = get_licenses(temp_file_path, include_text=True)[
        "license_detections"
    ]
    license_id = get_license_with_highest_coverage(license_detections)  # type: ignore
    spdx_license_id = get_spdx_license_id(LICENSES.keys(), license_id)
    spdx_license_url = f"https://spdx.org/licenses/{str(spdx_license_id)}.html"

    return spdx_license_url


def get_spdx_license_id(
    ref_licenses: Iterable[str], license_id: Optional[str]
) -> Optional[str]:
    """Given a scancode API license ID also known as a license detection, returns the correctly capitalized
    spdx id corresponding to it.

    Parameters
    ----------
    ref_licenses: Iterable[str]
        An iterable of (reference) SPDX license ids.
    license_id: Optional[str]
        A license id to match with SPDX licenses.
    """

    lower_ref_licenses = {ref.lower(): ref for ref in ref_licenses}

    if license_id in lower_ref_licenses:
        return lower_ref_licenses[license_id]

    return None


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
