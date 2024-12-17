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
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from gimie import logger
from gimie.graph.namespaces import SDO, MD4I
from gimie.parsers.abstract import Parser
from gimie.utils.uri import is_valid_orcid, extract_doi_match


class CffParser(Parser):
    """Parse DOI and authors from CITATION.cff."""

    def __init__(self, subject: str):
        super().__init__(subject)

    def parse(self, data: bytes) -> Graph:
        """Extracts DOIs and list of authors from a CFF file and returns a
        graph with triples <subject> <schema:citation> <doi>
        and a number of author objects with <schema:name> and <md4i:orcid> values.
        If no DOIs are found, they will not be included in the graph.
        If no authors are found, they will not be included in the graph.
        If neither authors nor DOIs are found, an empty graph is returned.
        """
        extracted_cff_triples = Graph()
        dois = get_cff_doi(data)
        authors = get_cff_authors(data)

        if dois:
            for doi in dois:
                extracted_cff_triples.add(
                    (self.subject, SDO.citation, URIRef(doi))
                )
        if not authors:
            return extracted_cff_triples
        for author in authors:
            if is_valid_orcid(author["orcid"]):
                orcid = URIRef(author["orcid"])
                extracted_cff_triples.add(
                    (self.subject, SDO.author, URIRef(orcid))
                )
                extracted_cff_triples.add(
                    (
                        URIRef(orcid),
                        SDO.name,
                        Literal(
                            author["given-names"]
                            + " "
                            + author["family-names"]
                        ),
                    )
                )
                extracted_cff_triples.add(
                    (
                        orcid,
                        MD4I.orcidId,
                        Literal(orcid),
                    )
                )
                extracted_cff_triples.add(
                    (
                        orcid,
                        SDO.affiliation,
                        Literal(author["affiliation"]),
                    )
                )
                extracted_cff_triples.add((orcid, RDF.type, SDO.Person))
        return extracted_cff_triples


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

    doi_match = extract_doi_match(doi)

    if doi_match is None:
        raise ValueError(f"Not a valid DOI: {doi}")

    return f"https://doi.org/{doi_match}"


def get_cff_doi(data: bytes) -> Optional[list[str]]:
    """Given a CFF file, returns a list of DOIs, if any.

    Parameters
    ----------
    data
        The cff file body as bytes.

    Returns
    -------
    list of str, optional
        DOIs formatted as valid URLs

    Examples
    --------
    >>> get_cff_doi(bytes("identifiers:\\n    - type: doi\\n      value: 10.5281/zenodo.1234\\n    - type: doi\\n      value: 10.5281/zenodo.5678", encoding="utf8"))
    ['https://doi.org/10.5281/zenodo.1234', 'https://doi.org/10.5281/zenodo.5678']
    >>> get_cff_doi(bytes("identifiers:\\n    - type: doi\\n      value: 10.5281/zenodo.9012", encoding="utf8"))
    ['https://doi.org/10.5281/zenodo.9012']
    >>> get_cff_doi(bytes("abc: def", encoding="utf8"))
    """

    try:
        cff = yaml.safe_load(data.decode())
    except yaml.scanner.ScannerError:
        logger.warning("cannot read CITATION.cff, skipped.")
        return None

    doi_urls = []

    try:
        identifiers = cff["identifiers"]
    except (KeyError, TypeError):
        logger.warning(
            "CITATION.cff does not contain a valid 'identifiers' key."
        )
        return None

    for identifier in identifiers:
        if identifier.get("type") == "doi":
            try:
                doi_url = doi_to_url(identifier["value"])
                doi_urls.append(doi_url)
            except ValueError as err:
                logger.warning(err)

    return doi_urls or None


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
