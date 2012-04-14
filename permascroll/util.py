"""
Assorted auxiliary classes/functions.
"""
import copy
import logging
import pickle
import re
import traceback
import unicodedata
import urllib

import gate

from google.appengine.api import users
from google.appengine.ext import db
from zope.interface import adapter, interface, providedBy

from permascroll import pedl
from permascroll.xu88 import *
from permascroll.exception import *


logger = logging.getLogger(__name__)



### Components

class IModel(interface.Interface): pass
class INode(IModel): pass
class IDirectory(IModel): pass
class IEntry(IModel): pass
class IVirtual(IModel): pass
#class ILiteralContent(IVirtual): pass
#class IEDL(IVirtual): pass
class IOutput(interface.Interface): pass

components = adapter.AdapterRegistry()

class PlainOutputAdapter(object):
    def __init__(self, adaptee):
        self.model = adaptee
    def __str__(self):
        return "%s" % self.model
    def __repr__(self):
        return "[PlainOutputAdapter %r]" % self.model

components.register([INode], IOutput, 'plain', PlainOutputAdapter)
components.register([IDirectory], IOutput, 'plain', PlainOutputAdapter)
components.register([IEntry], IOutput, 'plain', PlainOutputAdapter)

class NodeJSONOutputAdapter(object):
    def __init__(self, adaptee):
        self.model = adaptee
    def __str__(self):
        return "{%s}" % ", ".join([
            "'%s': %r" % (a, getattr(self.model, a))
            for a in ('position', 'length', 'leafs', 'title',)
            ] + [ "'type': '%s'" % self.model.__class__.__name__])
    def __repr__(self):
        return "[NodeJSONOutputAdapter %r]" % self.model

class EntryJSONOutputAdapter(object):
    def __init__(self, adaptee):
        self.model = adaptee
    #def __call__(self, adapter):
    def __str__(self):
        from google.appengine.ext import db

        content = ""
        for key in self.model.content:
            #assert isinstance(obj, LiteralContent)
            content += db.get(key).data

        return "{%s}" % ", ".join([
            "'%s': %r" % (a, getattr(self.model, a))
            for a in ('position', 'length', 'leafs', 'title')
            ] + [
                "'type': '%s'" % self.model.__class__.__name__,
                "'content': '%s'" % content
            ])
    def __repr__(self):
        return "[NodeJSONOutputAdapter %r]" % self.model

components.register([INode], IOutput, 'json', NodeJSONOutputAdapter)
components.register([IDirectory], IOutput, 'json', NodeJSONOutputAdapter)
components.register([IEntry], IOutput, 'json', EntryJSONOutputAdapter)



### Model properties

class PickleProperty(db.Property):
  """A property for storing complex objects in the datastore in pickled form.

  Example usage:

  >>> class PickleModel(db.Model):
  ...   data = PickleProperty()

  >>> model = PickleModel()
  >>> model.data = {"foo": "bar"}
  >>> model.data
  {'foo': 'bar'}
  >>> model.put() # doctest: +ELLIPSIS
  datastore_types.Key.from_path(u'PickleModel', ...)

  >>> model2 = PickleModel.all().get()
  >>> model2.data
  {'foo': 'bar'}
  """

  data_type = db.Blob

  def get_value_for_datastore(self, model_instance):
    value = self.__get__(model_instance, model_instance.__class__)
    if value is not None:
      #logging.info("Pickling..")
      return db.Blob(pickle.dumps(value))

  def make_value_from_datastore(self, value):
    if value is not None:
      #logging.info("Unpickling..")
      return pickle.loads(str(value))

  def default_value(self):
    """If possible, copy the value passed in the default= keyword argument.
    This prevents mutable objects such as dictionaries from being shared across
    instances."""
    return copy.copy(self.default)

class Link(unicode): # {{{
    "See google.appengine.api.datastore_types.Link. "
    def __init__(self, link):
        super(Link, self).__init__(self, link)
        ValidateString(link, 'link', max_len=_MAX_LINK_PROPERTY_LENGTH)

        scheme, domain, path, params, query, fragment = urlparse.urlparse(link)
        if (not scheme or (scheme != 'file' and not domain) or
                          (scheme == 'file' and not path)):
          raise datastore_errors.BadValueError('Invalid URL: %s' % link)

    def ToXml(self):
        return u'<link href=%s />' % saxutils.quoteattr(self)
    # }}}


