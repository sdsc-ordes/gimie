from rdflib import Graph, RDF
from gimie.graph.namespaces import SDO


def get_property_value(g, subject, predicate) -> str:
    if g.value(subject, predicate):
        return str(g.value(subject, predicate))
    else:
        return ""


def get_release_date(g, subject) -> str:
    """Returns the release date as a YYYY-MM-DD string, preferring
    datePublished over dateModified. Returns empty string if neither exists."""
    release_date = g.value(subject, SDO.datePublished) or g.value(
        subject, SDO.dateModified
    )
    return str(release_date)[:10] if release_date else ""


def get_licenses(g, subject) -> str:
    """Returns a comma-separated string of SPDX license identifiers.
    Converts SPDX URLs (e.g. https://spdx.org/licenses/MIT.html) to bare ids (e.g. MIT).
    """
    return ",".join(
        str(lic).split("/licenses/")[-1].replace(".html", "")
        for lic in g.objects(subject, SDO.license)
    )


def get_repo_owner(g, subject) -> str:
    """Returns the name of the first author. Authors are stored as blank
    nodes in RDF, with actual properties connected in next nodes."""
    first_author = g.value(subject, SDO.author)
    return (
        get_property_value(g, first_author, SDO.name) if first_author else ""
    )


def convert_to_publiccode(g: Graph) -> dict:

    # Find the SoftwareSourceCode node (= the repo subject)
    subject = next(g.subjects(RDF.type, SDO.SoftwareSourceCode))

    return {
        "publiccodeYmlVersion": "0.5",
        "name": get_property_value(g, subject, SDO.name).split("/")[-1],
        "url": str(subject),
        "softwareVersion": get_property_value(g, subject, SDO.version) or None,
        "releaseDate": get_release_date(g, subject),
        "description": {
            "en": {
                "shortDescription": get_property_value(
                    g, subject, SDO.description
                )[:150],
                "longDescription": get_property_value(
                    g, subject, SDO.description
                ),
            }
        },
        "legal": {
            "license": get_licenses(g, subject),
            "repoOwner": get_repo_owner(g, subject),
        },
        "maintenance": {
            "type": "community",
        },
        "tags": [str(k) for k in g.objects(subject, SDO.keywords)],
    }
