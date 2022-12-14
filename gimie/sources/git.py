from typing import Tuple, Optional
from dataclasses import field
import datetime


class GitMetadata:
    """
    This class is responsible for extracting metadata from a git repository.

    Parameters
    ----------
    path: str
        The path to the git repository.

    Attributes
    ----------
    authors: Tuple[str]
        The authors of the repository.
    creation_date
        The creation date of the repository.
    """

    authors: Tuple[str] = field(default_factory=tuple, init=False)
    creation_date: Optional[datetime.datetime] = field(init=False)

    def __init__(self, path: str):
        raise NotImplementedError