## Oldish (unused)

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




### Argument parser/convertor utilities

def _format_values(values, combine='or'):
    if len(values) > 1:
        return '.'.join(values[:-1]) + ' %s %s. ' % (combine, values[-1])
    elif values:
        return values[0]

def choice(argument, values): # {{{
    try:
        value = argument.lower().strip()
    except AttributeError:
        raise ValueError('must supply an argument; choose from %s'
                         % _format_values(values))
    if value in values:
        return value
    elif value:
        raise ValueError('"%s" unknown; choose from %s'
                         % (argument, _format_values(values)))
    else:
        raise ValueError('choose from %s'
                         % (_format_values(values)))
    # }}}

def null_conv(datatype=str, conv=None): # {{{
    """
    Create convertor for NoneType instances to type-specific empty instances.
    (Those for which ___nonzero__ == False holds)

    The convertor accepts a Node or string. Param `conv` may be provided for
    non-standard types. Otherwise the value from null() is used.
    """
    def conv_null(arg):
        if conv:
            return conv(arg)
        else:
            i = datatype()
            if arg and str(i) != arg:
                raise ValueError, "Invalid str representation of %r for %s" % (
                        arg, i)
            return i
    return conv_null
    # }}}

def conv_unicode(arg): # {{{
    "Return unicode, collapsed whitespace. "
    return re.sub('\s+', ' ', arg).strip()
    # }}}

def conv_str(arg, charset='ascii'): # {{{
    "Return string (default: ascii), collapsed whitespace. "
    unistr = conv_unicode(arg)
    return unistr.encode(charset)
    # }}}

def conv_text(arg): # {{{
    "Multiline text, unicode. "
    if isinstance(arg, str):
        arg = unicode(arg, 'ascii')
    assert isinstance(arg, unicode)
    return arg
    # }}}

has_whitespace = re.compile("\s").match
def conv_word(arg): # {{{
    """
    Unicode without whitespace.
    """
    w = arg.strip()
    if has_whitespace(w):
        raise ValueError("Need a single word value without whitespace. ")
    return w
    # }}}

def conv_int(arg): # {{{
    return int(conv_word(arg))
    # }}}

def conv_float(arg): # {{{
    return float(conv_word(arg))
    # }}}

def conv_long(arg): # {{{
    return long(conv_word(arg))
    # }}}

def conv_complex(arg): # {{{
    return complex(conv_str(arg))
    # }}}

def conv_uri_reference(href): # {{{
    # XXX: relative or absolute
    m = uriref.match(href)
    if not m:
        raise ValueError, "Not a valid URI reference: %s" % href
    return href
    # }}}

def conv_hex(arg):
    return hex(int(arg, 16))

def conv_hex32(arg):
    assert len(arg) == 32
    return conv_hex(arg)

def conv_bool(arg): # {{{
    """
    Parse yes/no, on/off, true/false and 1/0. Return bool or null.
    """
    arg = arg.strip()
    if arg:
        opt = choice(arg, ('yes', 'no', 'on', 'off', 'true',
            'false', '1', '0'))

        return opt in ('yes', 'on', 'true', '1')
    # }}}

def conv_yesno(arg): # {{{
    """
    Parse yes/no, return bool or null.
    """
    arg = arg.strip()
    if arg:
        opt = choice(arg, ('yes', 'no'))
        return opt == 'yes'
    # }}}

def cs_list(arg): # {{{
    """
    Argument validator, parses comma-separated list.
    May contain empty values.
    """
    arg = arg.strip()
    if arg:
        return [a.strip() for a in arg.split(',')]
    else:
        return []#XXX:u'']
    # }}}

def conv_tumbler(arg, T=Tumbler):
    arg = arg.strip('/').replace('/','.0.')
    t = T(arg)
    return t

def conv_address(arg):
    return conv_tumbler(arg, T=Address)

def conv_offset(arg):
    return conv_tumbler(arg, T=Offset)

def conv_width_exp(arg):
    """
    Read compressed width tumbler from string.

    First tumbler digit is the exponent: the number of digits that the given
    width tumbler needs to be offset to.
    """
    offset = Tumbler(arg).digits
    exp, offset = offset[0], offset[1:]
    while exp != 0:
        offset.insert(0,0)
        exp-=1
    return Offset(offset)

