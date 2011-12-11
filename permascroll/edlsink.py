


class EDLSink(object):

    """
    Commit links and content from EDL stream to storage.
    """

    def __init__(self, resolver, storage):
        self.resolver = resolver
        self.storage = storage

    def reset(self):
        self.content = []
        self.links = []

    @property
    def data(self):
        return ''.join(self.content)

    def apply(self, address, edlstream):
        " Commit or raise. "
        if self.storage.exists(address):
            raise "Document Exists"

        for obj in edlstream:
            if isinstance(obj, Data):
                self.prepare_data(address, obj)

        for obj in edlstream:
            if isinstance(obj, Link):
                self.prepare_link(address, obj)

        self.commit(address)
        self.reset()

    def prepare_data(self, this, obj):
        assert obj.vspan.docid == this
        assert obj.vspan.position == len(self.data)
        if not obj.data:
            assert obj.cid
            obj.data = self.resolver.resolve(obj.cid)
        assert obj.data
        assert obj.vspan.offset == len(obj.data)
        self.content.append(obj)

    def prepare_link(self, this, obj):
        assert obj.vspan.docid == this
        assert obj.vspan.position == len(this.links)
        assert obj.vspan.offset == 1
        for endset in obj:
            self._assert_ptr(this, endset)
        self.links.append(obj)

    def commit(self, address):
        self.storage.create(address)
        for obj in self.content:
            assert self.storage.append(address, obj.data) == obj.cid
        for obj in self.links:
            assert self.storage.link(address, *link) == obj.
        self.storage.close(address)


    def _assert_ptr(self, this, ptr):
        """
        Any pointer from the stream must either deref. existing or newly
        provided content.
        """
        if this == ptr.docid:
            assert ptr.within( this, len(self.data) )
        else:
            doc = self.resolver.fetch(ptr.docid)
            assert ptr.within( doc.address, doc.length )

