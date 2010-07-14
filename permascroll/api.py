import logging
from permascroll.model import *
from permascroll.exception import *


logger = logging.getLogger(__name__)


def get(*tumblers):
    """
    Dereference tumbler and return Node, Channel, Entry 
    (depending on component count) or raise NotFound.
    """
    docuverse = get_root()
    if not tumblers:
        return docuverse
    
    else:
        kind = Node
        tcnt = len(tumblers)
        if tcnt == 2: kind = Channel
        elif tcnt == 3: kind = Entry
        node = kind.get_by_key_name(
                '.0.'.join(map(str, tumblers)))
        if not node:
            raise NotFound, '.0.'.join(map(str, tumblers))

        return node

def fetch(*tumblers):
    try:
        return get(*tumblers)
    except NotFound, e:
        return None

def get_root():
    "The root has no address but keeps track of Ur-digits--it counts docuverses. "
    base = Docuverse.all().get()
    if not base:
        base = Docuverse(key_name='docuverse', length=0)
        base.put()
    return base

def new_root(**props):
    "Create new docuverse. "
    base = get_root()
    base.length += 1
    base.put()
    new = Node(key_name=str(base.length), position=base.length, **props)
    new.put()
    return new

def create_node(*tumblers, **props):
    kind = props.get('kind','node')
    if 'kind' in props: del props['kind']
    # New ur-verse
    if not tumblers:
        assert kind == 'node'
        return new_root(**props)
    # New node of kind beneath address
    base = get(*tumblers)
    assert base, tumblers
    subnode = \
        ((kind == 'node') and isinstance(base, Node)) or \
        ((kind == 'channel') and isinstance(base, Channel)) or \
        ((kind == 'entry') and isinstance(base, Entry))
    if subnode:
        return _new_node(None, base, kind=kind, **props)
    else:
        return _new_node(base, None, kind=kind, **props)
    logger.info([base, tumblers, subnode])

def _new_node(parent, base, kind=None, **props):
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
                isinstance(base, Channel), (parent, base)
        new = Channel(key_name=tumbler, position=pos, **props)
    elif kind == 'entry':
        assert isinstance(parent, Channel) or \
                isinstance(base, Entry), (parent, base)
        new = Entry(key_name=tumbler, position=pos, **props)
    else:
        raise Exception, kind
    if parent:
        parent.put()
    else:        
        base.put()
    new.put()
    return new

def update_node(node, **props):
    for k, v in props.items():
        assert hasattr(node, k), k
        setattr(node, k, v)
    node.put()        

def put_node(tumbler, kind='node', **props):
    "Convenience, create node but first assert position. "
    # XXX: transaction
    p = tumbler.rfind('.')
    base = get(tumbler[:p])
    assert base.length+1 == int(tumbler[p-1:])
    return create_node(base, kind, **props)



