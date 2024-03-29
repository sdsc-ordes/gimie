"""Tests for the Gimie command line interface."""

import os
import datetime

import pytest

from gimie.io import LocalResource
from gimie.extractors.git import GitExtractor
from gimie.project import Project

LOCAL_REPOSITORY = os.getcwd()
RENKU_GITHUB = "https://github.com/SwissDataScienceCenter/renku"
UNSUPPORTED_PROV = "https://codeberg.org/dnkl/foot"


@pytest.fixture
def local_meta():
    """Return metadata for a local repository."""
    extractor = GitExtractor(
        "https://github.com/sdsc-ordes/gimie", local_path=LOCAL_REPOSITORY
    )
    return extractor.extract()


def test_git_authors(local_meta):
    """Test part of the authors returned by gimie."""
    contribs = [c.name for c in local_meta.contributors]
    author = local_meta.authors[0]
    names = [
        "cmdoret",
        "Martin Nathan Tristan Fontanet",
        "rmfranken",
        "sabrinaossey",
    ]
    assert all([n in contribs for n in names])
    assert author.name == "Cyril Matthey-Doret"


def test_git_creation_date(local_meta):
    """Test the creation date of a git repository."""
    assert local_meta.date_created.astimezone(
        datetime.timezone.utc
    ) == datetime.datetime(
        2022, 12, 7, 10, 19, 31, tzinfo=datetime.timezone.utc
    )


def test_set_uri():
    meta = GitExtractor(
        "https://example.com/test", local_path=LOCAL_REPOSITORY
    ).extract()
    assert meta._id == "https://example.com/test"


def test_clone_extract_github():
    """Clone Git repository by setting git extractor
    explicitely and extract metadata locally."""
    proj = Project(RENKU_GITHUB, git_provider="git")
    assert type(proj.extractor) == GitExtractor
    proj.extract()


def test_clone_unsupported():
    """Instantiate Project from unsupported provider
    with git as default provider"""
    proj = Project(UNSUPPORTED_PROV)
    assert type(proj.extractor) == GitExtractor
    proj.extract()


def test_git_list_files():
    files = GitExtractor(UNSUPPORTED_PROV).list_files()
    assert all(isinstance(f, LocalResource) for f in files)
