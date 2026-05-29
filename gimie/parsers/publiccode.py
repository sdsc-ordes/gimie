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
"""Parse metadata from publiccode.yml files (v0.5.0 standard)."""

from __future__ import annotations

from typing import Dict, List, Optional

import yaml
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

from gimie import logger
from gimie.graph.namespaces import SDO
from gimie.parsers.abstract import Parser
from gimie.utils.uri import sanitize_identifier


class PublicCodeParser(Parser):
    """Parse metadata from publiccode.yml (v0.5.0)."""

    def parse(self, data: bytes) -> Graph:
        graph = Graph()

        pc = _parse_yaml(data)
        if pc is None:
            return graph

        is_based_on = get_publiccode_is_based_on(pc)
        contacts = get_publiccode_contacts(pc)

        if is_based_on:
            for url in is_based_on:
                graph.add((self.subject, SDO.isBasedOn, URIRef(url)))

        if contacts:
            for contact in contacts:
                uid = sanitize_identifier(contact["name"])
                person_uri = URIRef(f"{self.subject}/{uid}")

                graph.add((self.subject, SDO.author, person_uri))
                graph.add((person_uri, RDF.type, SDO.Person))
                graph.add((person_uri, SDO.name, Literal(contact["name"])))
                graph.add((person_uri, SDO.identifier, Literal(uid)))

                if contact.get("email") is not None:
                    graph.add(
                        (person_uri, SDO.email, Literal(contact["email"]))
                    )
                if contact.get("affiliation") is not None:
                    graph.add(
                        (
                            person_uri,
                            SDO.affiliation,
                            Literal(contact["affiliation"]),
                        )
                    )

        return graph


def _parse_yaml(data: bytes) -> Optional[dict]:
    """Parse publiccode.yml bytes into a dict.

    Returns None on invalid YAML or non-dict content.
    """
    try:
        pc = yaml.safe_load(data.decode())
    except (yaml.YAMLError, UnicodeDecodeError):
        logger.warning("Cannot read publiccode.yml, skipped.")
        return None

    if not isinstance(pc, dict):
        return None

    return pc


def get_publiccode_is_based_on(pc: dict) -> Optional[List[str]]:
    """Given a parsed publiccode.yml dict, return the isBasedOn URLs, if any.

    Parameters
    ----------
    pc
        The parsed publiccode.yml content as a dict.

    Returns
    -------
    list of str, optional
        URLs of upstream repositories.

    Examples
    --------
    >>> get_publiccode_is_based_on({"isBasedOn": "https://github.com/org/upstream"})
    ['https://github.com/org/upstream']
    >>> get_publiccode_is_based_on({"name": "test"})
    """
    is_based_on = pc.get("isBasedOn")
    if not is_based_on:
        return None

    urls = is_based_on if isinstance(is_based_on, list) else [is_based_on]
    return [str(url) for url in urls]


def get_publiccode_contacts(pc: dict) -> Optional[List[Dict[str, str]]]:
    """Given a parsed publiccode.yml dict, return maintenance contacts, if any.

    Parameters
    ----------
    pc
        The parsed publiccode.yml content as a dict.

    Returns
    -------
    list of dict, optional
        Each dict contains 'name' (mandatory) and optionally
        'email' and 'affiliation'.

    Examples
    --------
    >>> get_publiccode_contacts({"maintenance": {"contacts": [{"name": "Jane Doe", "email": "jane@example.org"}]}})
    [{'name': 'Jane Doe', 'email': 'jane@example.org'}]
    >>> get_publiccode_contacts({"name": "test"})
    """
    maintenance = pc.get("maintenance")
    if not isinstance(maintenance, dict):
        return None

    contacts = maintenance.get("contacts")
    if not isinstance(contacts, list):
        return None

    result = []
    for contact in contacts:
        if not isinstance(contact, dict):
            continue
        name = contact.get("name")
        if not name:
            continue
        entry: Dict[str, str] = {"name": name}
        entry["email"] = contact.get("email")
        entry["affiliation"] = contact.get("affiliation")
        result.append(entry)

    return result if result else None
