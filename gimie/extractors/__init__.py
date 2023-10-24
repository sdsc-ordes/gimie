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
from typing import Dict, Type
from gimie.extractors.abstract import Extractor
from gimie.extractors.github import GithubExtractor
from gimie.extractors.gitlab import GitlabExtractor
from gimie.extractors.git import GitExtractor

GIT_PROVIDERS: Dict[str, Type[Extractor]] = {
    "git": GitExtractor,
    "github": GithubExtractor,
    "gitlab": GitlabExtractor,
}
