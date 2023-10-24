"""Tests for the Gimie command line interface."""

from gimie import cli
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


def test_parsers_help():
    """Checks if the 'gimie parsers --help' command exits successfully."""
    result = runner.invoke(cli.app, ["parsers", "--help"])
    assert result.exit_code == 0
