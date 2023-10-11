import re
from spdx_license_list import LICENSES
from scancode.api import get_licenses
from typing import NamedTuple
from gimie.io import Resource, iterable_to_stream, RemoteResource


def _get_licenses(temp_file_path: str) -> str:
    """Takes a file with a license text in it, and matches this using the scancode API to a license to get some possible
    license matches. The highest match is then returned as a spdx license ID"""
    license_detections = get_licenses(temp_file_path, include_text=True)[
        "license_detections"
    ]
    license_id = get_license_with_highest_coverage(license_detections)
    spdx_license_id = get_spdx_license_id(LICENSES, license_id)

    return spdx_license_id


def get_spdx_license_id(license_dict: dict, license_id: str) -> str:
    """Given a scamcode API license ID also known as a license detection, returns the correctly capitalized
    spdx id corresponding to it"""
    for key, value in license_dict.items():
        if key.lower() == license_id.lower():
            return value.id


def is_license_path(filename: str) -> bool:
    """Given an input filename, returns a boolean indicating whether the filename path looks like a license."""
    if filename.startswith("."):
        return False
    pattern = r".*(license(s)?.*|lizenz|reus(e|ing).*|copy(ing)?.*)(\.(txt|md|rst))?$"
    if re.match(pattern, filename, flags=re.IGNORECASE):
        return True
    return False


def get_license_with_highest_coverage(license_detections: list[dict]) -> str:
    """Filters a list of "license detections" (the output of scancode.api.get_licenses)
    to return the one with the highest match percentage.
    This is used to select among multiple license matches from a single file."""
    highest_coverage = 0.0
    highest_license = None

    for detection in license_detections:

        matches = detection["matches"] if "matches" in detection else []
        for match in matches:
            match_coverage = match["score"] if "score" in match else 0
            if match_coverage > highest_coverage:
                highest_coverage = match_coverage
                highest_license = (
                    match["license_expression"]
                    if "license_expression" in match
                    else None
                )
    return highest_license
