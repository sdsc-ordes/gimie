from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from gimie.sources.local import GitExtractor
from gimie.sources.remote import (
    GithubExtractor,
    GitlabExtractor,
)
from rdflib import Graph

REMOTE_SOURCES: Dict[str, Any] = {
    "gitlab": GitlabExtractor,
    "github": GithubExtractor,
}
LOCAL_SOURCES: Dict[str, Any] = {
    "git": GitExtractor,
}

SOURCES: Dict[str, Any] = LOCAL_SOURCES | REMOTE_SOURCES
