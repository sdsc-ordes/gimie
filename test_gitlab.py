from gimie.sources.gitlab import GitlabExtractor


gh = GitlabExtractor('https://gitlab.com/inkscape/extensions')
gh.extract()


# To retrieve the rdflib.Graph object
g = gh.to_graph()

# To retrieve the serialized graph
serial = gh.serialize(format='ttl')
print(serial)