def conv_compressed_span(arg):
    """
    Read a argument as ``address tumbler '~' compressed offset tumbler``.
    """
    assert arg.count('~') == 1, arg
    tumblers = arg.split('~')
    start = conv_address(tumblers[0])
    width = conv_width_exp(tumblers[1])
    span = Span(start, width)
    logger.info("Parsed incoming span: %s -> %s", arg, span)
    return span

# XXX: but what about multiple components?

def conv_address_span(arg):
    """
    Read argument as ``address tumbler '+' offset tumbler``.
    """
    assert arg.count('+') == 1, arg
    tumblers = arg.split('+')
    start = conv_address(tumblers[0])
    width = conv_offset(tumblers[1])
    span = Span(start, width)
    logger.info("Parsed incoming span: %s -> %s", arg, span)
    return span

def conv_span_or_address(arg):
    """
    Scan for and convert a type of span or address.
    """
    if '+' in arg:
        return conv_address_span(arg)
    elif '~' in arg:
        return conv_compressed_span(arg)
    else:
        return conv_address(arg)

def conv_blob(arg):
    if hasattr(arg, 'disposition'): # cgi.FieldSet
        logging.info((arg, arg.type))
        if arg.type in data_convertor:
            logging.info((arg.type, data_convertor[arg.type]))
            return data_convertor[arg.type](arg)
    return arg

def conv_pedl(arg):
    doc = pedl.parse(arg)
    return doc

def conv_mime(arg):
    pass # TODO
    return arg


## Parser/convertor registry

data_convertor = {
    'hex': conv_hex,
    'hex_32byte': conv_hex32,
    'bool': conv_bool,
    'int': conv_int,
    'float': conv_float,
    'long': conv_long,
    'complex': conv_complex,
    'word': conv_word, # unicode word without whitespace
    # collapsed whitespace strings:
    # XXX: 'str,charset'?
    'str': conv_str, # ascii
    'unicode': conv_unicode,
    #'null': conv_null,
    # XXX: 'null,str'?
    'null-str': null_conv(str, conv_str),
    'text': conv_text, # unicode multiline text
    'href': conv_uri_reference,
    'yesno': conv_yesno,
    #'timestamp': conv_timestamp,
    #'isodate': conv_iso8801date,
    #'rfc822date': conv_rfc822date,
    'tumbler': conv_tumbler,
    'address': conv_address,
    'span': conv_address_span,
    'compressed_span': conv_compressed_span, # don't think this is used
    'span_or_address': conv_span_or_address,
    'cslist': cs_list,
    'blob': conv_blob,
    'mime': conv_mime,
    'text/x-pedl': conv_pedl,
}

def get_convertor(type_name):
    if ',' in type_name:
        complextype_names = type_name.split(',')
        basetype = data_convertor[complextype_names.pop(0)]
        return basetype + tuple([ data_convertor[n]
                for n in complextype_names ])
    else:
        return data_convertor[type_name]



### Request decorators

def mime(method):
    """
    A decorator to add a fixed media type to the response headers.
    This will also set MIME-Version: 1.0 and Content-Length.
    """
    mediatype = 'text/plain'
    #global mediatypes
    #@functools.wraps(method)
    def mime_handler(self, *args, **kwds):
        media = method(self, *args, **kwds)
        assert isinstance(media, basestring), type(media)
        #assert mediatype in mediatypes,\
        #        "Unknown mediatype %r.  " % mediatype
        #logger.info("Serving %s bytes as %s", len(media), mediatype)
        self.response.headers['MIME-Version'] = '1.0'
        self.response.headers['Content-Length'] = "%d" % len(media)
        self.response.headers['Content-Type'] = mediatype
        #self.response.headers['Content-ID']
        self.response.out.write(media)
    return mime_handler

def catch(method):
    """
    Catch any exception from calling the method,
    bring response in proper 500-state if needed.
    Chains with `mime` decorator.
    """
    def error_resp_handler(self, *args, **kwds):
        data = None
        try:
            data = method(self, *args, **kwds)
        except Exception, e:
            self.response.set_status(500)
            self.response.out.write("%s in %s handler: \n"%(type(e).__name__,
                    type(self).__name__))
            self.response.out.write(str(e))
            traceback.print_exc()
        if not data: data = ''
        return unicode(data) # XXX: codec?
    return mime(error_resp_handler)

