""" 
- Directorys and Entries in a Directory are counted.                    
- Mailinglist subclasses abstract class Directory, every list counts as a feed.
- MIMEMessage does not subclass non-abstract Entry, messages may appear in
  multiple lists, but for each an entry has to exist. 
- Entries can exist for any kind of entity. The entry_id's scheme has to be
  interpreted to find the Kind that is linked to if one wants to fetch the
  entity.

  E.g. for Entry(key_name='mid:someid@ahost') an entity can be found if the
  Kind is known for keys with the 'mid' scheme. In this case, the entry is 
  a mailinglist item, this may be Message(key_name='someid@ahost').

"""
from cgi import parse_qs
import random
import logging

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.db import polymodel#, djangoforms as gappforms
import zope.interface
from zope.interface import implements

from permascroll.util import INode, IDirectory, IEntry, PickleProperty


logger = logging.getLogger(__name__)

def is_cached(etag):
    return memcache.get(etag) != None

def invalidate_cache(etag):
    memcache.delete(etag)

def insert_cache(etag, data):
    memcache.add(etag, data)


class Status(db.Model):
    counts = PickleProperty()
    count_updated = db.ListProperty(str)
        
def get_status(name='default'):
    status = Status.get_by_key_name(name)
    if not status:
        #COUNTERS = ['node','directory','entry','virtual']
        COUNTERS = ['node','channel','entry','virtual']
        status = Status(counts=dict([(n,0) for n in COUNTERS]),updated=COUNTERS)
        status.put()
    return status

"""
TODO: sharded counting of all Nodes, Directories, Entries and virtual
streams/chars/bytes..

See also http://code.google.com/appengine/articles/sharding_counters.html.    
"""

class CounterShardConfig(db.Model):
    name = db.StringProperty(required=True)
    num_shards = db.IntegerProperty(required=True, default=20)

class CounterShard(db.Model):
    name = db.StringProperty(required=True)
    partial_count = db.IntegerProperty(required=True, default=0)

def get_count(name):
    status = get_status()
    if name in status.count_updated:
        total = 0
        for counter in CounterShard.all().filter('name = ', name):
            total += counter.partial_count
        status.count_updated -= [name]
        status.counts[name] = total
        status.put()
    return status.counts[name]

def increment(name, amount=1):
    config = CounterShardConfig.get_or_insert(name, name=name)
    def txn():
        shard = random.randint(0, config.num_shards-1)
        shard_name = name + str(shard)
        counter = CounterShard.get_by_key_name(shard_name)
        if counter is None:
            counter = CounterShard(key_name=shard_name, name=name)
        counter.partial_count += amount
        counter.put()
        status = get_status()
        if not name in status.count_updated:
            status.count_updated += [name]
            status.put()
        return counter.partial_count
    partcount = db.run_in_transaction(txn)
    #memcache.incr(name)


"""
Main classes

-  1 First Docuverse
-  1.4.1 A Node
-  1.4.1.0.1 first channel for node
-  1.4.1.0.1.0.1 first entry therein..
-  1.4.1.0.1.0.1.0.1... first vstr addr.
"""
class Docuverse(db.Model):
    """
    Represented by the Ur-digit, the first digit of a tumbler address. 
    Permascroll uses addresses with 3 components, ie. 3 tumbler digits
    concatenated by '.0.'.

    There are as many Docuverses as there are Ur-digits, in normal operation
    just 1.
    """
    length = db.IntegerProperty()
    "Nr. of contained nodes. "

    def __repr__(self):
        return "[First Docuverse, %s positions]" % self.length

class AbstractNode(db.Model):
    # tumbler address is used for key

    def __init__(self, *args, **props):
        assert not args or props, ("Abstract class expects no arguments/props", args, props)
        super(AbstractNode, self).__init__(**props)

    position = db.IntegerProperty(required=True)
    "Position on parent (the last digit of the tumbler). "

    length = db.IntegerProperty(default=0)
    "Nr. of positions below this tumblers last digit. "

    leafs = db.IntegerProperty(default=0)
    "Nr. of sub-address tumblers below this tumbler component. "

    @property
    def tumbler(self):
        "The full tumbler URI (key name) for this node. "
        return self.key().name()

    title = db.StringProperty(required=False)
    "Unicode string, uniqueness only required for certain Node types. "

    def __repr__(self):
        return "[%s, with %i positions at %s, and %i sub-adresses]" % \
    (self.title or "Untitled %s" % (self.kind()), 
                self.length, self.tumbler, self.leafs)

class Node(AbstractNode, db.Model):
    # parent = Docuverse
    #base = db.SelfReferenceProperty(required=False)
    #"Root Node's are based on a Docuverse, others on a Node. "
    implements(INode)

class Directory(AbstractNode, db.Model):
    # parent = Node
    #base = db.SelfReferenceProperty(required=False)
    implements(IDirectory)

