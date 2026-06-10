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
            raise ValueError(f"No node of type {SDO.SoftwareSourceCode} found in graph")
        self._subject = subject

    def _get(self, predicate: URIRef) -> str | None:
        val = self.g.value(self._subject, predicate)
        return str(val) if val else None

    def _licenses(self) -> str | None:
        """Comma-separated SPDX identifiers, or None if no licenses found.
        Converts SPDX URLs (e.g. https://spdx.org/licenses/MIT.html) to bare ids (e.g. MIT).
        """
        licenses = [
            Path(urlparse(str(lic)).path).stem
            for lic in self.g.objects(self._subject, SDO.license)
        ]
        return ",".join(licenses) if licenses else None

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

    def _maintenance(self) -> dict | None:
        """Returns a publiccode maintenance dict.

        Uses schema:author for type 'internal', schema:contributor for
        type 'community'. Only these two types are currently handled.
        """
        contacts = self._contacts(SDO.author)
        if contacts:
            return {"type": "internal", "contacts": contacts}

        contacts = self._contacts(SDO.contributor)
        if contacts:
            return {"type": "community", "contacts": contacts}

        return None

    def _description(self) -> dict | None:
        desc = self.get(SDO.description)
        if desc is None:
            return None
        if len(desc) > _SHORT_DESC_MAX:
            return {"en": {"longDescription": desc}}
        if len(desc) >= _SHORT_DESC_MIN:
            return {"en": {"shortDescription": desc}}
        return None

    def convert(self) -> dict[str, Any]:
        name = self.get(SDO.name)
        if not name:
            raise ValueError(f"{self._subject} has no schema:name")

        version = self.get(SDO.version)
        release_date = self.get(SDO.datePublished) or self.get(
            SDO.dateModified
        )
        description = self._description()
        license_str = self._licenses()
        maintenance = self._maintenance()

        return {
            "publiccodeYmlVersion": "0.5.0",
            "name": name.split("/")[-1],
            "url": str(self._subject),
            **({"softwareVersion": version} if version else {}),
            **(
                {"releaseDate": release_date[:10]}
                if release_date and len(release_date) >= 10
                else {}
            ),
            **({"description": description} if description else {}),
            **({"legal": {"license": license_str}} if license_str else {}),
            **({"maintenance": maintenance} if maintenance else {}),
        }


def convert_to_publiccode(g: Graph) -> dict:
    return PublicCodeConverter(g).convert()
