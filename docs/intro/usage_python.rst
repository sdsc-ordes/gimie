Python Usage
************

Gimie can be used as a python library. Either to run the end-to-end extraction process on an input URL, or only a specific extractor.

The end-to-end extraction is performed by ``gimie.Project`` and will automatically detect the git-provider:

.. code-block:: python

   from gimie.project import Project
   url = 'https://github.com/foo/bar'
   proj = Project(url)


A specific extractor can also be used, for example to use with GitLab projects:

.. code-block:: python

   from gimie.sources.gitlab import GitlabExtractor
   url = "https://gitlab.com/foo/bar"
   extractor = GitlabExtractor(url)
   extractor.extract()


Once a project's metadata has been extracted, it can be stored as an rdflib graph, or serialized to RDF triples:

.. code-block:: python

   import rdflib
   graph: rdflib.Graph = proj.to_graph()

   # serialize project directly as an RDF file
   proj.serialize(format='json-ld', destination='foobar.json')


Extractors also support the ``to_graph()`` and ``serialize()`` methods.
