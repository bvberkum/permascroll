import logging
from permascroll.model import *
from permascroll.exception import *


logger = logging.getLogger(__name__)


def get(*tumblers):
    """
    Dereference tumbler and return Node, Channel, Entry 
    (depending on component count) or raise NotFound.
    """
    tcnt = len(tumblers)
    
    # return record for deepest component,
    # starting at the top
    docuverse = get_root()
    if not tcnt:
        return docuverse
    elif tcnt == 1:
        node = Node.get_by_key_name(str(tumblers[0]), docuverse)
    elif tcnt == 2:
        key = db.Key.from_path('Channel', str(tumblers[1]), parent=docuverse)
        node = Channel.get(key)
    elif tcnt == 3:
        key = db.Key.from_path('Channel', str(tumblers[1]), 'Entry',
                str(tumblers[1]), parent=docuverse)
        node = Entry.get(key)
    else:
        raise Exception, "Need 1, 2 or 3 tumbler address components. "
    assert node, tumblers
    return node

def fetch(*tumblers):
    try:
        return get(*tumblers)
    except NotFound, e:
        return None

def get_root():
    base = Docuverse.all().get()
    if not base:
        base = Docuverse(key_name='docuverse', length=0)
        base.put()
    return base

def new_root(**props):
    base = get_root()
    base.length += 1
    base.put()
    new = Node(key_name=str(base.length), parent=base, position=base.length, **props)
    new.put()
    return new

def create_node(*tumblers, **props):
    kind = props.get('kind','node')
    if 'kind' in props: del props['kind']
    if not tumblers:
        # New ur-verse
        assert kind == 'node'
        return new_root(**props)
    base = fetch(*tumblers)
    subnode = \
        ((kind == 'node') and isinstance(base, Node)) or \
        ((kind == 'channel') and isinstance(base, Channel)) or \
        ((kind == 'entry') and isinstance(base, Entry))
    logger.info([base, tumblers, subnode])
    if subnode:
        return create_subnode(base, kind=kind, **props)
    else:
        return create_node_for(base, kind=kind, **props)

def create_subnode(base, kind, **props):
    return _new_node(None, base, kind=kind, **props)

def create_node_for(parent, kind, **props):        
    return _new_node(parent, None, kind=kind, **props)

def _new_node(parent, base, kind=None, **props):
    if parent: e = parent
    elif base: e = base
    else:
        raise Exception, (parent, base)
    #
    e.length += 1
    tumbler = "%s.%s" % (e.tumbler, e.length)
    e.put()
    pos = e.length
    #
    if kind == 'node':
        assert isinstance(parent, Docuverse) or \
                isinstance(base, Node), (parent, base)
        new = Node(key_name=tumbler, parent=parent, position=pos, **props)
    elif kind == 'channel':
        assert isinstance(parent, Node) or \
                isinstance(base, Channel), (parent, base)
        new = Channel(key_name=tumbler, parent=parent, position=pos, **props)
    elif kind == 'entry':
        assert isinstance(parent, Channel) or \
                isinstance(base, Entry), (parent, base)
        new = Entry(key_name=tumbler, parent=parent, position=pos, **props)
    else:
        raise Exception, kind
    if base:
        new.base = base
    new.put()
    return new

#def create_space(node, **props):
#    return create_node(node, kind='space', **props)
#
#def create_item(space, **props):
#    return create_node(node, kind='item', **props)

def update_node(node, **props):
    for k, v in props.items():
        assert hasattr(node, k), k
        setattr(node, k, v)
    node.put()        

def put_node(tumbler, kind='node', **props):
    p = tumbler.rfind('.')
    base = get(tumbler[:p])
    assert base.length+1 == int(tumbler[p-1:])
    return create_node(base, kind, **props)



