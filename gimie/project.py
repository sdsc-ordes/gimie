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
"""Orchestration of multiple extractors for a given project.
This is the main entry point for end-to-end analysis."""
from typing import Iterable, List, Optional, Tuple

from rdflib import Graph
from rdflib.term import URIRef
from urllib.parse import urlparse

from gimie.graph.operations import combine_graphs
from gimie.utils import validate_url
from gimie.extractors import GIT_PROVIDERS, Extractor
from gimie.parsers import PARSERS, Parser


class Project:
    """A class to represent a project's git repository.


    Parameters
    ----------
    path:
        The full path (URL) of the repository.
    base_url:
        The base URL of the git remote. Can be used to
        specify delimitation between base URL and project name.
    git_provider:
        The name of the git provider to extract metadata from.
        ('git', 'github', 'gitlab')
    parser_names:
        Names of file parsers to use. ('license').
        If None, all parsers are used.

    Examples
    --------
    >>> proj = Project("https://github.com/SDSC-ORD/gimie")
    >>> assert isinstance(proj.extract(), Graph)
    """

    def __init__(
        self,
        path: str,
        base_url: Optional[str] = None,
        git_provider: Optional[str] = None,
        parser_names: Optional[Iterable[str]] = None,
    ):

        if not git_provider:
            git_provider = infer_git_provider(path)

        self.base_url = base_url
        self.project_dir = None
        self._cloned = False
        if validate_url(path):
            self.url = path
        else:
            self.project_dir = path

        self.extractor = get_extractor(
            self.url,
            git_provider,
            base_url=self.base_url,
            local_path=self.project_dir,
        )
        self.parsers = get_parsers(path, parser_names)

    def extract(self) -> Graph:
        """Extract repository metadata from git provider to RDF graph and enrich with
        metadata parsed from file contents."""

        repo = self.extractor.extract()
        repo_graph = repo.to_graph()

        files = self.extractor.list_files()
        parsed_graphs = [
            parser.parse_multiple(files) for parser in self.parsers
        ]

        repo_graph += combine_graphs(repo_graph, *parsed_graphs)
        return repo_graph


def split_git_url(url) -> Tuple[str, str]:
    base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
    project = urlparse(url).path.strip("/")
    return base_url, project


def get_extractor(
    url: str,
    source: str,
    base_url: Optional[str] = None,
    local_path: Optional[str] = None,
) -> Extractor:
    """Instantiate the correct extractor for a given source.

    Parameters
    -----------
    URL
        Where the repository metadata is extracted from.
    source
        The source of the repository (git, gitlab, github, ...).
    base_url
        The base URL of the git remote.
    local_path
        If applicable, the path to the directory where the
        repository is cloned.
    """
    try:
        return GIT_PROVIDERS[source](
            url, base_url=base_url, local_path=local_path
        )
    except KeyError as err:
        raise ValueError(
            f"Unknown git provider: {source}.\n"
            f"Supported sources: {', '.join(GIT_PROVIDERS)}"
        ) from err


def get_parsers(
    uri: str, parser_names: Optional[Iterable[str]] = None
) -> List[Parser]:
    """Instantiate the correct parsers for a given URI.
    If parser_names is None, all parsers are used."""

    parsers = []

    if parser_names is None:
        parser_names = PARSERS.keys()

    for parser_name in parser_names:
        try:
            parsers.append(PARSERS[parser_name](URIRef(uri)))
        except KeyError as err:
            raise ValueError(
                f"Unknown parser: {parser_name}.\n"
                f"Supported parsers: {', '.join(PARSERS)}"
            ) from err
    return parsers


def infer_git_provider(url: str) -> str:
    """Given a git repository URL, return the corresponding git provider.
    Local path or unsupported git providers will return "git"."""
    # NOTE: We just check if the provider name is in the URL.
    # We may want to use a more robust check.
    if validate_url(url):
        for name, _ in GIT_PROVIDERS.items():
            if name in url and name != "git":
                return name
    # Fall back to git if local path or unsupported provider
    return "git"
