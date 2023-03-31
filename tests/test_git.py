"""Tests for the Gimie command line interface."""

import os
from gimie.sources.git import GitExtractor
import datetime
import pytest

LOCAL_REPOSITORY = os.getcwd()
RENKU_REPOSITORY = "https://github.com/SwissDataScienceCenter/renku"


@pytest.fixture
def local_meta():
    """Return metadata for a local repository."""
    meta = GitExtractor(LOCAL_REPOSITORY)
    meta.extract()
    return meta


def test_git_authors(local_meta):
    """Test part of the authors returned by gimie."""
    contribs = [c.name for c in local_meta.contributors]
    names = [
        "cmdoret",
        "Martin Nathan Tristan Fontanet",
        "rmfranken",
        "sabrinaossey",
    ]
    assert all([n in contribs for n in names])
    assert local_meta.author.name == "Cyril Matthey-Doret"


def test_git_creation_date(local_meta):
    """Test the creation date of a git repository."""
    assert local_meta.date_created.astimezone(
        datetime.timezone.utc
    ) == datetime.datetime(
        2022, 12, 7, 10, 19, 31, tzinfo=datetime.timezone.utc
    )
