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
from tempfile import gettempdir, TemporaryDirectory
from typing import Iterable, List, Optional, Union
from gimie.graph.operations import combine_graphs
from gimie.utils import validate_url
from gimie.sources.helpers import (
    get_extractor,
    get_git_provider,
    is_local_source,
    is_remote_source,
    Extractor,
)
import shutil

import git
from rdflib import Graph


class Project:
    """A class to represent a project's git repository.


    Parameters
    ----------
    url :
        The URL of the repository.
    sources:
        The metadata sources to use.

    Examples
    --------
    >>> proj = Project("https://github.com/SDSC-ORD/gimie")
    """

    def __init__(
        self, url: str, sources: Optional[Union[str, Iterable[str]]] = None
    ):

        if not validate_url(url):
            raise ValueError("Input must be a valid URL.")

        sources = normalize_sources(url, sources)
        # Remember if we cloned to cleanup at the end
        self._cloned = False
        self.url = url
        # We only need to clone a remote project
        # if a local extractor is enabled
        if any(map(is_local_source, sources)):
            self.project_dir = self.clone(url)

        self.extractors = self.get_extractors(sources)
        for ex in self.extractors:
            ex.extract()

    def clone(self, url: str) -> str:
        """Clone target url in a new temporary directory"""
        target_dir = TemporaryDirectory().name
        cloned = git.Repo.clone_from(url, target_dir)  # type: ignore
        self._cloned = True

        return str(cloned.working_tree_dir)

    def get_extractors(self, sources: Iterable[str]) -> List[Extractor]:

        extractors: List[Extractor] = []
        for src in sources:
            if is_remote_source(src):
                extractor = get_extractor(self.url, src)  # type: ignore
            else:
                extractor = get_extractor(self.project_dir, src)
            extractors.append(extractor)

        return extractors

    def to_graph(self) -> Graph:
        graphs = map(lambda ex: ex.to_graph(), self.extractors)
        combined_graph = combine_graphs(*graphs)
        return combined_graph

    def serialize(self, format: str = "ttl"):
        return self.to_graph().serialize(format=format)

    def cleanup(self):
        """Recursively delete the project. Only works
        for cloned projects."""
        try:
            tempdir = gettempdir()
            in_temp = self.project_dir.startswith(tempdir)
            if self._cloned and in_temp:
                shutil.rmtree(self.project_dir)
        except AttributeError:
            pass

    def __del__(self):
        self.cleanup()


def normalize_sources(
    url: str, sources: Optional[Union[Iterable[str], str]] = None
) -> List[str]:
    """Input validation and normalization for metadata sources.
    Returns a list of all input sources.

    Parameters
    ----------
    url :
        The URL to the repository.
    sources:
        The metadata sources to use. If None only the git provider is used.

    Returns
    -------
    List[str]
        A list of all input sources. If the git provider was missing
        from input sources, it is inferred from path.

    Examples
    --------
    >>> normalize_sources("https://github.com/SDSC-ORD/gimie")
    ['github']
    >>> normalize_sources("https://github.com/SDSC-ORD/gimie", "github")
    ['github']
    >>> normalize_sources("https://github.com/SDSC-ORD/gimie", ["github"])
    ['github']
    """
    if isinstance(sources, str):
        norm = [sources]
    elif isinstance(sources, Iterable):
        norm = list(sources)
    elif sources is None:
        norm = []
    else:
        raise ValueError(f"Invalid sources: {sources}")

    git_provider = get_git_provider(url)
    if git_provider not in norm:
        norm.append(git_provider)

    return norm
