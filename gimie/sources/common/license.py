import os
import re
from typing import List

import spdx_matcher
import subprocess

from gimie.graph.namespaces import GIMIE
import spdx_matcher as lookup

import base64
import os
import re
from typing import List
from scancode.api import get_licenses
from gimie.graph.namespaces import GIMIE
import requests
import json

repo_url = "https://github.com/comfyanonymous/ComfyUI"
github_token = os.environ.get("GITHUB_TOKEN")
headers = {"Authorization": f"token {github_token}"}
repo_url = repo_url.rstrip("/")


def get_default_branch_name(repo_url):
    # Construct the URL for the GitHub repository
    url = repo_url.replace(
        "https://github.com", "https://api.github.com/repos"
    )
    # Send a GET request to the GitHub API to get repository information
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        repository_info = response.json()
        # Check if "master" exists as a branch name
        if "master" == repository_info["default_branch"]:
            return "master"

        # Check if "main" exists as a branch name
        if "main" == repository_info["default_branch"]:
            return "main"

        # If neither "master" nor "main" exists, return None
        return None
    else:
        print(
            f"Failed to retrieve repository information. Status code: {response.status_code}"
        )
        return None


def get_files_in_repository_root(repo_url, headers):
    """Given a GitHub repository URL, outputs a list of files present in the root folder"""
    # Extract the username and repository name from the URL
    parts = repo_url.strip("/").split("/")
    username = parts[-2]
    repo_name = parts[-1]

    # Construct the GitHub API URL for the repository's contents
    api_url = f"https://api.github.com/repos/{username}/{repo_name}/git/trees/{get_default_branch_name(repo_url)}"

    try:
        # Make a GET request to the GitHub API
        response = requests.get(api_url, headers=headers)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            contents = response.json()
            files_dict = [
                {"path": item["path"], "url": item["url"]}
                for item in contents["tree"]
            ]
            return files_dict
        else:
            # If the request was not successful, raise an exception
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def get_license_path(files_dict, license_files):
    """Given a list of files, returns the URL filepath which contains the license"""
    if files_dict:
        for file in files_dict:
            if file["path"].startswith("."):
                continue
            pattern = (
                r".*(license(s)?|reus(e|ing)|copy(ing)?)(\.(txt|md|rst))?$"
            )
            if re.match(pattern, file["path"], flags=re.IGNORECASE):
                print(file["url"], file["path"])
                license_path = (
                    repo_url
                    + f"/blob/{get_default_branch_name(repo_url)}/"
                    + file["path"]
                )
                license_files.append(license_path)
                print(
                    license_path
                    + " is the license path gimie found, starting extraction of license..."
                )

    if len(license_files) > 1:
        return "More than 1 license file was found, please make sure you only have one license."
    else:
        for license_file in license_files:
            return license_file


def github_read_file(url, github_token=None):
    """Uses the Github API to download the license file using its URL"""
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    return data


def extract_license_string(url):
    """Runs the spdx license matcher (Scancode-toolkit) against the license_string"""

    file1 = open("myfile.json", "w", encoding="utf-8")
    json.dump(github_read_file(url), file1)
    file1.close()
    found_spdx_license_id = get_licenses("myfile.json")[
        "detected_license_expression_spdx"
    ]
    os.remove("myfile.json")
    return found_spdx_license_id


def get_spdx_url(name: str) -> str:
    """Given an SPDX license identifier, return the full URL."""
    return f"https://spdx.org/licenses/{name}.html"


def get_license(repo_url, headers, license_files=[]):
    get_default_branch_name(repo_url)
    url = get_license_path(
        get_files_in_repository_root(repo_url, headers),
        license_files=license_files,
    )
    github_read_file(url)
    print(get_spdx_url(extract_license_string(url)))


get_license(repo_url, headers=headers)