def conneg(method):
    """
    Decorator to lookup output adapters for return value,
    auto-decorates with `catch`.
    """
    def conneg_wrap(self, *args, **kwds):
        media = method(self, *args, **kwds)
        #adapters = components.lookupAll(providedBy(media), IOutput)
        # Negotiate output format to use
        response_format = 'xml'
        conneg = gate.conneg.Conneg.for_request(self.request)
        variants = (
                ("json", 1.0, {'type':'application/javascript'}),
                #("yaml", 1.0, {'type':'application/yaml'}),
                #("xml", 1.0, {'type': 'application/xml'}),
                ("plain", 0.4, {'type':'text/plain'}),

                #("xml", 1.0, {'type': 'text/xml'}),
            )
        candidate_formats = conneg.select(variants, algorithm="RVSA/1.0")
        #candidate_formats = [
        #        (args[0], conneg.accept_rvsa_1_0(*args[0:2], **args[2])[-1])
        #        for args in variants ]
        if candidate_formats:
            response_format = candidate_formats[0]
            logger.info("Negotiated %s output format", response_format)
        output = components.queryAdapter(media, IOutput, response_format)
        logger.info("%s, %r", output, output)
        return output
    return catch(conneg_wrap)

def error2(method):
    " Catch basic errors and finish HTTP response.  "
    #@functools.wraps(method)
    def http_deco(self, *args, **kwds):
        try:
            return method(self, *args, **kwds)
        except AssertionError, e:
            self.assertion_error(e)
        except Exception, e:
            logger.critical("While handling %s (%s): %s", self.request.path,
                    self.__class__.__name__, e)
            self.exception(e)
    return http_deco

def _http_qwd_specs(fields):
    "Parse spec fields, and set default convertor.  "
    fields = [tuple(q.split(':')) for q in fields]
    for i, q in enumerate(fields):
        if len(q)==1:
            p, v = q +( 'str', )
        else:
            p, v = q
        fields[i] = p, v
    # filter out specs without name (positional arguments)
    idx_fields = [(i,v) for i,(k,v) in enumerate(fields) if not k]
    [fields.remove((k,v)) for k,v in fields if not k ]
    return idx_fields, fields

def _convspec(fields):
    "Get convertors for fields. "
    convs = dict([ (k,get_convertor(v)) for k,v in fields if v != '_' ])
    # keep '_' char for ignored arg/kwd
    convs.update(dict([ (k,'_') for k,v in fields if v == '_' ]))
    return convs

