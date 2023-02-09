# Gimie

[![PyPI version](https://badge.fury.io/py/gimie.svg)](https://badge.fury.io/py/gimie) [![Python Poetry Test](https://github.com/SDSC-ORD/gimie/actions/workflows/poetry-pytest.yml/badge.svg)](https://github.com/SDSC-ORD/gimie/actions/workflows/poetry-pytest.yml)

Gimie (GIt Meta Information Extractor) is a python library and command line tool to extract structured metadata from git repositories.

:warning: Gimie is at an early development stage. It is not yet functional.

## Context
Scientific code repositories contain valuable metadata which can be used to enrich existing catalogues, platforms or databases. This tool aims to easily extract structured metadata from a generic git repositories. The following sources of information are used:

* [x] Github API
* [ ] Gitlab API
* [ ] Local Git metadata
* [ ] License text
* [ ] Free text in README
* [ ] Renku project metadata

## Installation

To install the stable version on PyPI:

```shell
pip install gimie
```

To install the dev version from github:

```shell
pip install git+https://github.com/SDSC-ORD/gimie.git@main#egg=gimie
```

Gimie is also available as a docker container hosted on the [Github container registry](https://github.com/SDSC-ORD/gimie/pkgs/container/gimie):

```shell
docker pull ghcr.io/sdsc-ord/gimie:latest

# The access token can be provided as an environment variable
docker run -e ACCESS_TOKEN=$ACCESS_TOKEN ghcr.io/sdsc-ord/gimie:latest gimie data <repo>
```


### For development:

activate a conda or virtual environment with Python 3.8 or higher

```shell
git clone https://github.com/SDSC-ORD/gimie && cd gimie
make install
```

run tests:

```shell
make test
```

run checks:

```shell
make check
```

## Usage

### Set your github credentials

In order to avoid rate limits with the github api, you need to provide your github
username and a github token: see
[here ](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
on how to generate a github token.

There are 2 options for setting up your github token in your local environment:

**Option 1:**

```
cp .env.dist .env
```

And then edit the `.env` file and put your github token in.

**Option 2:**

Add your github token in your terminal:

```bash
export ACCESS_TOKEN=
```

After the github token has been added, you can run the command without running into an github api limit.
Otherwise you can still run the command, but might hit that limit after running the command several times.

### Run the command

As a command line tool:
```shell
gimie data https://github.com/numpy/numpy
```
As a python library:

```python
from gimie.project import Project
proj = Project("https://github.com/numpy/numpy)

# To retrieve the rdflib.Graph object
g = proj.to_graph()

# To retrieve the serialized graph
proj.serialize(format='ttl')
```

Or to extract only from a specific source:
```python
from gimie.sources.remote import GithubExtractor
gh = GithubExtractor('https://github.com/SDSC-ORD/gimie')
gh.extract()

# To retrieve the rdflib.Graph object
g = gh.to_graph()

# To retrieve the serialized graph
gh.serialize(format='ttl')
```

## Outputs

The default output is JSON-ld, a JSON serialization of the [RDF](https://en.wikipedia.org/wiki/Resource_Description_Framework) data model. We follow the schema recommended by [codemeta](https://codemeta.github.io/).
Supported formats are json-ld, turtle and n-triples.

## Contributing

All contributions are welcome. New functions and classes should have associated tests and docstrings following the [numpy style guide](https://numpydoc.readthedocs.io/en/latest/format.html).

The code formatting standard we use is [black](https://github.com/psf/black), with `--line-length=79` to follow [PEP8](https://peps.python.org/pep-0008/) recommendations. We use [pytest](https://docs.pytest.org/en/7.2.x/) as our testing framework. This project uses [pyproject.toml](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/) to define package information, requirements and tooling configuration.

## Releases and Publishing on Pypi

Releases are done via github release

- a release will trigger a github workflow to publish the package on Pypi
- Make sure to update to a new version in `pyproject.toml` before making the release
- It is possible to test the publishing on Pypi.test by running a manual workflow: go to github actions and run the Workflow: 'Publish on Pypi Test'
