import logging
from permascroll import rc
from permascroll.util import list_q
from permascroll.model import *
from permascroll.exception import *


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
        tccnt = addr.digits.count(0)+1
        if tccnt == 2: kind = Directory
        elif tccnt == 3: kind = Entry
        node = kind.get_by_key_name(str(addr))
        if not node:
            raise NotFound, (kind, addr)

        return node

def fetch(addr):
    try:
        return get(addr)
    except NotFound, e:
        return None

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
        parent.leafs += 1
        tumbler = "%s.0.%s" % (parent.tumbler, parent.leafs)
        pos = parent.leafs
    else:
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
    "List nodes at address range. "
    assert len(span.width) == 2
    nodes = []
    ts = []
    # Handle query: dereference node for each position in span
    # retrieves positions for one specific tumbler digit position or 'address level'
    logger.info([span.start.digits[-1], span.width[1]+1])
    for x in xrange(span.start[-1], span.width[1]+1):
        t = span.start
        t.digits[-1] = x
        logger.info(x)
        #ts.append(t.copy)
        nodes.append(get(t))
    # TODO: return query        
    return nodes

def append(addr, data=None, title=None, **props):
    """
    Append data for Entry type at address.

    1. literal
    2. link

    TODO:
        3. image 
        4. audio
        5. video
    """
    entry_addr, vaddr = addr.split()
    base = get(entry_addr)
    assert base.kind() in ('Entry', 'Directory')
    length = len(data)
    if length > 1024**3:
        raise "XXX: Largish data..? %s" % length
    increment('virtual', length)
    #assert isinstance(node, Entry) or isinstance(node, Channel), node
    v = None
    if vaddr[0] == 1:
        v = LiteralContent(data=data, **props)        
        v.length = len(v.data)
    elif vaddr[0] == 2:
        v = EDL(data=data, **props)
    elif vaddr[0] == 3:
        v = Image(data=data, **props)
    else:
        raise InvalidVType, vaddr[0]
    # content = 'blob:hash-of-image', 'literal:hash-of-literal', 
    #           'edl:hash-of-edl'
    v.put()
    if base.kind() == 'Entry':
        n = _new_node(None, base, kind='entry', title=title)
    else:    
        n = _new_node(base, None, kind='entry', title=title)
    n.content = [v.key()]
    n.put()
    return n

def deref(span):
    "Return data for Entry nodes at address range. "
    assert span.start.split_all() == 4, "Need complete address, including virtual part. "
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

def blank(span):
    "Erase data at span (retains blank space for the range of previous width). "
    pass