def http_q(*fields, **kwds): # {{{
    """
    Convert parameters from URL (GET) or x-form-encoded entity (POST).

    Unnamed fields are positional arguments from the URL path, matched by the
    handler dispatcher (by embedding match groups in the patterns in the URL
    map).

    Named fields are taken from the GET query or the POST entity.
    Field names are converted to name IDs, and '-' is replaced by '_'
    (to use the name ID as a Python identifier).

    Convertors are loaded from the data_convertor map in this module.
    For syntax see below.

    .. raw:: python

       class ExampleRequestHandler:
           pattern = '^/version/([0-9]+)/([^/]+)/(0|1)/([^\.]+)(\.test)$'

           @http(':int',':_',':bool',':unicode',':ext', 'kwd1:unicode', 'kwd2:text', test='pickle')
           def myhandle(self, v, arg1, arg2, arg3, kwd1=None, **otherkwds):
               pass

    '_' is treated as a special convertor to ignore an arg/kwd.

    The keyword `qwd_method` is reserved, an may be set to 'auto', 'both', or
    'GET' or 'POST'. Default is 'auto' to get arguments for current method
    (either GET or POST) only, other values allow explicit selection.
    """
    qwd_method = kwds.get('qwd_method', 'auto').lower()
    if 'qwd_method' in kwds:
        del kwds['qwd_method']
    aspec, qspec = map(_convspec, _http_qwd_specs(fields))
    qspec.update(_convspec(kwds.items()))
    def http_qwds(method):
        #@functools.wraps(method)
        def qwds_deco(self, *args, **kwds):
            #logger.info(args)
            if self.request.method in ('POST', 'PUT'):
                ct = self.request.headers.get('Content-Type')
                if ';' in ct:
                    p = ct.find(';')
                    ct = ct[:p]
                assert ct in ('application/x-www-form-urlencoded',
                        'multipart/form-data', ), "XXX: unsupported %s" % ct
            # take positional arguments from URL pattern
            argcnt = len(args)
            items = list(enumerate(args))
            ignorespecs = 0
            assert len(items) <= len(aspec), (items, aspec)
            for idx, data in items:
                if aspec[idx] == '_':
                    ignorespecs += 1
                    args = args[:idx] + args[idx+1:]
                    continue # ignore argument
                if type(data) == type(None) or idx >= argcnt: break
                value = None
                try:
                    value = aspec[idx](urllib.unquote(data))
                except (TypeError, ValueError), e:
                    # TODO: report warning in-document
                    logger.warning([idx, args[idx], e, aspec[idx], qspec])
                    logger.warning("Error applying argument convertor for '%s', "
                            "message: %s, convertor: %s", idx, e, qspec[idx])
                # always replace argument
                args = args[:idx-ignorespecs] + (value,) + args[idx-ignorespecs+1:]
            logger.debug("Converted arguments %s", args)
            # take keyword arguments from GET query or POST entity
            m = self.request.method
            items = []
            if m in ('POST','GET'):
                if qwd_method == 'auto':
                    # get args explicitly from current request method only
                    #items = getattr(self.request, m).items()
                    #items = tuple([
                    #    (a, self.request.get(a))
                    #    for a in self.request.params()
                    #])
                    items = self.request.params.items()
                    #logging.info((items, self.request.arguments()))
                    # XXX: self.request.params() also seems to work
                else:
                    # get args from at most both methods
                    if qwd_method in ('get', 'both'):
                        items += self.request.GET.items()
                    if qwd_method in ('post', 'both'):
                        items += self.request.POST.items()
            # validate/convert value for each key
            for key, data in items:
                key = key.replace('_','-')
                if key in qspec:
                    if qspec[key] == '_':
                        continue # ignore keyword
                    value = None
                    try:
                        value = qspec[key](data)
                    except (TypeError, ValueError), e:
                        # TODO: report warning in-document
                        logger.warning("Error applying data convertor for '%s', "
                                "message: %s, convertor: %s", key, e, qspec[key])
                    #logging.info([key, data, value, dir(value)])
                    if value != None: # update/add keyword
                        python_id = make_id(key).replace('-','_')
                        kwds[python_id] = value
            logger.debug(
                    'Converted URL query parameters to method signature: %s. ', kwds)
            return method(self, *args, **kwds)
        return qwds_deco
    return http_qwds
    # }}}


## User and Alias authentication

def web_auth(method): # {{{
    " Authenticate, prefix user.  "
    #@functools.wraps(method)
    def authorize_user_decorator(self, *args, **kwds):
        ga_user = users.get_current_user()
        if not ga_user:
            logger.info("Unauthorized request from %r", self.request.remote_addr)
            # XXX: redirect, but match browsers */* only?
            self.redirect(users.create_login_url(self.request.uri))
            return
        logger.debug('Request %s for user %s. ', self.request.url, ga_user.email())
        user = api.new_or_existing_ga(ga_user)
        return method(self, user, *args, **kwds)
    return authorize_user_decorator
    # }}}


## Experimental (unused)

list_param_set = (
        #('page', 'size', 'total') # XXX: relative
        ('num:int', 'start:long'), # like GAE dev-server admin
    )

def _find_pattern(kwds):
    for lp in list_param_set:
        v = True
        if lp[0] not in kwds:
            continue
        else:
            for query_name in lp:
                if query_name not in kwds:
                    #logger.info('Query failed for pattern %s', lp)
                    v = False
            if v:
                return lp

def list_q(method):
    "Do paging by parameters on list-queries, see model.api functions. "
    def list_q_wrap(*args, **kwds):
        p = _find_pattern(kwds)
        if p:
            cnt_, start = p
            if cnt_ in kwds:
                cnt = kwds.get(cnt,0)
            if start_ in kwds:
                start = kwds.get(start,0)
        else: # some compat. mode
            return method(*args, **kwds)
        q = method(*args, **kwds)
        return q.fetch(cnt, start)
    return list_q_wrap



### Borrowed from docutils: makeid

