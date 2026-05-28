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
"""Parse metadata from publiccode.yml files (v0.5.0 standard).

Only extracts properties that are not already provided by
extractors or other parsers (license, description, version, etc.).
Currently extracts:
- maintenance/contacts -> schema:author Person nodes
- isBasedOn -> schema:isBasedOn
"""

from __future__ import annotations

from typing import Any, Dict, List

import yaml
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

from gimie import logger
from gimie.graph.namespaces import SDO
from gimie.parsers.abstract import Parser


def _sanitize_identifier(name: str) -> str:
    """Create a URL-safe identifier from a contact name.

    >>> _sanitize_identifier("John Doe")
    'john_doe'
    """
    return name.strip().replace(" ", "_").lower()


class PublicCodeParser(Parser):
    """Parse metadata from publiccode.yml (v0.5.0)."""

    def __init__(self, subject: str):
        super().__init__(subject)

    def parse(self, data: bytes) -> Graph:
        """Extract RDF triples from a publiccode.yml file.

        Maps publiccode.yml fields to schema.org properties compatible
        with gimie's existing vocabulary.
        """
        graph = Graph()

        try:
            pc = yaml.safe_load(data.decode())
        except (yaml.YAMLError, UnicodeDecodeError):
            logger.warning("Cannot read publiccode.yml, skipped.")
            return graph

        if not isinstance(pc, dict):
            logger.warning("publiccode.yml is not a valid YAML mapping.")
            return graph

        self._add_is_based_on(graph, pc)
        self._add_contacts(graph, pc)

        return graph

    def _add_description(self, graph: Graph, pc: Dict[str, Any]) -> None:
        description = _get_description(pc)
        if description:
            graph.add(
                (self.subject, SDO.description, Literal(description))
            )

    def _add_version(self, graph: Graph, pc: Dict[str, Any]) -> None:
        version = pc.get("softwareVersion")
        if version:
            graph.add((self.subject, SDO.version, Literal(str(version))))

    def _add_release_date(self, graph: Graph, pc: Dict[str, Any]) -> None:
        release_date = pc.get("releaseDate")
        if release_date:
            graph.add(
                (
                    self.subject,
                    SDO.datePublished,
                    Literal(str(release_date)),
                )
            )

    def _add_licenses(self, graph: Graph, pc: Dict[str, Any]) -> None:
        legal = pc.get("legal")
        if not isinstance(legal, dict):
            return
        license_expr = legal.get("license")
        if not license_expr:
            return
        for spdx_id in _parse_spdx_expression(str(license_expr)):
            url = _spdx_id_to_url(spdx_id)
            graph.add((self.subject, SDO.license, URIRef(url)))

    def _add_is_based_on(self, graph: Graph, pc: Dict[str, Any]) -> None:
        is_based_on = pc.get("isBasedOn")
        if not is_based_on:
            return
        urls = (
            is_based_on if isinstance(is_based_on, list) else [is_based_on]
        )
        for url in urls:
            graph.add((self.subject, SDO.isBasedOn, URIRef(str(url))))

    def _add_contacts(self, graph: Graph, pc: Dict[str, Any]) -> None:
        maintenance = pc.get("maintenance")
        if not isinstance(maintenance, dict):
            return
        contacts = maintenance.get("contacts")
        if not isinstance(contacts, list):
            return

        for contact in contacts:
            if not isinstance(contact, dict):
                continue
            name = contact.get("name")
            if not name:
                continue

            uid = _sanitize_identifier(name)
            person_uri = URIRef(f"{self.subject}/{uid}")

            graph.add((self.subject, SDO.author, person_uri))
            graph.add((person_uri, RDF.type, SDO.Person))
            graph.add((person_uri, SDO.name, Literal(name)))
            graph.add(
                (person_uri, SDO.identifier, Literal(uid))
            )

            email = contact.get("email")
            if email:
                graph.add((person_uri, SDO.email, Literal(email)))

            affiliation = contact.get("affiliation")
            if affiliation:
                graph.add(
                    (person_uri, SDO.affiliation, Literal(affiliation))
                )
