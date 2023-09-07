import os
import re
from typing import List

from gimie.graph.namespaces import GIMIE


import base64
import os
import re
from typing import List

from gimie.graph.namespaces import GIMIE
import requests
import json

headers = {'Authorization': 'token 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'}
username = 'rmfranken'
github_token = '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'
def get_files_in_repository_root(repo_url):
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
            files = [item['name'] for item in contents if item['type'] == 'file']

            return files

        else:
            # If the request was not successful, raise an exception
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# https://github.com/SDSC-ORD/gimie/blob/main/LICENSE
# Example usage:
repo_url = "https://github.com/SDSC-ORD/gimie"
files_in_root = get_files_in_repository_root(repo_url)
license_files = []
pattern = r".*(license(s)?|reus(e|ing)|copy(ing)?)(\.(txt|md|rst))?$"
def return_license_path(files):
    if files:
        for file in files:
            print(file)
            if file.startswith("."):
                continue

            if re.match(pattern, file, flags=re.IGNORECASE):
                license_path = repo_url+"/blob/main/"+file
                license_files.append(license_path)
    for license_file in license_files:
        return license_file

print(return_license_path(get_files_in_repository_root(repo_url)))

url = (return_license_path(get_files_in_repository_root(repo_url)))
def github_read_file(url, github_token=None):
    headers = {}
    if github_token:
        headers['Authorization'] = f"token {github_token}"

    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    print(data)
    return data


my_data = github_read_file(url)
# json.load(my_data)
file1= open("myfile.json", 'w', encoding='utf-8')

file1.write(str(my_data))
file1.close()

#     print(json.dump())


# def locate_licenses(path: str, recurse: bool = False) -> List[str]:
#     """Returns valid potential paths to license files in the project.
#     This uses pattern-matching on file names.
#
#     Parameters
#     ----------
#     path:
#         The root path to search for license files.
#     recurse:
#         Whether to look into subdirectories.
#
#     Returns
#     -------
#     license_files:
#         The list of relative paths (from input path) to files which
#         potentially contain license text.
#
#     Examples
#     --------
#     >>> locate_licenses('.')
#     ['./LICENSE']
#     """
#     license_files = []
#     pattern = r".*(license(s)?|reus(e|ing)|copy(ing)?)(\.(txt|md|rst))?$"
#
#     for root, _, files in os.walk(path):
#         # skip toplevel hidden dirs (e.g. .git/)
#         subdir = os.path.relpath(root, path)
#         if subdir.startswith(".") and subdir != ".":
#             continue
#         for file in files:
#             # skip hidden files
#             if file.startswith("."):
#                 continue
#
#             if re.match(pattern, file, flags=re.IGNORECASE):
#                 license_path = os.path.join(root, file)
#                 license_files.append(license_path)
#
#         # The first root of os.walk is the current dir
#         if not recurse:
#             return license_files
#
#     return license_files


def get_spdx_url(name: str) -> str:
    """Given an SPDX license identifier, return the full URL."""
    return f"https://spdx.org/licenses/{name}"

def get_spdx_url(name: str) -> str:
    """Given an SPDX license identifier, return the full URL."""
    return f"https://spdx.org/licenses/{name}"
