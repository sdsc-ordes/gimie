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
"""Standard input interfaces to local or remote resources for gimie."""

import io
import os
from pathlib import Path
import requests
from typing import Iterator, Optional, Union


class Resource:
    """Abstract class for read-only access to local or remote resources via
    a file-like interface.

    Parameters
    ----------
    path:
        The local relative path to the resource.
    """

    path: Path

    def open(self) -> io.RawIOBase:
        raise NotImplementedError


class LocalResource(Resource):
    """Providing read-only access to local data via a file-like interface.

    Examples
    --------
    >>> resource = LocalResource("README.md")
    """

    def __init__(self, path: Union[str, os.PathLike]):
        self.path: Path = Path(path)

    def open(self) -> io.RawIOBase:
        return io.FileIO(self.path, mode="r")


class RemoteResource(Resource):
    """Provides read-only access to remote data via a file-like interface.

    Parameters
    ----------
    url:
        The URL where the resource. can be downladed from.
    headers:
        Optional headers to pass to the request.

    Examples
    --------
    >>> url = "https://raw.githubusercontent.com/sdsc-ordes/gimie/main/README.md"
    >>> content = RemoteResource("README.md", url).open().read()
    >>> assert isinstance(content, bytes)
    """

    def __init__(self, path: str, url: str, headers: Optional[dict] = None):
        self.path = Path(path)
        self.url = url
        self.headers = headers or {}

    def open(self) -> io.RawIOBase:
        resp = requests.get(
            self.url, headers=self.headers, stream=True
        ).iter_content(chunk_size=128)
        return IterStream(resp)


class IterStream(io.RawIOBase):
    """Wraps an iterator under a like a file-like interface.
    Empty elements in the iterator are ignored.

    Parameters
    ----------
    iterator:
        An iterator yielding bytes.

    Examples
    --------
    >>> stream = IterStream(iter([b"Hello ", b"", b"World"]))
    >>> stream.read()
    b'Hello World'
    """

    def __init__(self, iterator: Iterator[bytes]):
        self.leftover = b""
        self.iterator = iterator

    def readable(self):
        return True

    def readinto(self, b):
        try:
            l = len(b)  # We're supposed to return at most this much
            while True:
                chunk = self.leftover or next(self.iterator)
                # skip empty elements
                if not chunk:
                    continue
                output, self.leftover = chunk[:l], chunk[l:]
                b[: len(output)] = output
                return len(output)
        except StopIteration:
            return 0  # indicate EOF