class Entry(AbstractNode, db.Model):
    # parent = Directory
    #base = db.SelfReferenceProperty(required=False)
    #"Root entry's are based in a Directory, others have a parent Entry. "
    implements(IEntry)

    def __init__(self, data='', **props):
        super(Entry, self).__init__(**props)
        if data:
            self.add_vstream(data)

    def add_vstream(self, data):
        assert isinstance(data, unicode)
        bytesize = len(data.encode('utf-8'))
        #md5digest = 
        content = LiteralContent(data=data, size=bytesize, length=len(data))
        content.save()
        self.content.append(content.key())
        self.leafs += 1
        self.save()

    #content_type = ['PEDL']
    content = db.ListProperty(db.Key)
    "One or more keys for Content objects, implementing one or more v-streams.  "
    # The tumbler format of the vstream is determined by the content-type

    def __repr__(self):
        return "[%s, with %i positions at %s, and %i sub-adresses]" % \
    (self.title or "Untitled %s" % (self.kind()), 
                self.length, self.tumbler, self.leafs)

    #leafs = 3 # XXX: Entry recognizes 3 v-types

#class Virtual(AbstractNode, db.Model):
#    content = db.ListProperty(db.Key)
#    "One or more keys for Content objects, implementing one or more v-streams.  "

class LiteralContent(db.Model):
    data = db.TextProperty()

    #encoding = PlainStringProperty()
    #"Original codec/charset of the text data. "
    #md5_digest = db.BlobProperty()
    #"MD5 digest of bytestring. "
    size = db.IntegerProperty()
    "Nr. of bytes (length of bytestring). "
    length = db.IntegerProperty()
    "Nr. of characters (length of unicode-text string)."

    def __str__(self):
        return self.data

class LinkContent(db.Model):
    data = db.ListProperty(db.Link)
    # XXX: size/length?    

class ImageContent(db.Model):
    pass

class Unused:
    node_id = db.LinkProperty( )
    "A (Web) URI for the node, applicable for non-original content. "


"""
MIME message support.
"""

class MIMEMessage(db.Model):

    """
    First version of representation of mailinglist message.
    """

    message_id = db.LinkProperty(required=True)
    from_id = db.StringProperty() # make Link once User object with Unique ID is there
    subject = db.StringProperty()
    reply_to = db.LinkProperty()

    content_type = db.StringProperty()
    content = db.StringProperty()

    @classmethod
    def create(cls, message_id):
        msg = MIMEMessage.get_by_key_name(message_id)
        if msg:
            raise Exception('Exists')
        msg = MIMEMessage(
                key_name=message_id,
                message_id=message_id
                )
        msg.put()
        return msg


class Mailinglist(Directory):

    """
    List of MIMEMessages.
    """

    mailbox_id = db.StringProperty()

    @classmethod
    def create(cls, mailbox_id, parent=1):
        ml = Mailinglist.all().filter('mailbox_id =',mailbox_id)
        if ml:
            raise Exception('Exists')
        ml = Mailinglist(
                key_name=mailbox_id, 
                mailbox_id=mailbox_id,
                feed_id='mailto:%s' % mailbox_id,
                parent=parent,
                index=increment('space'))
        ml.put()
        return ml

    def add_message(self, msg, msg_id):
        if not msg:
            msg = MIMEMessage.create(msg_id)
        Entry.create(feed_id, entry_id)


def get_form(kind, *properties):
    exclusive = False
    if properties and isinstance(properties[0], bool):
        exclusive, properties = not properties[0], properties[1:]
    elif not properties:
        exclusive = True

    if exclusive:
        class MetaInfo:
            model = kind
            exclude = list(properties)
    else:
        class MetaInfo:
            model = kind
            fields = list(properties)

    return gappforms.ModelFormMetaclass('GenericForm',
        (gappforms.ModelForm,), {'Meta': MetaInfo})


def decode(data, contenttype):

    if contenttype == 'application/x-www-form-urlencoded':
        data = parse_qs(data)
    else:
        raise contenttype

    return data


def validate(data, headers, kind):
    """
    Return a generator which returns:

    1. a boolean if the data is valid for kind
    1.1. a new entity of kind if the data was valid
    2. the form for kind that was used the validate the data
    """
 
    contenttype = headers.get('content-type', 'application/octet-stream')
    data = decode(data, contenttype)

    form = get_form(kind, kind.properties().keys())( data=data )

    valid = form.is_valid()
    yield valid

    if valid:
        #record = kind.create( data._cleaned_data )
        record = form.save(commit=False)
        yield record

    yield form



# Oldish
class Unique(db.Model):

    index = db.IntegerProperty()

    @classmethod
    def check(cls, scope, value):
        """
        Create new entity if value is unique, assign index number.
        """
        def txn(scope, value):
            key_name = "U%s:%s" % (scope, value)
            ue = Unique.get_by_key_name(key_name)
            if ue:
                raise UniqueConstraintViolation(scope, value)
            ue.index = get_count(scope)
            ue.put()
            return ue.index
        return db.run_in_transaction(txn, scope, value)

class UniqueConstraintViolation(Exception):
    def __init__(self, scope, value):
        super(UniqueConstraintViolation, self).__init__(
                "Value '%s' is not unique within scope '%s'." % (value, scope, ))

