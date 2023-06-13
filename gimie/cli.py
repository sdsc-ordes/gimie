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
from enum import Enum
from typing import Optional
from gimie import __version__
import click
import typer

from gimie.project import Project

app = typer.Typer(add_completion=False)

# Used to autogenerate docs with sphinx-click
@click.group()
def cli():
    """Command line group"""
    pass


class SerializationFormat(str, Enum):
    """Enumeration of valid RDF serialization formats for project graphs"""

    ttl = "ttl"
    jsonld = "json-ld"
    nt = "nt"


def version_callback(value: bool):
    if value:
        print(f"gimie {__version__}")
        # Exits successfully
        raise typer.Exit()


@app.command()
def data(
    url: str,
    format: SerializationFormat = typer.Option(
        "ttl",
        "--format",
        show_choices=True,
        help="Output serialization format for the RDF graph.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Display version and exit",
        callback=version_callback,
    ),
):
    """Extract linked metadata from a Git repository at the target URL.

    The output is sent to stdout, and turtle is used as the default serialization format."""
    proj = Project(url)
    print(proj.serialize(format=format))


@app.command()
def advice(url: str):
    """Show a metadata completion report for a Git repository
    at the target URL.

    NOTE: Not implemented yet"""
    ...
    raise typer.Exit()


typer_cli = typer.main.get_command(app)
cli.add_command(typer_cli, "cli")

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
