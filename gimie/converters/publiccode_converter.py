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

    def _get(self, predicate: URIRef) -> str:
        val = self._g.value(self._subject, predicate)
        return str(val) if val else ""

    def _get_for(self, node, predicate: URIRef) -> str:
        val = self._g.value(node, predicate)
        return str(val) if val else ""

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
            name = self._get_for(person, SDO.name)
            if name:
                contact["name"] = name
            email = self._get_for(person, SDO.email)
            if email:
                contact["email"] = email
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
            return {"type": "internal", "contacts": contacts}

        contacts = self._contacts(SDO.contributor)
        if contacts:
            return {"type": "community", "contacts": contacts}

        return {}

    def convert(self) -> dict:
        result: dict = {
            "publiccodeYmlVersion": "0.5.0",
            "name": self._get(SDO.name).split("/")[-1],
            "url": str(self._subject),
        }

        version = self._get(SDO.version)
        if version:
            result["softwareVersion"] = version

        # Prefer datePublished, fall back to dateModified
        release_date = self._get(SDO.datePublished) or self._get(SDO.dateModified)
        if release_date:
            result["releaseDate"] = release_date[:10]

        desc = self._get(SDO.description)
        en_desc: dict = {}
        if len(desc) > _SHORT_DESC_MAX:
            en_desc["longDescription"] = desc
        elif len(desc) >= _SHORT_DESC_MIN:
            en_desc["shortDescription"] = desc
        if en_desc:
            result["description"] = {"en": en_desc}

        license_str = self._licenses()
        if license_str:
            result["legal"] = {"license": license_str}

        maintenance = self._maintenance()
        if maintenance:
            result["maintenance"] = maintenance

        return result


def convert_to_publiccode(g: Graph) -> dict:
    return _PublicCodeConverter(g).convert()
