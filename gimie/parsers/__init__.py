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
from typing import Iterable, NamedTuple, Optional, Set, Type

from gimie.graph import Property
from gimie.io import Resource
from gimie.parsers.abstract import Parser
from gimie.parsers.license import LicenseParser, is_license_filename
from gimie.parsers.cff import CffParser

from rdflib import Graph


class ParserInfo(NamedTuple):
    default: bool
    type: Type[Parser]


PARSERS = {
    "license": ParserInfo(default=True, type=LicenseParser),
    "cff": ParserInfo(default=True, type=CffParser),
}


def get_parser(name: str) -> Type[Parser]:
    """Get a parser by name."""
    parser = PARSERS.get(name, None)
    if parser is None:
        raise ValueError(
            f"Unknown parser: {name}.\n"
            f"Supported parsers: {', '.join(PARSERS)}"
        )
    return parser.type


def list_default_parsers() -> Set[str]:
    """List the names of all default parsers."""
    return {k for k, v in PARSERS.items() if v.default}


def list_parsers() -> Set[str]:
    """List the names of all parsers."""
    return set(PARSERS.keys())


def select_parser(
    path: Path,
    parsers: Optional[Set[str]] = None,
) -> Optional[Type[Parser]]:
    """Select the appropriate parser from a collection based on a file path.
    If no parser is found, return None.

    Parameters
    ----------
    path:
        The path of the file to parse.
    parsers:
        A set of parser names. If None, use the default collection.
    """
    # Only parse licenses and citations in the root directory
    if is_license_filename(path.name) and len(path.parts) == 1:
        name = "license"
    elif path.name == "CITATION.cff" and len(path.parts) == 1:
        name = "cff"
    else:
        return None

    if name not in (parsers or list_parsers()):
        return None
    return get_parser(name)


def parse_files(
    subject: str,
    files: Iterable[Resource],
    parsers: Optional[Set[str]] = None,
) -> Graph:
    """For each input file, select appropriate parser among a collection and
    parse its contents. Return the union of all parsed properties in the form of triples.
    If no parser is found for a given file, skip it.

    Parameters
    ----------
    subject:
        The subject URI of the repository.
    files:
        A collection of file-like objects.
    parsers:
        A set of parser names. If None, use the default collection.
    """
    parsed_properties = Graph()
    for file in files:
        parser = select_parser(file.path, parsers)
        if not parser:
            continue
        data = file.open().read()
        parsed_properties |= parser(subject).parse(data or b"")
    return parsed_properties
