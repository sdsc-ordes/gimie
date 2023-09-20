from tempfile import TemporaryFile
import os
import re
from scancode.api import get_licenses
import requests
import json

# from gimie.sources.github import GithubExtractor


github_token = os.environ.get("GITHUB_TOKEN")
headers = {"Authorization": f"token {github_token}"}


def get_default_branch_name_and_root_files_dict(repo_url: str) -> tuple:
    """Given a repository URL, returns a json document containing the repository default branch name and
    a dictionary of filenames which can be found in the root of the repository"""
    repo_url = repo_url.rstrip("/")
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


def get_license_path(repo_url, files_dict) -> str:
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
                    repo_url
                    + f"/blob/{get_default_branch_name_and_root_files_dict(repo_url)[0]}/"
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


def github_read_file(url: str, github_token=None) -> dict:
    """Uses the Github API to download the license file using its URL"""
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    return data


def extract_license_string(url: str) -> str:
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


def get_license(repo_url: str, headers: dict[str, str]) -> str:
    """Finds a license in a github repository, extracts it, scans it and returns the result as an SPDX identifier URL"""
    license_file_path = get_license_path(
        repo_url, get_default_branch_name_and_root_files_dict(repo_url)[1]
    )
    license_string = extract_license_string(license_file_path)
    spdx_url = get_spdx_url(license_string)
    return spdx_url
