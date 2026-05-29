from rdflib import Graph, RDF
from gimie.graph.namespaces import SDO


def get_property_value(g, subject, predicate) -> str:
    if g.value(subject, predicate):
        return str(g.value(subject, predicate))
    else:
        return ""


def get_licenses(g, subject) -> str:
    """Returns a comma-separated string of SPDX license identifiers.
    Converts SPDX URLs (e.g. https://spdx.org/licenses/MIT.html) to bare ids (e.g. MIT).
    """
    return ",".join(
        str(lic).split("/licenses/")[-1].replace(".html", "")
        for lic in g.objects(subject, SDO.license)
    )


def get_contacts(g, subject, predicate) -> list:
    contacts = []
    for person in g.objects(subject, predicate):
        contact = {}
        name = get_property_value(g, person, SDO.name)
        if name:
            contact["name"] = name
        email = get_property_value(g, person, SDO.email)
        if email:
            contact["email"] = email.replace("@", "\x64")
        if contact:
            contacts.append(contact)
    return contacts


def get_maintenance(g, subject) -> dict:
    """Returns a publiccode maintenance dict.

    Uses schema:author for type 'internal', schema:contributor for
    type 'community'. Only these two types are currently handled.
    """
    contacts = get_contacts(g, subject, SDO.author)
    if contacts:
        return {"type": "internal", "contacts": contacts}

    contacts = get_contacts(g, subject, SDO.contributor)
    if contacts:
        return {"type": "community", "contacts": contacts}

    return {"type": "community", "contacts": None}


def convert_to_publiccode(g: Graph) -> dict:

    # Find the SoftwareSourceCode node (= the repo subject)
    subject = next(g.subjects(RDF.type, SDO.SoftwareSourceCode))

    return {
        "publiccodeYmlVersion": "0.5",
        "name": get_property_value(g, subject, SDO.name).split("/")[-1],
        "url": str(subject),
        "platforms": None,
        "developmentStatus": None,
        "softwareType": None,
        "description": {
            "en": {
                "shortDescription": get_property_value(
                    g, subject, SDO.description
                )[:150],
                "longDescription": get_property_value(
                    g, subject, SDO.description
                ),
                "features": None,
            }
        },
        "legal": {
            "license": get_licenses(g, subject),
        },
        "maintenance": get_maintenance(g, subject),
        "localisation": {
            "localisationReady": None,
            "availableLanguages": None,
        },
    }
