import unittest

tests = (
            ("/node/", {title:"Docuverse I", data:"Whoo haa"}),
            ("/node/1/fetch", None, "Whoo haa", False),
            ("/node/", {title:"Docuverse II"}, "", False),
            ("/node/", {title:"Docuverse III"}, "", False),
            ("/node/", {title:"Docuverse IV"}, "", False),
            ("/node/4/fetch", None, ""),
            ("/node/", {title:"Docuverse I", data:"Node I"}),
        )


def _tester(url, data, response
testcases = [
    unittest.FunctionTestCase(_tester(*t),
        description='SGMLScraper_%u' % tests.index(t)) 
    for t in tests]

Tests = unittest.
