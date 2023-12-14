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

"""Git providers from which metadata can be extracted by gimie."""
from typing import Dict, Optional, Type
from gimie.extractors.abstract import Extractor
from gimie.extractors.github import GithubExtractor
from gimie.extractors.gitlab import GitlabExtractor
from gimie.extractors.git import GitExtractor
from gimie.utils.uri import validate_url

GIT_PROVIDERS: Dict[str, Type[Extractor]] = {
    "git": GitExtractor,
    "github": GithubExtractor,
    "gitlab": GitlabExtractor,
}


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
        repository is located.

    Examples
    --------
    >>> extractor = get_extractor(
    ...     "https://github.com/sdsc-ordes/gimie",
    ...     "github"
    ... )
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


def infer_git_provider(url: str) -> str:
    """Given a git repository URL, return the corresponding git provider.
    Local path or unsupported git providers will return "git".

    Examples
    --------
    >>> infer_git_provider("https://gitlab.com/foo/bar")
    'gitlab'
    >>> infer_git_provider("/foo/bar")
    'git'
    >>> infer_git_provider("https://codeberg.org/dnkl/foot")
    'git'
    """
    # Fall back to git if local path
    if not validate_url(url):
        return "git"

    # NOTE: We just check if the provider name is in the URL.
    # We may want to use a more robust check.
    for name in GIT_PROVIDERS.keys():
        if name in url and name != "git":
            return name

    # Fall back to git for unsupported providers
    return "git"
