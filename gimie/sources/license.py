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

from typing import List, Tuple
from scancode.api import get_licenses


class LicenseMetadata:
    """
    This class provides metadata about software licenses.
    It requires paths to files containing the license text.

    Attributes
    ----------
    paths:
        The collection of paths containing license information.

    Examples
    --------
    >>> LicenseMetadata('./LICENSE').get_licenses()
    ['https://spdx.org/licenses/Apache-2.0']
    """

    def __init__(self, *paths: str):
        self.paths: Tuple[str] = paths

    def get_licenses(self, min_score: int = 50) -> List[str]:
        """Returns the SPDX URLs of detected licenses.
        Performs a diff comparison between file contents and a
        database of licenses via the scancode API.

        Parameters
        ----------
        min_score:
            The minimal matching score used by scancode (from 0 to 100)
            to return a license match.

        Returns
        -------
        licenses:
            A list of SPDX URLs matching provided licenses,
            e.g. https://spdx.org/licenses/Apache-2.0.html.
        """
        mappings = get_licenses(self.paths[0], min_score=min_score)
        licenses = [
            mapping["spdx_url"] for mapping in mappings.get("licenses")
        ]

        return licenses
