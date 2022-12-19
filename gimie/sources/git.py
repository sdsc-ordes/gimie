from typing import Tuple, Optional
from dataclasses import dataclass, field
from pydriller import Repository
import datetime


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
    creator: Optional[str] = field(init=False)
    repository: Repository
    releases: Tuple[Release] = field(default_factory=tuple, init=False)

    def __init__(self, path: str):
        self.repository = Repository(path)

        self.authors = self.get_authors()
        self.creation_date = self.get_creation_date()
        self.releases = sorted(self.get_releases())
        self.creator = self.get_repo_creator()

    def get_authors(self) -> Tuple[str]:
        """Get the authors of the repository."""
        return tuple(set(commit.author.name for commit in self.repository.traverse_commits()))

    def get_creation_date(self) -> Optional[datetime.datetime]:
        """Get the creation date of the repository."""
        try:
            return next(self.repository.traverse_commits()).author_date
        except StopIteration:
            return None

    def get_releases(self) -> Tuple[Release]:
        """Get the releases of the repository."""
        try:
            return tuple(Release(tag=tag.name, date=tag.commit.authored_datetime, commit_hash=tag.commit.hexsha) for tag in self.repository.git.repo.tags)
        except StopIteration:
            return None

    def get_repo_creator(self) -> Optional[str]:
        """Get the creator of the repository."""
        try:
            return next(self.repository.traverse_commits()).author.name
        except StopIteration:
            return None
