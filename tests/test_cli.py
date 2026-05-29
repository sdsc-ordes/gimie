"""Tests for the Gimie command line interface."""

from unittest.mock import patch

from gimie import cli
from gimie.extractors.github import GithubExtractor
from gimie.models import Repository
from typer.testing import CliRunner

runner = CliRunner()


def test_data_help():
    """Checks if the 'gimie data --help' command exits successfully."""
    result = runner.invoke(cli.app, ["data", "--help"])
    assert result.exit_code == 0


def test_advice_help():
    """Checks if the 'gimie advice --help' command exits successfully."""
    result = runner.invoke(cli.app, ["advice", "--help"])
    assert result.exit_code == 0


def test_advice_rejects_non_github():
    result = runner.invoke(cli.app, ["advice", "https://gitlab.com/foo/bar"])
    assert result.exit_code == 1
    assert "GitHub" in result.output


@patch.object(GithubExtractor, "extract")
def test_advice_prints_pr_author_counts(mock_extract):
    mock_extract.return_value = Repository(
        url="https://github.com/o/r",
        name="o/r",
        distinct_pr_authors=3,
        distinct_non_maintainer_pr_authors=2,
    )

    result = runner.invoke(cli.app, ["advice", "https://github.com/o/r"])

    assert result.exit_code == 0
    assert '"distinct_pr_authors": 3' in result.output
    assert '"distinct_non_maintainer_pr_authors": 2' in result.output


def test_parsers_help():
    """Checks if the 'gimie parsers --help' command exits successfully."""
    result = runner.invoke(cli.app, ["parsers", "--help"])
    assert result.exit_code == 0
