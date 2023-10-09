from tempfile import NamedTemporaryFile
import re
from scancode.api import get_licenses
import requests
import json
import os
from gimie.io import Resource, iterable_to_stream, RemoteResource
from io import BufferedReader
from typing import List


def is_license_path(file: Resource) -> bool:
    """Given a list of files, returns the URL filepath which contains the license"""
    if file.name.startswith("."):
        return False
    pattern = r".*(license(s)?.*|lizenz|reus(e|ing).*|copy(ing)?.*)(\.(txt|md|rst))?$"
    if re.match(pattern, file.name, flags=re.IGNORECASE):
        return True
    return False


def get_license_with_highest_coverage(license_detections) -> str:
    """takes a license_detection object (the output of get_licenses) and
    returns the one with the highest match percentage, in case a file
    contains two license texts"""
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
