# Gimie
# Copyright 2022 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import re

from typing import List


class FilesMetadata:
    """This classes provides helpers to navigate and read metadata files
    from a project directory.

    Examples
    --------
    >>> FilesMetadata('.').locate_licenses()
    ['./LICENSE']
    """

    def __init__(self, project_path: str):
        self.project_path = project_path

    def locate_licenses(self) -> List[str]:
        """Returns valid potential paths to license files in the project.
        This uses pattern-matching on file names.
        """
        license_files = []
        pattern = r".*(license(s)?|reus(e|ing)|copy(ing)?)(\.(txt|md|rst))?$"
        for root, _, files in os.walk(self.project_path):
            if not root.startswith("./."):
                for file in files:
                    file = os.path.join(root, file)

                    if re.match(pattern, file, flags=re.IGNORECASE):
                        license_files.append(file)

        return license_files
