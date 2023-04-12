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

"""Sources from which metadata can be extracted by gimie."""
from typing import Type
from gimie.sources.abstract import Extractor
from gimie.sources.github import GithubExtractor
from gimie.sources.gitlab import GitlabExtractor
from gimie.sources.git import GitExtractor

from dataclasses import dataclass


@dataclass
class Source:
    """Source of metadata."""

    remote: bool
    git: bool
    extractor: Type[Extractor]


SOURCES = {
    "git": Source(remote=False, git=True, extractor=GitExtractor),
    "github": Source(remote=True, git=True, extractor=GithubExtractor),
    "gitlab": Source(remote=True, git=True, extractor=GitlabExtractor),
}
