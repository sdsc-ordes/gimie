"""Tests for the Gimie command line interface."""

import os
from gimie.sources.git import GitExtractor
from gimie.project import Project
import datetime
import pytest
from gimie.graph.namespaces import GIMIE

LOCAL_REPOSITORY = os.getcwd()
RENKU_REPOSITORY = "https://github.com/SwissDataScienceCenter/renku"
UNSUPPORTED_PROV = "https://codeberg.org/dnkl/foot"


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
    assert local_meta._id.startswith(GIMIE), "ID should be a Gimie URI"


def test_git_creation_date(local_meta):
    """Test the creation date of a git repository."""
    assert local_meta.date_created.astimezone(
        datetime.timezone.utc
    ) == datetime.datetime(
        2022, 12, 7, 10, 19, 31, tzinfo=datetime.timezone.utc
    )


def test_set_uri():
    meta = GitExtractor(LOCAL_REPOSITORY, _id="https://example.com/test")
    meta.extract()
    assert meta._id == "https://example.com/test"


def test_clone_extract_github():
    """Clone Git repository by setting git extractor
    explicitely and extract metadata locally."""
    meta = Project(RENKU_REPOSITORY, sources="git")


def test_clone_unsupported():
    """Instantiate Project from unsupported provider
    with git as default provider"""
    meta = Project(UNSUPPORTED_PROV)
