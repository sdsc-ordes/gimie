from rdflib import Graph, RDF
from gimie.graph.namespaces import SDO


def get_property_value(g, subject, predicate) -> str:
    val = g.value(subject, predicate)
    return str(val) if val else ""


def get_licenses(g, subject):
    """Returns a comma-separated string of SPDX license identifiers, or None if no licenses found.
    Converts SPDX URLs (e.g. https://spdx.org/licenses/MIT.html) to bare ids (e.g. MIT).
    """
    licenses = [
        str(lic).split("/licenses/")[-1].replace(".html", "")
        for lic in g.objects(subject, SDO.license)
    ]
    return ",".join(licenses) if licenses else None


def get_contacts(g, subject, predicate) -> list:
    contacts = []
    for person in g.objects(subject, predicate):
        contact = {}
        name = get_property_value(g, person, SDO.name)
        if name:
            contact["name"] = name
        email = get_property_value(g, person, SDO.email)
        if email:
            contact["email"] = email
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

    return {}


def convert_to_publiccode(g: Graph) -> dict:

    # Find the SoftwareSourceCode node (= the repo subject)
    subject = next(g.subjects(RDF.type, SDO.SoftwareSourceCode), None)
    if subject is None:
        raise ValueError("No SoftwareSourceCode node found in graph")

    desc = get_property_value(g, subject, SDO.description)

    result: dict = {
        "publiccodeYmlVersion": "0.5.0",
        "name": get_property_value(g, subject, SDO.name).split("/")[-1],
        "url": str(subject),
    }

    version = get_property_value(g, subject, SDO.version)
    if version:
        result["softwareVersion"] = version

    # Prefer datePublished, fall back to dateModified
    release_date = get_property_value(g, subject, SDO.datePublished) or get_property_value(g, subject, SDO.dateModified)
    if release_date:
        result["releaseDate"] = release_date[:10]

    # Descriptions <=150 chars go to shortDescription, longer to longDescription
    en_desc = {}
    if len(desc) > 150:
        en_desc["longDescription"] = desc
    elif len(desc) >= 10:
        en_desc["shortDescription"] = desc
    if en_desc:
        result["description"] = {"en": en_desc}

    license = get_licenses(g, subject)
    if license:
        result["legal"] = {"license": license}

    maintenance = get_maintenance(g, subject)
    if maintenance:
        result["maintenance"] = maintenance

    return result
