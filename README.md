# extrameta

A python library and command line tool to extract structured metadata from git repositories.

## Context
Scientific code repositories contain valuable metadata which can be used to enrich existing catalogues, platforms or databases. This tool aims to easily extract structured metadata from a generic git repositories. The following sources of information will be used:

* [ ] Git metadata
* [ ] Filenames
* [ ] License
* [ ] HTML in web page
* [ ] Freetext content in README

## Outputs

The default output is JSON-ld, a JSON serialization of the [RDF](https://en.wikipedia.org/wiki/Resource_Description_Framework) data model.
