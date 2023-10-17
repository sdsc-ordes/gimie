"""Standard input interfaces to local or remote resources for gimie."""

import io
import os
from pathlib import Path
import requests
from typing import Optional, Union


class Resource:
    """Abstract class for buffered read-only access to local or remote resources via
    a file-like interface."""

    name: str

    def open(self) -> io.BufferedReader:
        raise NotImplementedError


class LocalResource(Resource):
    """Providing buffered read-only access to local data.

    Parameters
    ----------
    name: the name of the resource, typically the filename.
    url: the URL where the resource. can be downladed from.
    headers: optional headers to pass to the request.

    Examples
    --------
    >>> from gimie.io import LocalResource
    >>> resource = LocalResource("README.md")
    """

    def __init__(self, path: Union[str, os.PathLike]):
        self.path: Path = Path(path)

    def open(self, mode="r") -> io.BufferedReader:
        return io.BufferedReader(io.FileIO(self.path, mode))

    @property
    def name(self) -> str:
        return self.path.name


class RemoteResource(Resource):
    """Provides buffered read-only access to remote data.

    Parameters
    ----------
    name: the name of the resource, typically the filename.
    url: the URL where the resource. can be downladed from.
    headers: optional headers to pass to the request.

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

    def open(self) -> io.BufferedReader:
        resp = requests.get(
            self.url, headers=self.headers, stream=True
        ).iter_content(chunk_size=128)
        return iterable_to_stream(resp)


def iterable_to_stream(
    iterable, buffer_size=io.DEFAULT_BUFFER_SIZE
) -> io.BufferedReader:
    """
    Converts an iterable yielding bytestrings to a read-only input stream.
    Lets you use an iterable (e.g. a generator) that yields bytestrings as a read-only
    input stream.

    The stream implements Python 3's newer I/O API (available in Python 2's io module).
    For efficiency, the stream is buffered.

    credits: https://stackoverflow.com/a/20260030/8440675
    """

    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = ""

        def readable(self):
            return True

        def readinto(self, b):
            try:
                l = len(b)  # We're supposed to return at most this much
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:l], chunk[l:]
                b[: len(output)] = output
                return len(output)
            except StopIteration:
                return 0  # indicate EOF

    return io.BufferedReader(IterStream(), buffer_size=buffer_size)
