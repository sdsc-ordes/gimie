"""Test the command line interface of gimie"""
from pyshacl import validate
from rdflib import Graph


# TEST_GIT_LOCATIONS = [
#         "https://example.org/git-repo1.git",
#         "https://example.org/git-repo2.git",
#         "https://example.org/git-repo3.git",
#         r"C:\Users\franken\gimie",
# ]
# #do we need 2 different tests here? the output should be the same: Namely whether the extracted metadata is a valid
# #JSON-LD file with the right properties filled in. Whether it is a URL or local filepath does not matter for the test
#
# @pytest.mark.parametrize("location", TEST_GIT_LOCATIONS)
def test_git_output():
    output = "output.ttl"  # will become run_gimie() when functional
    """Returns correct git metadata from target URL."""

    # Input for this test function is the output of the main function i.e. the JSON_LD file.
    Metadatafile = open(output, "r")
    shgraph = open("shaclgraph.ttl", "r")
    g = Graph()
    try:
        g.parse(Metadatafile)
    except:
        raise Exception('Your output file is not a valid linked data serialization')

    s = Graph()
    s.parse(shgraph)
    try:
        validationresult = validate(data_graph=g,
                                    shacl_graph=s,
                                    ont_graph=None,
                                    inference='rdfs',
                                    abort_on_first=False,
                                    allow_infos=False,
                                    allow_warnings=False,
                                    meta_shacl=False,
                                    advanced=False,
                                    js=False,
                                    debug=False)
    except:
        raise Exception("Your file won't validate, something is going wrong in the validate function")
    # for humans
    f = open("shapesoutputhuman.ttl", "w")
    f.write(str(validationresult[2]))
    f.close()
    # for machines (ttl)
    validationreportcomputer = validationresult[1]
    validationreportcomputer.serialize(destination="shapesoutput.ttl", format='turtle')
    if (validationresult[0] == False):
        raise Exception("SHACL report still contains errors, resolve them to continue (see shapesoutput.ttl)")

# JSON LD being valid can be checked with SHACL - A graph that has all the mandatory and optional properties of a
# valid repository can be run against the output. If the validation report does not produce errors, all is well.
# <this should be done using pyShacl, and is part of the test, only if JSON-LD file is valid>


# def test_invalid_url():
#     """Fails gracefully on invalid URL."""
#     invalid_url = "https://github.com/SDSC-ORD/not-exist"
#     ...

# filenames
# should return a flat list of files that is present in the project

# license
# has a license been specified somewhere in the project?


# HTML in webpage
# Is there HTML present at the URL specified? Yes = Pass, No = Fail
