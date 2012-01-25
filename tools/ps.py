"""
Simple frontend for Permascroll REST API. Maintain:

- Hierarchical node structure
- Append-only documents
"""
import os
import optparse
import sys
import urllib2


class RESTClient(object):

    def __init__(self, base_url):
        self.opener = urllib2.build_opener(urllib2.HTTPHandler)
        self.base_url = base_url

    def fetch(self, path='/', data={}):
        request = urllib2.Request(self.base_url + path)
        rfl = self.opener.open(request)
        data = rfl.read()
        return data

    def put(self, path='/', data=""):
        request = urllib2.Request(self.base_url + path, data=data)
        #request.add_header('Content-Type', 'your/contenttype')
        request.get_method = lambda: 'PUT'
        self.opener.open(request)

class Permascroll(object):
    def __init__(self, server):
        url = "http://%s" % server
        self.client = RESTClient(url)
    def deref(self, node):
        print "# Node: %s" % node
        print self.client.fetch("/node/%s" % node, headers={'Accept':'text/plain'})
    def get(self, node):
        print "# Node: %s" % node
        print self.client.fetch("/node/%s" % node)
    def touch(self, node, title=None):
        pass
    def append(self, entry, data):
        pass
    def insert(self, entry, data):
        pass
    def link(self, entry, v1, v2, v3):
        pass

    def main(self):
        print sys.argv
        self.get("1")
        self.get("1.1")
        self.get("1.1/1")
        self.get("1.1/2.1/1")
        self.get("1.1/1/1")
        self.get("1.1/1/2")

if __name__ == '__main__':
    Permascroll("localhost:8083").main()
