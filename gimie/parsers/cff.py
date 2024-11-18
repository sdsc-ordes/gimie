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
from io import BytesIO
import re
from typing import List, Optional, Set
import yaml
from rdflib.term import URIRef
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF
from gimie import logger
from gimie.graph.namespaces import SDO, MD4I
from gimie.parsers.abstract import Parser, Property


class CffParser(Parser):
    """Parse DOI and authorsfrom CITATION.cff into schema:citation <doi>. and schema:"""

    def __init__(self, subject: str):
        super().__init__(subject)

    def parse(self, data: bytes) -> Graph:
        """Extracts a DOI link and list of authors from a CFF file and returns a
        graph with a single triple <subject> <schema:citation> <doi>
        and a number of author objects with <schema:name> and <md4i:orcid> values.
        If no DOI is found, it will not be included in the graph.
        If no authors are found, it will not be included in the graph.
        If neither authors nor DOI are found, an empty graph is returned.
        """
        rdf_graph = Graph()
        doi = get_cff_doi(data)
        authors = get_cff_authors(data)

        if doi:
            rdf_graph.add((self.subject, SDO.citation, URIRef(doi)))
        if not authors:
            return rdf_graph
        for author in authors:
            if author["orcid"]:
                rdf_graph.add(
                    (self.subject, SDO.author, URIRef(author["orcid"]))
                )
                rdf_graph.add(
                    (
                        URIRef(author["orcid"]),
                        SDO.name,
                        Literal(
                            author["given-names"]
                            + " "
                            + author["family-names"]
                        ),
                    )
                )
                rdf_graph.add(
                    (
                        URIRef(author["orcid"]),
                        MD4I.orcidId,
                        Literal(author["orcid"]),
                    )
                )
                rdf_graph.add(
                    (
                        URIRef(author["orcid"]),
                        SDO.affiliation,
                        Literal(author["affiliation"]),
                    )
                )
                rdf_graph.add((URIRef(author["orcid"]), RDF.type, SDO.Person))
        return rdf_graph


def doi_to_url(doi: str) -> str:
    """Formats a doi to an https URL to doi.org.

    Parameters
    ----------
    doi
        doi where the scheme (e.g. https://) and
        hostname (e.g. doi.org) may be missing.

    Returns
    -------
    str
        doi formatted as a valid url. Base url
        is set to https://doi.org when missing.

    Examples
    --------
    >>> doi_to_url("10.0000/example.abcd")
    'https://doi.org/10.0000/example.abcd'
    >>> doi_to_url("doi.org/10.0000/example.abcd")
    'https://doi.org/10.0000/example.abcd'
    >>> doi_to_url("https://doi.org/10.0000/example.abcd")
    'https://doi.org/10.0000/example.abcd'
    """

    # regex from:
    # https://www.crossref.org/blog/dois-and-matching-regular-expressions
    doi_match = re.search(
        r"10.\d{4,9}/[-._;()/:A-Z0-9]+$", doi, flags=re.IGNORECASE
    )

    if doi_match is None:
        raise ValueError(f"Not a valid DOI: {doi}")

    short_doi = doi_match.group()

    return f"https://doi.org/{short_doi}"


def get_cff_doi(data: bytes) -> Optional[str]:
    """Given a CFF file, returns the DOI, if any.

    Parameters
    ----------
    data
        The cff file body as bytes.

    Returns
    -------
    str, optional
        doi formatted as a valid url

    Examples
    --------
    >>> get_cff_doi(bytes("doi:   10.5281/zenodo.1234", encoding="utf8"))
    'https://doi.org/10.5281/zenodo.1234'
    >>> get_cff_doi(bytes("abc: def", encoding="utf8"))

    """

    try:
        cff = yaml.safe_load(data.decode())
    except yaml.scanner.ScannerError:
        logger.warning("cannot read CITATION.cff, skipped.")
        return None

    try:
        doi_url = doi_to_url(cff["doi"])
    # No doi in cff file
    except (KeyError, TypeError):
        logger.warning("CITATION.cff does not contain a 'doi' key.")
        doi_url = None
    # doi is malformed
    except ValueError as err:
        logger.warning(err)
        doi_url = None

    return doi_url


def get_cff_authors(data: bytes) -> Optional[List[dict[str, str]]]:
    """Given a CFF file, returns a list of dictionaries containing orcid, affiliation, first and last names of authors, if any.

    Parameters
    ----------
    data
        The cff file body as bytes.

    Returns
    -------
    list(dict), optional
        orcid, names strings of authors

    Examples
    --------
    >>> get_cff_doi(bytes(CFF_path, encoding="utf8"))
    [{orcid:'https://orcid.org/1234-5678-9101-1121', family-names: 'Druskat', given-names: 'Stephan', affiliation: 'EPFL},{orcid:'https://orcid.org/1234-5678-9101-2354', family-names: 'English', given-names: 'Johnny'}
    orcid: }]

    """

    try:
        cff = yaml.safe_load(data.decode())
    except yaml.scanner.ScannerError:
        logger.warning("cannot read CITATION.cff, skipped.")
        return None

    authors = []
    try:
        for author in cff["authors"]:
            author_dict = {
                "family-names": author.get("family-names", ""),
                "given-names": author.get("given-names", ""),
                "orcid": author.get("orcid", ""),
                "affiliation": author.get("affiliation", ""),
            }
            authors.append(author_dict)
    except KeyError:
        logger.warning("CITATION.cff does not contain an 'authors' key.")
        return None

    return authors if authors else None
