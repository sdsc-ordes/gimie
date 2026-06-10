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
from typing import List, Optional

import click
import typer
import yaml

from gimie import __version__
from gimie.converters.publiccode_converter import convert_to_publiccode
from gimie.parsers import get_parser, list_default_parsers, list_parsers
from gimie.project import Project

app = typer.Typer(add_completion=False)


# Used to autogenerate docs with sphinx-click
@click.group()
def cli():
    """Command line group"""
    pass


class RDFFormatChoice(str, Enum):
    ttl = "ttl"
    jsonld = "json-ld"
    nt = "nt"


class OutputFormatChoice(str, Enum):
    rdf = "rdf"
    publiccode = "publiccode"


def version_callback(value: bool):
    if value:
        print(f"gimie {__version__}")
        # Exits successfully
        raise typer.Exit()


@app.command()
def data(
    url: str,
    format: RDFFormatChoice = typer.Option(
        RDFFormatChoice.ttl,
        "--format",
        show_choices=True,
        help="Output serialization format for the RDF graph.",
    ),
    base_url: Optional[str] = typer.Option(
        None,
        "--base-url",
        help="Specify the base URL of the git provider. Inferred by default.",
    ),
    include_parser: Optional[List[str]] = typer.Option(
        None,
        "--include-parser",
        "-I",
        help="Only include selected parser. Use 'gimie parsers' to list parsers.",
    ),
    exclude_parser: Optional[List[str]] = typer.Option(
        None,
        "--exclude-parser",
        "-X",
        help="Exclude selected parser.",
    ),
    to: OutputFormatChoice = typer.Option(
        OutputFormatChoice.rdf,
        "--to",
        show_choices=True,
        help="Output format: 'rdf' for RDF serialization, 'publiccode' for publiccode.yml.",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Display version and exit",
        callback=version_callback,
    ),
):
    """Extract linked metadata from a Git repository at the target URL.

    The output is sent to stdout, and turtle is used as the default serialization format.
    """
    parser_names = list_default_parsers()
    if exclude_parser:
        parser_names -= set([parser for parser in exclude_parser])
    if include_parser:
        parser_names = set([parser for parser in include_parser])
    proj = Project(url, base_url=base_url, parser_names=parser_names)
    repo_meta = proj.extract()

    match to:
        case OutputFormatChoice.publiccode:
            publiccode = convert_to_publiccode(repo_meta)
            output = yaml.dump(publiccode, default_flow_style=False, sort_keys=False)
        case OutputFormatChoice.rdf:
            output = repo_meta.serialize(format=format.value)
        case _:
            raise ValueError(f"Unknown output format: {to}")
    print(output)


@app.command()
def advice(url: str):
    """Show a metadata completion report for a Git repository
    at the target URL.

    NOTE: Not implemented yet"""
    ...
    raise typer.Exit()


@app.command()
def parsers(
    verbose: bool = typer.Option(
        False, "--verbose", help="Show parser description."
    )
):
    """List available parsers, specifying which are default.
    If --verbose is used, show parser description."""
    message = ""
    parsers = list_parsers()
    default_parsers = list_default_parsers()

    for name in parsers:
        # Each parser gets their name in bold green
        title = typer.style(name, fg=typer.colors.GREEN, bold=True)
        default = " (default)" if name in default_parsers else ""
        description = f" - {get_parser(name).__doc__}" if verbose else ""

        parser_line = f"{title}{default}{description}"
        message += f"{parser_line}\n"

    typer.echo(message)


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
