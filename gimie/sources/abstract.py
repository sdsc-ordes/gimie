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
"""Abstract classes for gimie objects."""
from abc import ABC, abstractmethod
from typing import List, Optional

from urllib.parse import urlparse

from gimie.io import Resource
from gimie.models import Repository
from gimie.sources.common.license import get_license_url, is_license_path


class Extractor(ABC):
    """Extractor is an Abstract Base Class. It is only meant
    to define a standard interface for all extractors.

    All subclasses must implement extract() and to_graph() methods
    they are free to override the default serialize() and jsonld()
    """

    def __init__(
        self,
        url: str,
        base_url: Optional[str] = None,
        local_path: Optional[str] = None,
    ):
        self.url = url
        self.base_url = base_url
        self.local_path = local_path

    @abstractmethod
    def extract(self) -> Repository:
        """Extract metadata"""
        ...

    def list_files(self) -> List[Resource]:
        """List all files in the repository HEAD."""
        ...

    @property
    def path(self) -> str:
        """Path to the repository without the base URL."""
        if self.base_url is None:
            return urlparse(self.url).path.strip("/")
        return self.url.removeprefix(self.base_url).strip("/")

    @property
    def base(self) -> str:
        """Base URL of the remote."""
        if self.base_url is None:
            url = urlparse(self.url)
            return f"{url.scheme}://{url.netloc}"
        return self.base_url

    def _get_licenses(self) -> List[str]:
        """Extracts SPDX License URLs from the repository."""
        # TODO: Move functionality into a dedicate Parser
        license_files = filter(
            lambda p: is_license_path(p.name), self.list_files()
        )
        license_urls = []
        for file in license_files:
            license_url = get_license_url(file)
            if license_url:
                license_urls.append(license_url)
        return license_urls
