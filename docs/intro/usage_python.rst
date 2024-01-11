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
   url = "https://gitlab.com/inkscape/inkscape"
   extractor = GitlabExtractor(url)
   repo = extractor.extract()


Unlike `Project`, extractors only extract data from the git repository without running any parser, and return a `Repository` object.

The `Repository` object can be serialized to RDF or converted to an rdflib graph:

.. code-block:: python

   type(repo)
   # gimie.models.Repository
   repo.name
   # 'inkscape/inkscape'
   repo.prog_langs
   # ['C++', 'C', 'CMake', 'HTML', 'Python']
   repo.serialize(format='json-ld', destination='inkscape.json')
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
   # [b'Inkscape. Draw Freely.\n', b'======================\n']
