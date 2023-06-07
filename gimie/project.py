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

import shutil
import git
from rdflib import Graph

from gimie.graph.operations import combine_graphs
from gimie.utils import validate_url
from gimie.sources import SOURCES
from gimie.sources.abstract import Extractor
from gimie.utils import validate_url


class Project:
    """A class to represent a project's git repository.


    Parameters
    ----------
    path :
        The path to the repository, either a file path or a URL.
    sources:
        The metadata sources to use.

    Examples
    --------
    >>> proj = Project("https://github.com/SDSC-ORD/gimie")
    """

    def __init__(
        self, path: str, sources: Optional[Union[str, Iterable[str]]] = None
    ):

        sources = normalize_sources(path, sources)
        # Remember if we cloned to cleanup at the end
        self._cloned = False
        if validate_url(path):
            self.url = path
            # We only need to clone a remote project
            # if a local extractor is enabled
            if any(map(is_local_source, sources)):
                self.project_dir = self.clone(path)
        else:
            self.url = None
            self.project_dir = path

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
                extractor = get_extractor(self.project_dir, src, _id=self.url)
            extractors.append(extractor)

        return extractors

    def to_graph(self) -> Graph:
        graphs = map(lambda ex: ex.to_graph(), self.extractors)
        combined_graph = combine_graphs(*graphs)
        return combined_graph

    def serialize(self, format: str = "ttl", **kwargs):
        return self.to_graph().serialize(format=format, **kwargs)

    def cleanup(self):
        """Recursively delete the project. Only works
        for remote (i.e. cloned) projects."""
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
    path: str, sources: Optional[Union[Iterable[str], str]] = None
) -> List[str]:
    """Input validation and normalization for metadata sources.
    Returns a list of all input sources.

    Parameters
    ----------
    path :
        The path to the repository, either a local path or a URL.
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

    git_provider = get_git_provider(path)
    if git_provider not in norm:
        norm.append(git_provider)

    if (not validate_url(path)) and any(map(is_remote_source, norm)):
        raise ValueError("Cannot use a remote source with a local project.")
    return norm


def get_extractor(
    path: str, source: str, _id: Optional[str] = None
) -> Extractor:
    """Instantiate the correct extractor for a given source.

    Parameters
    -----------
    path
        Where the repository metadata is extracted from.
    source
        The source of the repository (git, gitlab, github, ...).
    _id
        The identifier to use for the repository. If not provided,
        it will be determined automatically by the extractor
    """
    return SOURCES[source].extractor(path, _id=_id)


def is_valid_source(source: str) -> bool:
    """Check if input is a valid source for gimie."""
    return source in SOURCES


def is_remote_source(source: str) -> bool:
    """Check if input is a valid remote source for gimie."""
    if is_valid_source(source):
        return SOURCES[source].remote
    return False


def is_local_source(source: str) -> bool:
    """Check if input is a valid local source for gimie."""
    return not is_remote_source(source)


def is_git_provider(source: str) -> bool:
    """Check if input is a valid git provider for gimie."""
    if is_valid_source(source):
        return SOURCES[source].git
    return False


def get_git_provider(url: str) -> str:
    """Given a git repository URL, return the corresponding git provider.
    Local path or unsupported git providers will return "git"."""
    # NOTE: We just check if the provider name is in the URL.
    # There may be a more robust way.
    if validate_url(url):
        for name, prov in SOURCES.items():
            if prov.git and prov.remote and name in url:
                return name
    # Fall back to local git if local path of unsupported provider
    return "git"
