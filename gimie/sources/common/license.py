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

from gimie.graph.namespaces import GIMIE
import requests
import json

github_token = os.environ.get("GITHUB_TOKEN")
headers = {"Authorization": f"token {github_token}"}
repo_url = "https://github.com/SDSC-ORD/gimie"


def get_files_in_repository_root(repo_url):
    """Given a GitHub repository URL, outputs a list of files present in the root folder"""
    # Extract the username and repository name from the URL
    parts = repo_url.strip("/").split("/")
    username = parts[-2]
    repo_name = parts[-1]

    # Construct the GitHub API URL for the repository's contents
    api_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/"

    try:
        # Make a GET request to the GitHub API
        response = requests.get(api_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            contents = response.json()

            # Filter out only the files (exclude directories)
            files = [
                item["name"] for item in contents if item["type"] == "file"
            ]

            return files

        else:
            # If the request was not successful, raise an exception
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


files_in_root = get_files_in_repository_root(repo_url)
license_files = []


def return_license_path(files):
    """Given a list of files, returns the URL filepath which contains the license"""
    if files:
        for file in files:
            if file.startswith("."):
                continue
            pattern = (
                r".*(license(s)?|reus(e|ing)|copy(ing)?)(\.(txt|md|rst))?$"
            )
            if re.match(pattern, file, flags=re.IGNORECASE):
                license_path = repo_url + "/blob/main/" + file
                license_files.append(license_path)
                print(
                    license_path
                    + " is the license path gimie found, starting extraction of license..."
                )
    for license_file in license_files:
        return license_file


url = return_license_path(get_files_in_repository_root(repo_url))


def github_read_file(url, github_token=None):
    """Uses the Github API to download the license file using its URL"""
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    return data


file1 = open("myfile.json", "w", encoding="utf-8")
json_object1 = json.dump(github_read_file(url), file1)
file1.close()


def extract_license_string():
    """Runs the spdx license matcher (Scancode-toolkit) against the license_string"""
    with open(r"myfile.json", "r") as json_object:
        json_object = json.load(json_object)
        # print(json_object)
        license_string = str(json_object["payload"]["blob"]["rawLines"])
    subprocess.run(
        f"scancode --json-pp ./output.json  --license ./myfile.json "
    )
    os.remove("myfile.json")


extract_license_string()


def extract_spdx_url():
    """Parses the scancode-toolkit output to extract the full SPDX URL of found license"""
    with open("output.json", "r") as file2:
        json_object2 = json.load(file2)
        license_identifier = json_object2["files"][0]["licenses"][0][
            "spdx_url"
        ]
        print(license_identifier)
    os.remove("output.json")
    return license_identifier


extract_spdx_url()


def get_spdx_url(name: str) -> str:
    """Given an SPDX license identifier, return the full URL."""
    return f"https://spdx.org/licenses/{name}"
