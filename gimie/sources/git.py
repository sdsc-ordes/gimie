from typing import Tuple, Optional
from dataclasses import field
import datetime
import pydriller


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
    repository: pydriller.Repository

    def __init__(self, path: str):
        self.repository = pydriller.Repository(path)

        self.authors = self.get_authors()
        self.creation_date = self.get_creation_date()

    def get_authors(self) -> Tuple[str]:
        """Get the authors of the repository."""
        return tuple(set(commit.author.name for commit in self.repository.traverse_commits()))

    def get_creation_date(self) -> Optional[datetime.datetime]:
        """Get the creation date of the repository."""
        try:
            return next(self.repository.traverse_commits()).author_date
        except StopIteration:
            return None
