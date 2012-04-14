"""
This is the data or storage API, see server_handler for HTTP service endpoints.
"""

import logging
from permascroll import rc
from permascroll.util import list_q
from permascroll.model import *
from permascroll.exception import *


from xu88 import Tumbler, Address, Offset


logger = logging.getLogger(__name__)


def get(addr):
    """
    Dereference tumbler and return Node, Directory, Entry 
    (depending on component count) or raise NotFound.
    """
    docuverse = get_root()
    if not addr:
        return docuverse

    else:
        kind = Node
        tccnt = addr.digits.count(0)+1 # XXX
        if tccnt == 2: kind = Directory
        elif tccnt == 3: kind = Entry

        logging.info("Retrieving %s", addr)
        node = kind.get_by_key_name(str(addr))

        if not node:
            raise NotFound, (kind, addr)

        return node

def fetch(addr):
    """
    Like `get` but return None instead of raising NotFound.
    """
    try:
        return get(addr)
    except NotFound, e:
        return None

def find_content(checksum):
    """
    Retrieve data by checksum key.
    """
    return LiteralContent.get_by_key_name(checksum)

def find_entries(checksum):
    """
    Find Entry records that contain data of this checksum key.
    """
    e = Entry.gql("WHERE content = :1", db.Key.from_path('LiteralContent',checksum)).fetch(100)
    return e

def get_root():
    """
    The root has no address but keeps track of Ur-digits--it counts docuverses. 
    """
    base = Docuverse.all().get()
    if not base:
        base = Docuverse(key_name='docuverse', length=0)
        base.put()
    return base

def new_root(**props):
    "Create new docuverse within current root (%s). " %  rc.HOST
    base = get_root()
    base.length += 1
    base.put()
    new = Node(key_name=str(base.length), position=base.length, **props)
    new.put()
    return new

def create(addr, kind='node', **props):
    "Create a new position benath tumbler `address`. "
    # New ur-verse
    if not addr:
        assert kind == 'node'
        return new_root(**props)
    # New node of kind beneath address
    base = get(addr)
    assert base, addr
    subnode = \
        ((kind == 'node') and isinstance(base, Node)) or \
        ((kind == 'channel') and isinstance(base, Directory)) or \
        ((kind == 'entry') and isinstance(base, Entry))
    logger.info(['create', addr, subnode, kind])
    if subnode:
        return _new_node(None, base, kind=kind, **props)
    else:
        return _new_node(base, None, kind=kind, **props)


def _new_node(parent, base, kind=None, **props):

    """
    Helper to create a specific entity for the specified address (excluding
    virtual part). 
    """

    if parent:
        # attach new node at new sub-component address
        parent.leafs += 1
        tumbler = "%s.0.%s" % (parent.tumbler, parent.leafs)
        pos = parent.leafs
    else:
        # attach new node at new sub-address of current component
        base.length += 1
        tumbler = "%s.%s" % (base.tumbler, base.length)
        pos = base.length

    if kind == 'node':
        assert isinstance(parent, Docuverse) or \
                isinstance(base, Node), (parent, base)
        new = Node(key_name=tumbler, position=pos, **props)
    elif kind == 'channel':
        assert isinstance(parent, Node) or \
                isinstance(base, Directory), (parent, base)
        new = Directory(key_name=tumbler, position=pos, **props)
    elif kind == 'entry':
        assert isinstance(parent, Directory) or \
                isinstance(base, Entry), (parent, base)
        new = Entry(key_name=tumbler, position=pos, **props)
    else:
        raise Exception, kind

    if parent:
        parent.put()
    else:        
        base.put()

    increment(kind)            
    new.put()
    return new


def update(addr, **props):
    "Update properties of node at address. "
    node = get(addr)
    return update_node(node)


def update_node(node, **props):
    "Update properties of node. "
    for k, v in props.items():
        assert hasattr(node, k), k
        setattr(node, k, v)
    node.put()        


