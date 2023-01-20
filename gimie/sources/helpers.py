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
from gimie.sources import (
    LOCAL_SOURCES,
    REMOTE_SOURCES,
    SOURCES,
)

from gimie.sources.abstract import Extractor


def get_local_extractor(path: str, source: str) -> Extractor:
    return LOCAL_SOURCES[source](path)


def get_remote_extractor(path: str, source: str) -> Extractor:
    return REMOTE_SOURCES[source](path)


def get_extractor(path: str, source: str) -> Extractor:
    return SOURCES[source](path)


def is_local_source(source: str) -> bool:
    return source in LOCAL_SOURCES


def is_remote_source(source: str) -> bool:
    return source in REMOTE_SOURCES


def is_valid_source(source: str) -> bool:
    return source in SOURCES
