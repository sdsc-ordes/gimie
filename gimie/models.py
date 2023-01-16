from dataclasses import dataclass, field
import datetime
from typing import Optional, List


@dataclass(order=True)
class Release:
    """
    This class represents a release of a repository.

    Parameters
    ----------
    tag: str
        The tag of the release.
    date: datetime.datetime
        The date of the release.
    commit_hash: str
        The commit hash of the release.
    """

    tag: str = field(compare=False)
    date: datetime.datetime = field(compare=True)
    commit_hash: str = field(compare=False)


@dataclass
class Person:
    first_name: Optional[str] = None


@dataclass
class Organization:
    name: str
    members: Optional[List[Person]] = None
