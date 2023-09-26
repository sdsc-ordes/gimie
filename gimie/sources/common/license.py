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
    pattern = r".*(license(s)?|reus(e|ing)|copy(ing)?)(\.(txt|md|rst))?$"
    if re.match(pattern, file.name, flags=re.IGNORECASE):
        return True
    return False
