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
from typing import Iterable, Optional, Tuple

from rdflib import Graph
from rdflib.term import URIRef
from urllib.parse import urlparse

from gimie.extractors import get_extractor, infer_git_provider
from gimie.graph.operations import properties_to_graph
from gimie.parsers import parse_files
from gimie.utils.uri import validate_url


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
        If None, default parsers are used (see gimie.parsers.PARSERS).

    Examples
    --------
    >>> proj = Project("https://github.com/sdsc-ordes/gimie")
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
        if parser_names:
            self.parsers = set(parser_names)
        else:
            self.parsers = None

    def extract(self) -> Graph:
        """Extract repository metadata from git provider to RDF graph and enrich with
        metadata parsed from file contents."""

        repo = self.extractor.extract()
        repo_graph = repo.to_graph()

        files = self.extractor.list_files()
        parsed_graph = parse_files(self.url, files, self.parsers)

        repo_graph += parsed_graph
        return repo_graph


def split_git_url(url: str) -> Tuple[str, str]:
    """Split a git URL into base URL and project path.

    Examples
    --------
    >>> split_git_url("https://gitlab.com/foo/bar")
    ('https://gitlab.com', 'foo/bar')
    """
    base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
    project = urlparse(url).path.strip("/")
    return base_url, project
