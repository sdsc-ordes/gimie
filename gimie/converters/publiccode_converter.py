from typing import Any

from rdflib import Graph, RDF, URIRef
from gimie.graph.namespaces import SDO

_SHORT_DESC_MIN = 10
_SHORT_DESC_MAX = 150


class _PublicCodeConverter:
    def __init__(self, g: Graph):
        subject = next(g.subjects(RDF.type, SDO.SoftwareSourceCode), None)
        if subject is None:
            raise ValueError("No SoftwareSourceCode node found in graph")
        self._g = g
        self._subject = subject

    def _get(self, predicate: URIRef) -> str | None:
        val = self._g.value(self._subject, predicate)
        return str(val) if val else None

    def _licenses(self) -> str | None:
        """Comma-separated SPDX identifiers, or None if no licenses found.
        Converts SPDX URLs (e.g. https://spdx.org/licenses/MIT.html) to bare ids (e.g. MIT).
        """
        licenses = [
            str(lic).split("/licenses/")[-1].replace(".html", "")
            for lic in self._g.objects(self._subject, SDO.license)
        ]
        return ",".join(licenses) if licenses else None

    def _contacts(self, predicate: URIRef) -> list[dict]:
        contacts = []
        for person in self._g.objects(self._subject, predicate):
            contact: dict = {}
            name = self._g.value(person, SDO.name)
            if name:
                contact["name"] = str(name)
            email = self._g.value(person, SDO.email)
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

    def convert(self) -> dict[str, Any]:
        name = self._get(SDO.name)
        if not name:
            raise ValueError("SoftwareSourceCode has no schema:name")

        desc = self._get(SDO.description)
        en_desc = {}
        if desc is not None:
            if len(desc) > _SHORT_DESC_MAX:
                en_desc["longDescription"] = desc
            elif len(desc) >= _SHORT_DESC_MIN:
                en_desc["shortDescription"] = desc

        version = self._get(SDO.version)
        release_date = self._get(SDO.datePublished) or self._get(SDO.dateModified)
        license_str = self._licenses()
        maintenance = self._maintenance()

        return {
            "publiccodeYmlVersion": "0.5.0",
            "name": name.split("/")[-1],
            "url": str(self._subject),
            **( {"softwareVersion": version} if version else {} ),
            **( {"releaseDate": release_date[:10]} if release_date and len(release_date) >= 10 else {} ),
            **( {"description": {"en": en_desc}} if en_desc else {} ),
            **( {"legal": {"license": license_str}} if license_str else {} ),
            **( {"maintenance": maintenance} if maintenance else {} ),
        }
    


def convert_to_publiccode(g: Graph) -> dict:
    return _PublicCodeConverter(g).convert()