def make_id(string): # {{{
    """
    Convert `string` into an identifier and return it.

    Docutils identifiers will conform to the regular expression
    ``[a-z](-?[a-z0-9]+)*``.  For CSS compatibility, identifiers (the "class"
    and "id" attributes) should have no underscores, colons, or periods.
    Hyphens may be used.

    - The `HTML 4.01 spec`_ defines identifiers based on SGML tokens:

          ID and NAME tokens must begin with a letter ([A-Za-z]) and may be
          followed by any number of letters, digits ([0-9]), hyphens ("-"),
          underscores ("_"), colons (":"), and periods (".").

    - However the `CSS1 spec`_ defines identifiers based on the "name" token,
      a tighter interpretation ("flex" tokenizer notation; "latin1" and
      "escape" 8-bit characters have been replaced with entities)::

          unicode     \\[0-9a-f]{1,4}
          latin1      [&iexcl;-&yuml;]
          escape      {unicode}|\\[ -~&iexcl;-&yuml;]
          nmchar      [-a-z0-9]|{latin1}|{escape}
          name        {nmchar}+

    The CSS1 "nmchar" rule does not include underscores ("_"), colons (":"),
    or periods ("."), therefore "class" and "id" attributes should not contain
    these characters. They should be replaced with hyphens ("-"). Combined
    with HTML's requirements (the first character must be a letter; no
    "unicode", "latin1", or "escape" characters), this results in the
    ``[a-z](-?[a-z0-9]+)*`` pattern.

    .. _HTML 4.01 spec: http://www.w3.org/TR/html401
    .. _CSS1 spec: http://www.w3.org/TR/REC-CSS1
    """
    id = string.lower()
    if not isinstance(id, unicode):
        id = id.decode()
    id = id.translate(_non_id_translate_digraphs)
    id = id.translate(_non_id_translate)
    # get rid of non-ascii characters.
    # 'ascii' lowercase to prevent problems with turkish locale.
    id = unicodedata.normalize('NFKD', id).\
         encode('ascii', 'ignore').decode('ascii')
    # shrink runs of whitespace and replace by hyphen
    id = _non_id_chars.sub('-', ' '.join(id.split()))
    id = _non_id_at_ends.sub('', id)
    return str(id)

_non_id_chars = re.compile('[^a-z0-9]+')
_non_id_at_ends = re.compile('^[-0-9]+|-+$')
_non_id_translate = {
    0x00f8: u'o',       # o with stroke
    0x0111: u'd',       # d with stroke
    0x0127: u'h',       # h with stroke
    0x0131: u'i',       # dotless i
    0x0142: u'l',       # l with stroke
    0x0167: u't',       # t with stroke
    0x0180: u'b',       # b with stroke
    0x0183: u'b',       # b with topbar
    0x0188: u'c',       # c with hook
    0x018c: u'd',       # d with topbar
    0x0192: u'f',       # f with hook
    0x0199: u'k',       # k with hook
    0x019a: u'l',       # l with bar
    0x019e: u'n',       # n with long right leg
    0x01a5: u'p',       # p with hook
    0x01ab: u't',       # t with palatal hook
    0x01ad: u't',       # t with hook
    0x01b4: u'y',       # y with hook
    0x01b6: u'z',       # z with stroke
    0x01e5: u'g',       # g with stroke
    0x0225: u'z',       # z with hook
    0x0234: u'l',       # l with curl
    0x0235: u'n',       # n with curl
    0x0236: u't',       # t with curl
    0x0237: u'j',       # dotless j
    0x023c: u'c',       # c with stroke
    0x023f: u's',       # s with swash tail
    0x0240: u'z',       # z with swash tail
    0x0247: u'e',       # e with stroke
    0x0249: u'j',       # j with stroke
    0x024b: u'q',       # q with hook tail
    0x024d: u'r',       # r with stroke
    0x024f: u'y',       # y with stroke
}
_non_id_translate_digraphs = {
    0x00df: u'sz',      # ligature sz
    0x00e6: u'ae',      # ae
    0x0153: u'oe',      # ligature oe
    0x0238: u'db',      # db digraph
    0x0239: u'qp',      # qp digraph
}

# }}}



### Array utils

def merge(d, **kwds):

    """
    Recursive dictionary merge, ie. multi-level update.

    Set D[k] = kwds[...][k] where D is any dictionary nested within `d`.
    Works like dict.update but recurses and updates nested dictionaries
    first.
    """

    # merge sublevels before overwriting on update
    for k in kwds:
        if isinstance( kwds[k], dict ):
            if k in d:
                subl = kwds[k]
                kwds[k] = merge( d[k], **subl )
    d.update(kwds)
    return d

