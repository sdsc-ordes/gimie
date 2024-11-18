from gimie.io import LocalResource
from gimie.parsers.cff import get_cff_authors


def test_parse_cff():
    cff_file = LocalResource("CITATION.cff")
    with open(cff_file.path, "rb") as f:
        cff_content = f.read()
    authors = get_cff_authors(cff_content)
    assert authors is not None
