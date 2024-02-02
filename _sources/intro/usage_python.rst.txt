Python Usage
************

Gimie can be used as a python library. Either to run the end-to-end extraction process on an input URL, or only a specific extractor.

The end-to-end extraction is performed by ``gimie.Project`` and will automatically detect the git-provider and return directly an `rdflib.Graph` object. After extracting data from the git repository, parsers are executed on the files contents to enrich the graph with additional information.:

.. code-block:: python

   from gimie.project import Project
   url = 'https://github.com/apache/pulsar'
   proj = Project(url)
   g = proj.extract()


A specific extractor can also be used, for example to use with GitLab projects:

.. code-block:: python

   from gimie.extractors import GitlabExtractor
   url = "https://gitlab.com/data-custodian/custodian"
   extractor = GitlabExtractor(url)
   repo = extractor.extract()


Unlike `Project`, extractors only extract data from the git repository without running any parser, and return a `Repository` object.

The `Repository` object can be serialized to RDF or converted to an rdflib graph:

.. code-block:: python

   type(repo)
   # gimie.models.Repository
   repo.name
   # 'data-custodian/custodian'
   repo.prog_langs
   # ['Go', 'Dockerfile', 'Smarty', 'Shell', 'Makefile']
   repo.serialize(format='json-ld', destination='custodian.json')
   g = repo.to_graph()
   type(g)
   # rdflib.graph.Graph

Extractors also have a `list_files()` method which provides handles to a streamable file-like interface for files in the root of the repository.

.. code-block:: python

   handles = extractor.list_files()
   readme_handle = handles[11]
   readme_handle.path
   # PosixPath('README.md')
   readme_handle.open().readlines()[:2]
   # [b'# The Swiss Data Custodian\n', b'\n']


Parsers can also be run manually on the files contents:


.. code-block:: python

   from gimie.parsers import LicenseParser
   parser = LicenseParser()
   license_handle = handles[8]
   license_contents = license_handle.open().read()
   parser.parse(license_contents)
   # {(rdflib.term.URIRef('http://schema.org/license'), rdflib.term.URIRef('https://spdx.org/licenses/AGPL-3.0-only.html'))}


There is also a helper function to run parsers on a list of files,
selecting the correct parser based on file names:

.. code-block:: python

   from gimie.parsers import parse_files
   parse_files(handles)
   # {(rdflib.term.URIRef('http://schema.org/license'), rdflib.term.URIRef('https://spdx.org/licenses/AGPL-3.0-only.html'))}
