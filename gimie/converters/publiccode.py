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


def convert_to_publiccode(g: Graph) -> dict:

    # Find the SoftwareSourceCode node (= the repo subject)
    subject = next(g.subjects(RDF.type, SDO.SoftwareSourceCode))

    return {
        "publiccodeYmlVersion": "0.5",
        "name": get_property_value(g, subject, SDO.name).split("/")[-1],
        "url": str(subject),
        "platforms": "toFill",
        "developmentStatus": "toFill",
        "softwareType": "toFill",
        "description": {
            "en": {
                "shortDescription": get_property_value(
                    g, subject, SDO.description
                )[:150],
                "longDescription": get_property_value(
                    g, subject, SDO.description
                ),
                "features": "toFill",
            }
        },
        "legal": {
            "license": get_licenses(g, subject),
        },
        "maintenance": {"type": "community", "contacts": "toFill"},
        "localisation": {
            "localisationReady": "toFill",
            "availableLanguages": "toFill",
        },
    }
