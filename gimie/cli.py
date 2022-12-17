"""Command line interface to the gimie package."""
from typing import Optional
from gimie import __version__
import typer

app = typer.Typer(add_completion=False)


def version_callback(value: bool):
    if value:
        print(f"gimie {__version__}")
        # Exits successfully
        raise typer.Exit()


@app.command()
def data(
    path: str,
    skip_license: bool = typer.Option(
        False, "--skip-license", help="Skip license scan."
    ),
    skip_html: bool = typer.Option(
        False, "--skip-html", help="Skip html page scan."
    ),
    skip_git: bool = typer.Option(
        False, "--skip-git", help="Skip git commit scan."
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Display version and exit",
        callback=version_callback,
    ),
):
    """Extract metadata from a Git repository at the target PATH."""
    ...
    raise typer.Exit()


@app.command()
def status(path: str):
    """Show a metadata completion report for a Git repository
    at the target PATH."""
    ...
    raise typer.Exit()


# This callback is triggered when gimie is called without subcommand
@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback
    )
):
    """gimie digs Git repositories for metadata."""


if __name__ == "__main__":
    app()
