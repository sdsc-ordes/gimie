from rdflib import Graph, URIRef

def add_license_to_graph(path: str, license: str):
    g = Graph()
    g.add(
        (
            URIRef(path),
            URIRef("https://schema.org/license"),
            URIRef(str(license)),
        )
    )