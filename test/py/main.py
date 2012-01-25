import time, sys
import subprocess
import unittest

#GAE_DIR = '/src/google-appengine/latest/google/appengine/tools/'
#sys.path.insert(0, GAE_DIR)
#import dev_appserver_main
#dev_appserver_main.main()

def gather_unittests():
    return []

def gather_systemtests():
    import restapi
    for testcase in (
                restapi.Tests
            ):
        tests.append(unittest.TestLoader().loadTestsFromTestCase(testcase))
    return []


def main():

    """
    Run all tests.
    """

    testsuite = unittest.TestSuite(
            gather_unittests() + 
            gather_systemtests()
        )


if __name__ == '__main__':
    import sys
    main()

