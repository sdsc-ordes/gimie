"""Tests for the Gimie command line interface."""

import os
from gimie.sources.git import GitMetadata
import datetime
import pytest

LOCAL_REPOSITORY = os.getcwd()


def test_git_authors():
    """Test part of the authors returned by gimie."""
    git_metadata = GitMetadata(LOCAL_REPOSITORY)
    assert "Cyril Matthey-Doret" in git_metadata.authors
    assert "sabrinaossey" in git_metadata.authors
    assert "Martin Nathan Tristan Fontanet" in git_metadata.authors
    assert "rmfranken" in git_metadata.authors
    assert "cmdoret" in git_metadata.authors


def test_git_creation_date():
    """Test the creation date of a git repository."""
    git_metadata = GitMetadata(LOCAL_REPOSITORY)
    assert git_metadata.creation_date.astimezone(
        datetime.timezone.utc
    ) == datetime.datetime(
        2022, 12, 7, 10, 19, 31, tzinfo=datetime.timezone.utc
    )


def test_git_creator():
    """Test the creator of a git repository."""
    git_metadata = GitMetadata(LOCAL_REPOSITORY)
    assert git_metadata.creator == "Cyril Matthey-Doret"


def test_git_releases():
    """Test the first release of a git repository."""
    git_metadata = GitMetadata(RENKU_REPOSITORY)
    first_release = git_metadata.releases[0]
    assert first_release.tag == "maint-0.1"
    assert first_release.date.astimezone(
        datetime.timezone.utc
    ) == datetime.datetime(
        2018, 2, 16, 20, 40, 10, tzinfo=datetime.timezone.utc
    )
    assert (
        first_release.commit_hash == "615132e9c0c0e6e139f566c4066a17af93651b55"
    )
