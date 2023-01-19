# Gimie

Gimie (GIt Meta Information Extractor) is a python library and command line tool to extract structured metadata from git repositories.

:warning: Gimie is at an early development stage. It is not yet functional.

## Context
Scientific code repositories contain valuable metadata which can be used to enrich existing catalogues, platforms or databases. This tool aims to easily extract structured metadata from a generic git repositories. The following sources of information are used:

* [ ] Git metadata
* [ ] Filenames
* [ ] License
* [ ] Freetext content in README and other files

## Installation

To install the dev version from github:

```shell
pip install git+https://github.com/SDSC-ORD/gimie.git#egg=gimie
```

## Usage

As a command line tool:
```shell
gimie https://github.com/numpy/numpy
```
As a python library:

```python
import gimie
repo = gimie.Repo("https://github.com/numpy/nump)
```

## Outputs

The default output is JSON-ld, a JSON serialization of the [RDF](https://en.wikipedia.org/wiki/Resource_Description_Framework) data model. We follow the schema recommended by [codemeta](https://codemeta.github.io/).

## Contributing

All contributions are welcome. New functions and classes should have associated tests and docstrings following the [numpy style guide](https://numpydoc.readthedocs.io/en/latest/format.html).

The code formatting standard we use is [black](https://github.com/psf/black), with `--line-length=79` to follow [PEP8](https://peps.python.org/pep-0008/) recommendations. We use [pytest](https://docs.pytest.org/en/7.2.x/) as our testing framework. This project uses [pyproject.toml](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/) to define package information, requirements and tooling configuration.

For local development, you can clone the repository and install the package in editable mode, either using [pip](https://pip.pypa.io/en/stable/):

```shell
git clone https://github.com/SDSC-ORD/gimie && cd gimie
pip install -e .
```
Or [poetry](https://python-poetry.org/), to work in an isolated virtual environment:
```shell
git clone https://github.com/SDSC-ORD/gimie && cd gimie
poetry install
```

## Releases and Publishing on Pypi

Releases are done via github release

- a release will trigger a github workflow to publish the package on Pypi
- Make sure to update to a new version in `pyproject.toml` before making the release
- It is possible to test the publishing on Pypi.test by running a manual workflow: go to github actions and run the Workflow: 'Publish on Pypi Test'
