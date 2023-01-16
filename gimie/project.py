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
from typing import Iterable, List, Union
from gimie.utils import validate_url
from gimie.sources.utils import (
    get_local_extractor,
    get_remote_extractor,
    is_local_source,
    is_remote_source,
    is_valid_source,
    Extractor,
)


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
    >>> proj = Project("https://github.com/SDSC-ORD/gimie", sources=['git'])
    Traceback (most recent call last):
    ...
    NotImplementedError
    """

    def __init__(
        self, path: str, sources: Iterable[str] = ["git", "gitlab", "github"]
    ):

        # We want to temporarily clone remote projects (i.e. cleanup behind)
        if validate_url(path):
            self.url = path
            self.project_dir = self.clone(path)
            self._remote = True
        else:
            self.url = None
            self.project_dir = path

        self.extractors = self.get_extractors(sources)

    def clone(self, url: str) -> str:
        raise NotImplementedError

    def get_extractors(self, sources: Iterable[str]) -> List[Extractor]:

        extractors: List[Any] = []
        for src in sources:
            if not is_valid_source(src):
                raise ValueError("Invalid source: {src}.")

            if is_remote_source(src) and not self._remote:
                raise ValueError(
                    "Cannot use a remote source with a local project."
                )
            if is_remote_source(src):
                extractor = get_remote_extractor(self.url, src)
            else:
                extractor = get_local_extractor(self.project_dir, src)
            extractors.append(extractor)

        return extractors

    def cleanup(self):
        ...
