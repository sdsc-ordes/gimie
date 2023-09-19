import os
import re
from typing import List

import subprocess
from tempfile import TemporaryFile
from gimie.graph.namespaces import GIMIE

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


def graph_ql_query_bit(repo_url):
    url = repo_url.replace(
        "https://github.com", "https://api.github.com/repos"
    )
    parts = repo_url.strip("/").split("/")
    username = parts[-2]
    repo_name = parts[-1]
    url = "https://api.github.com/graphql"
    query = """
       query {
         repository(owner: "%s", name: "%s") {
           defaultBranchRef {
             name
           }
           object(expression: "HEAD:") {
             ... on Tree {
               entries {
                 name
               }
             }
           }
         }
       }
       """ % (
        username,
        repo_name,
    )
    # Send a GET request to the GitHub API to get repository information
    response = requests.post(url, json={"query": query}, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        repository_info = response.json()
        default_branch_name = repository_info["data"]["repository"][
            "defaultBranchRef"
        ]["name"]
        files_dict = repository_info["data"]["repository"]["object"]["entries"]
        try:
            return default_branch_name, files_dict
        except KeyError:
            print("Could not identify default branch")


def get_license_path(files_dict, license_files):
    """Given a list of files, returns the URL filepath which contains the license"""
    if files_dict:
        for file in files_dict:
            if file["name"].startswith("."):
                continue
            pattern = (
                r".*(license(s)?|reus(e|ing)|copy(ing)?)(\.(txt|md|rst))?$"
            )
            if re.match(pattern, file["name"], flags=re.IGNORECASE):
                license_path = (
                    repo_url
                    + f"/blob/{graph_ql_query_bit(repo_url)[0]}/"
                    + file["name"]
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
    file1 = TemporaryFile(delete=False)
    file1.close()
    with open(file1.name, "w", encoding="utf-8") as license_handler:
        json.dump(github_read_file(url), license_handler)

    found_spdx_license_id = get_licenses(file1.name)[
        "detected_license_expression_spdx"
    ]
    return found_spdx_license_id


def get_spdx_url(name: str) -> str:
    """Given an SPDX license identifier, return the full URL."""
    return f"https://spdx.org/licenses/{name}.html"


def get_license(repo_url, headers, license_files=[]):
    url = get_license_path(
        graph_ql_query_bit(repo_url)[1], license_files=license_files
    )
    github_read_file(url)
    print(get_spdx_url(extract_license_string(url)))


get_license(repo_url, headers=headers)
