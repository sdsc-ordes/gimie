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
from typing import Dict, Iterable, NamedTuple, Optional, Set, Type

from gimie.graph import Property
from gimie.io import Resource
from gimie.parsers.abstract import Parser
from gimie.parsers.license import LicenseParser, is_license_filename


class ParserInfo(NamedTuple):
    default: bool
    type: Type[Parser]


_PARSERS = {
    "license": ParserInfo(default=True, type=LicenseParser),
}

DEFAULT_PARSERS = {k: v.type for k, v in _PARSERS.items() if v.default}
PARSERS = {k: v.type for k, v in _PARSERS.items()}


def select_parser(
    path: Path,
    parser_collection: Optional[Dict[str, Type[Parser]]] = None,
) -> Optional[Type[Parser]]:
    """Select the appropriate parser from a collection based on a file path.
    If no parser is found, return None.

    Parameters
    ----------
    path:
        The path of the file to parse.
    parser_collection:
        A dictionary of parser names and their corresponding types.
        If None, use the default collection.
    """
    # Only parse licenses in the root directory
    if is_license_filename(path.name) and len(path.stem) == 1:
        name = "license"
    else:
        return None

    if name not in (parser_collection or DEFAULT_PARSERS):
        return None
    return PARSERS.get(name, None)


def parse_files(
    files: Iterable[Resource],
    parser_collection: Optional[Dict[str, Type[Parser]]] = None,
) -> Set[Property]:
    """For each input file, select appropriate parser among a collection and
    parse its contents. Return the union of all parsed properties. If no parser
    is found for a given file, skip it.

    Parameters
    ----------
    files:
        A collection of file-like objects.
    parser_collection:
        A dictionary of parser names and their corresponding types.
        If None, use the default collection.
    """
    properties = set()
    for file in files:
        parser = select_parser(file.path, parser_collection)
        if not parser:
            continue
        data = file.open().read()
        properties |= parser().parse(data or b"")
    return properties
