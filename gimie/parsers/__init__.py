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
"""Files which can be parsed by gimie."""
from pathlib import Path
from typing import NamedTuple, Optional, Type

from gimie.parsers.abstract import Parser
from gimie.parsers.license import LicenseParser, is_license_filename


class ParserInfo(NamedTuple):
    default: bool
    type: Type[Parser]


_PARSERS = {
    "license": ParserInfo(default=True, type=LicenseParser),
}

DEFAULT_PARSERS = {k: v.type for k, v in _PARSERS.items() if v.default}
EXTRA_PARSERS = {k: v.type for k, v in _PARSERS.items() if not v.default}


def get_parser(path: Path, parsers=DEFAULT_PARSERS) -> Optional[Type[Parser]]:
    """Get the appropriate parser based on a file path."""
    # Only parse licenses in the root directory
    if is_license_filename(path.name) and len(path.stem) == 1:
        name = "license"
    else:
        name = None
    return parsers.get(name, None)
