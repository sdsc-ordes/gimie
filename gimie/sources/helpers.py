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
"""Helper functions to check sources and access extractors."""
from typing import Optional

from gimie.sources import SOURCES
from gimie.sources.abstract import Extractor
from gimie.utils import validate_url


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
    return SOURCES[source].extractor(path)


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
