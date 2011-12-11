
class EDLAttribute(object):
    pass

class EDLNode(object):
    vspan = None

class Pointer(EDLAttribute):
    docid = None
    start = None
    offset = None

    href = None
    cref = None
    tref = None
    rref = None

    def __init__(self, docid, start, offset, href=None, tref=None):
        self.docid = docid
        self.start = start
        self.offset = offset
        self.href = href
        self.tref = tref

    @property
    def end(self):
        return self.start + self.offset

    def within(self, addr, length):
        return ( addr == self.docid ) \
            and ( self.start < length and self.end < length )

    def after(self, addr, length):
        return ( addr == self.docid ) \
            and ( self.start == length )

class Data(EDLNode):
    data = None
  
    def __init__(self, cid, data):
        assert isinstance(cid, Pointer)
        self.vaddr = cid
        self.data = data


class Link(EDLNode):
    def __init__(self, pfrom, pto, pthree):
        pass

    def __iter__(self):
        yield self.pfrom
        yield self.pto
        yield self.pthree
