from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from rdflib import Graph, RDF, URIRef
from gimie.converters.abstract import Converter
from gimie.graph.namespaces import SDO

_SHORT_DESC_MIN = 10
_SHORT_DESC_MAX = 150


class PublicCodeConverter(Converter):
    def __init__(self, g: Graph):
        super().__init__(g)
        subject = next(g.subjects(RDF.type, SDO.SoftwareSourceCode), None)
        if subject is None:
            raise ValueError(
                f"No node of type {SDO.SoftwareSourceCode} found in graph"
            )
        self._subject = subject

    def _get(self, predicate: URIRef) -> str | None:
        val = self.g.value(self._subject, predicate)
        return str(val) if val else None

    def _licenses(self) -> dict:
        """Converts SPDX URLs (e.g. https://spdx.org/licenses/MIT.html) to bare ids (e.g. MIT)."""
        licenses = [
            Path(urlparse(str(lic)).path).stem
            for lic in self.g.objects(self._subject, SDO.license)
        ]
        return {"legal": {"license": ",".join(licenses)}} if licenses else {}

    def _contacts(self, predicate: URIRef) -> list[dict]:
        contacts = []
        for person in self.g.objects(self._subject, predicate):
            contact: dict = {}
            name = self.g.value(person, SDO.name)
            if name:
                contact["name"] = str(name)
            email = self.g.value(person, SDO.email)
            if email:
                contact["email"] = str(email)
            if contact:
                contacts.append(contact)
        return contacts

    def _maintenance(self) -> dict:
        """Returns a publiccode maintenance dict.

        Uses schema:author for type 'internal', schema:contributor for
        type 'community'. Only these two types are currently handled.
        """
        contacts = self._contacts(SDO.author)
        if contacts:
            return {"maintenance": {"type": "internal", "contacts": contacts}}

        contacts = self._contacts(SDO.contributor)
        if contacts:
            return {"maintenance": {"type": "community", "contacts": contacts}}

        return {}

    def _version(self) -> dict:
        version = self._get(SDO.version)
        return {"softwareVersion": version} if version else {}

    def _release_date(self) -> dict:
        release_date = self._get(SDO.datePublished) or self._get(
            SDO.dateModified
        )
        if not release_date:
            return {}
        return {"releaseDate": str(datetime.fromisoformat(release_date).date())}

    def _description(self) -> dict:
        desc = self._get(SDO.description)
        if desc is None:
            return {}
        if len(desc) > _SHORT_DESC_MAX:
            return {"description": {"en": {"longDescription": desc}}}
        if len(desc) >= _SHORT_DESC_MIN:
            return {"description": {"en": {"shortDescription": desc}}}
        return {}

    def convert(self) -> dict[str, Any]:
        name = self._get(SDO.name)
        if not name:
            raise ValueError(f"{self._subject} has no schema:name")

        return (
            {
                "publiccodeYmlVersion": "0.5.0",
                "name": name.split("/")[-1],
                "url": str(self._subject),
            }
            | self._version()
            | self._release_date()
            | self._description()
            | self._licenses()
            | self._maintenance()
        )


def convert_to_publiccode(g: Graph) -> dict:
    return PublicCodeConverter(g).convert()
