# Gimie
# Copyright 2022 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from scancode.api import get_licenses
import re

path = r"C:\Users\franken\gimie"  # this is to be filled with the path from the CLI input, not sure how to access it


def find_licenses(path: str):
    """returns a python list of licenses found at destination"""
    path_files = os.listdir(path)
    print(path)
    print(path_files)
    found_licenses = []
    for file in path_files:
        result = re.match("licens", file, flags=re.IGNORECASE)
        #regex used is very basic right now, what are other common license file names?
        if result:
            license_location = str(path) + "\\" + str(file)
            license_mappings = get_licenses(license_location, min_score=50)
            # todo we need some tests to see how to set this min_score param
            found_licenses.append(
                ((license_mappings.get("licenses")[0]).get("key"))
            )

    return found_licenses

    # todo had to remove file "html" from gimie because it was matching the package html

print(find_licenses(path))


# class LicenseMetadata:
#     def __init__(self, path: str):
#         raise NotImplementedError
