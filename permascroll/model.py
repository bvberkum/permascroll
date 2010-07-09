""" Permascroll <>----- Feed <>------ Entry
                         ^              entry_id  
                         v               | 
                         |               |
                         |               v
                    Mailinglist <>--- MIMEMessage
                                        message_id



- Feeds and Entries in a Feed are counted.                    
- Mailinglist subclasses abstract class Feed, every list counts as a feed.
- MIMEMessage does not subclass non-abstract Entry, messages may appear in
  multiple lists, but for each an entry has to exist. 
- Entries can exist for any kind of entity. The entry_id's scheme has to be
  interpreted to find the Kind that is linked to if one wants to fetch the
  entity.

  E.g. for Entry(key_name='mid:someid@ahost') an entity can be found if the
  Kind is known for keys with the 'mid' scheme. In this case, the entry is 
  a mailinglist item, this may be Message(key_name='someid@ahost').

"""
import random
from cgi import parse_qs
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.db import polymodel, djangoforms as gappforms


"""
Counters are kept for items in each space
, and by default 'sharded' into 20 separate entities.
This is interesting when doing multiple inserts, since writing takes longer than 
reading.
However, each insert still needs the total count to be able to assign an index
number.

See http://code.google.com/appengine/articles/sharding_counters.html.    
"""

class CounterShardConfig(db.Model):
    name = db.StringProperty(required=True)
    num_shards = db.IntegerProperty(required=True, default=20)

class CounterShard(db.Model):
    name = db.StringProperty(required=True)
    partial_count = db.IntegerProperty(required=True, default=0)

def get_count(name):
	total = 0
	for counter in CounterShard.all().filter('name = ', name):
		total += counter.partial_count
	return total

def increment(name):
    config = CounterShardConfig.get_or_insert(name, name=name)
    def txn():
        shard = random.randint(0, config.num_shards-1)
        shard_name = name + str(shard)
        counter = CounterShard.get_by_key_name(shard_name)
        if counter is None:
            counter = CounterShard(key_name=shard_name, name=name)
        counter.partial_count += 1
        counter.put()
        return counter.partial_count
    count = db.run_in_transaction(txn)
	#memcache.incr(name)


"""
Main classes
"""

class Permascroll(db.Model):

    """
    Main entity, a list of tumbler, space-kind records.
    """

    tumbler_address = db.StringProperty()
    kind_of_space = db.StringProperty()


class Node(db.Model):

    """
    Abstract record, numbered sequentially and hierarchically structured.

    Instances of the two subclasses are counted by the sharded counters 'space' and
    'item'. parent, index pairs should ofcourse be unique. node_id too as that
    serves as keynames for the actual records. Each node is identified (by
    keyname) using a tumbler which are created in order and hierchically. 
    Mappings of tumbler, kind are kept for subclasses of Space, see 
    Permascroll db.Model.
    """

    index = db.IntegerProperty( )
    title = db.StringProperty()
	# key_name = tumbler URI
    node_id = db.LinkProperty( required=True ) # web URI
    parent_id = db.LinkProperty( ) # tumbler URI


class Space(Node):

    """
    Abstract container class.
    """

    node_kind = 'space'


class Item(Node):

    """
    Abstract member of Space.
    """

    node_kind = 'item'


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


class Mailinglist(Space):

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

def get(tumbler):
    # split hierarchical components (server, account, document)
    parts = tumbler.split('.0.')

    # return record for deepest component,
    # starting at the top:

    server = Permascroll.get(db.Key(parts[0]))
    if not server:
        return # tumbler not found
    elif len(parts)==1:
        return parse[0], server

    account = Permascroll.get(db.Key('.0.'.join(parts[0:2])))
    if not account:
        return # tumbler not found
    elif len(parts)==2:
        return '.0.'.join(parts[0:2]), account

    user = users.get_current_user()

#    if not user:
#        user = 'anonymous'
#    if not has_access( account.node_kind, account.node_id ):
#        return 

    document = Node.get()
    if not document:
        return
    else:
        return '.0.'.join(parts[0:2]), account

    map(int, tumbler.split('.'))

    kind = Permascroll.all().filter('tumbler=', tumbler).kind
    return Node(key_name=tumbler, node_id=db.Link('http://foo/'+tumbler))

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

