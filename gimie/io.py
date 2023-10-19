"""Standard input interfaces to local or remote resources for gimie."""

import io
import os
from pathlib import Path
import requests
from typing import BinaryIO, Iterator, Optional, Union


class Resource:
    """Abstract class for buffered read-only access to local or remote resources via
    a file-like interface.

    Parameters
    ----------
    name:
        The name of the resource, typically the filename.
    """

    name: str

    def open(self) -> BinaryIO:
        raise NotImplementedError


class LocalResource(Resource):
    """Providing buffered read-only access to local data.

    Examples
    --------
    >>> from gimie.io import LocalResource
    >>> resource = LocalResource("README.md")
    """

    def __init__(self, path: Union[str, os.PathLike]):
        self.path: Path = Path(path)

    def open(self, mode="r") -> Union[BinaryIO, io.RawIOBase]:
        return io.FileIO(self.path, mode)

    @property
    def name(self) -> str:
        return self.path.name


class RemoteResource(Resource):
    """Provides buffered read-only access to remote data.

    Parameters
    ----------
    url:
        The URL where the resource. can be downladed from.
    headers:
        Optional headers to pass to the request.

    Examples
    --------
    >>> from gimie.io import RemoteResource
    >>> url = "https://raw.githubusercontent.com/SDSC-ORD/gimie/main/README.md"
    >>> resource = RemoteResource("README.md", url)
    """

    def __init__(self, name: str, url: str, headers: Optional[dict] = None):
        self.name = name
        self.url = url
        self.headers = headers or {}

    def open(self) -> io.RawIOBase:
        resp = requests.get(
            self.url, headers=self.headers, stream=True
        ).iter_content(chunk_size=128)
        return IterStream(resp)


class IterStream(io.RawIOBase):
    """Wraps an iterator to make it look like a file-like object.

    Parameters
    ----------
    iterator:
        An iterator that yields bytes.

    Examples
    --------
    >>> from gimie.io import IterStream
    >>> stream = IterStream(iter([b"Hello ", b"World"]))
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
            chunk = self.leftover or next(self.iterator)
            output, self.leftover = chunk[:l], chunk[l:]
            b[: len(output)] = output
            return len(output)
        except StopIteration:
            return 0  # indicate EOF
