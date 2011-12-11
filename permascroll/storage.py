from permascroll import api
from permascroll.exception import NotFound
from permascroll.model import Entry


class DocumentStore(object):

    def __init__(self):
        self.session = {}

    def exists(self, docid):
        try:
            doc = api.get(docid)
        except NotFound, e:
            return False
        return isinstance(doc, Entry)

    def open(self, docid):
        doc = api.get(docid)
        assert isinstance(doc, Entry)
        self.session[docid] = doc
        return doc

    def create(self, docid):
        assert not self.exists(docid)
        parentid = docid.parent # XXX
        doc = api.create(parentid, kind='entry')
        assert doc.tumbler == docid, "epic fail"
        self.session[docid] = doc
        return doc

    def append(self, docid, data):
        doc = self.session[docid]
        vspan = doc.add_vstream(data)
        return doc.vspan

    def link(self, docid, pfrom, pto, pthree):
        doc = self.session[docid]
        vspan = doc.add_vstream((pfrom, pto, pthree))
        return vspan

    def set(self, docid, **meta):
        pass

    def close(self, docid):
        #self.session[docid].put()
        del self.session[docid]
