# Gimie
# Copyright 2022 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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


@app.command()
def advice(path: str):
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