#def put_node(tumbler, kind='node', **props):
#    "Convenience, create node but first assert position. "
#    # XXX: transaction
#    p = tumbler.rfind('.')
#    base = get(tumbler[:p])
#    assert base.length+1 == int(tumbler[p-1:])
#    return create_node(base, kind, **props)


@list_q # filter various offset/length paging parameters
def list_nodes(span):
    """
    List nodes at address range. 
    As with FEBE, this includes the start address up to but not including the end address.
    """
    #assert len(span.width) == 2 relevant for fixed-level address such as virtual part

    #return [span.start, span.width, span.end()]

    nodes = []
    end = span.end()
    startnode = get(span.start)
    nodes.append(startnode)
    diff = end - span.start
    qlvl = max(len(span.start), len(end))
    assert len(diff) == qlvl
    current = Address(span.start.digits)
    for i in xrange(0, qlvl):
        while diff[i] > 0:
            nodes.extend(list_subnodes(current))
            current += Offset( *( i*( 0,) ) + ( 1,) )
            if current == end:
                break
            nodes.append(get(current))
            diff.digits[i] -= 1
    return nodes

def list_subnodes(addr):
    """
    Recursively query for all nodes after last digit.
    """
    nodes = []
    node = get(addr)
    for i in xrange(1, node.length+1):
        subaddr = Address(addr.digits)#copy()
        subaddr.digits.append(i)
        nodes.append(get(subaddr))
        nodes.extend(list_subnodes(subaddr))
    return nodes


def append_v(address, stream_index, data):
    entry = get(address)
    if stream_index <= entry.spaces:
        entry.init_stream(stream_index)
    vstream = entry.content[stream_index]
    vstream.add(data)
    vstream.put()


def append(addr, data=[], title=None):
    """
    Put content as new entry in directory.

    1. literal
    2. link
    3. image 
    
    TODO: 4. audio 
    TODO: 5. video
    """
    assert len(addr.split_all()) == 2
    contents = []
    idx = 0
    for idx, vstr in enumerate(data):
        length = len(vstr)
        if length > 1024**3:
            raise "XXX: Largish data..? %s" % length
        #increment('virtual', length)
        if idx == 0:
            assert isinstance(data[0], unicode)
            size = len(data[0].encode('utf-8'))
            v = LiteralContent(data=data[0], length=length, size=size)
        if idx == 1:
            v = LinkContent(data=data[1], length=length)
        if idx == 2:
            v = ImageContent(data=data[2])
        if idx > 2:
            raise InvalidVType, idx
        v.put()
        contents.append(v.key())
    base = get(addr)        
    n = _new_node(base, None, kind='entry', title=title)
    n.content = contents
    n.leafs = len(data)
    n.put()
    logging.info("Stored %i virtual streams at %s", idx+1, n)
    return n


def blank(span):
    "Erase data at span (retains blank space for the range of previous width). "
    pass # TODO: blank out data at span



# TODO: use Blobstore instead of datastore
def deref(span):
    "Return data for Entry nodes at address range. "
    assert span.start.split_all() == 4, \
            "Need complete address, including virtual part. "
    entry_addr, vaddr = span.start.split()

    # res_key = ...

    # Instantiate a BlobReader for a given Blobstore value.
    blob_reader = blobstore.BlobReader(res_key)

    # Instantiate a BlobReader for a given Blobstore value, setting the
    # buffer size to 1 MB.
    blob_reader = blobstore.BlobReader(res_key, buffer_size=1048576)

    # Instantiate a BlobReader for a given Blobstore value, setting the
    # initial read position.
    blob_reader = blobstore.BlobReader(res_key, position=4194304)
 
    # TODO

    # Read the entire value into memory.  This may take a while depending
    # on the size of the value and the size of the read buffer, and is not
    # recommended for large values.
    #value = blob_reader.read()

    # Set the read position, then read 100 bytes.
    #blob_reader.seek(2097152)
    #data = blob_reader.read(100)

