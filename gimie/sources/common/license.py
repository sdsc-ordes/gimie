from tempfile import NamedTemporaryFile
import re
from scancode.api import get_licenses
import requests
import json
import os


def get_license_path(
    repo_url: str, default_branch_name: str, files_dict: dict
) -> str:
    """Given a list of files, returns the URL filepath which contains the license"""
    repo_url = repo_url.rstrip("/")
    license_files = []
    if files_dict:
        for file in files_dict:
            if file["name"].startswith("."):
                continue
            pattern = (
                r".*(license(s)?|reus(e|ing)|copy(ing)?)(\.(txt|md|rst))?$"
            )
            if re.match(pattern, file["name"], flags=re.IGNORECASE):
                license_path = (
                    repo_url + f"/blob/{default_branch_name}/" + file["name"]
                )
                license_files.append(license_path)

    if len(license_files) > 1:
        return "More than 1 license file was found, please make sure you only have one license."
    else:
        for license_file_url in license_files:
            return license_file_url


def extract_license_id(url: str, headers: dict) -> str:
    """Runs the SPDX license matcher (Scancode-toolkit) against the license_string and return a SPDX License ID"""
    file1 = NamedTemporaryFile(delete=False)

    with open(file1.name, "w", encoding="utf-8") as license_handler:
        data = requests.get(url, headers=headers).json()
        json.dump(data, license_handler)

    found_spdx_license_id = get_licenses(file1.name)[
        "detected_license_expression_spdx"
    ]
    file1.close()
    os.remove(file1.name)
    return found_spdx_license_id
