from gimie.sources import (
    LOCAL_SOURCES,
    REMOTE_SOURCES,
    SOURCES,
)

from gimie.abstract import Extractor


def get_local_extractor(path: str, source: str) -> Extractor:
    return LOCAL_SOURCES[source](path=path)


def get_remote_extractor(path: str, source: str) -> Extractor:
    return REMOTE_SOURCES[source](path=path)


def is_local_source(source: str) -> bool:
    return source in LOCAL_SOURCES


def is_remote_source(source: str) -> bool:
    return source in REMOTE_SOURCES


def is_valid_source(source: str) -> bool:
    return source in SOURCES
