"""Tests for the Gimie command line interface."""

from gimie import cli
from typer.testing import CliRunner

runner = CliRunner()


def test_data():
    """Checks if the 'gimie data' command runs."""
    result = runner.invoke(cli.app, ["data", "help"])
    assert result.exit_code == 0


def test_status():
    """Checks if the 'gimie status' command runs."""
    result = runner.invoke(cli.app, ["status", "help"])
    assert result.exit_code == 0
