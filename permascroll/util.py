# Stdlib {{{
import re
import traceback
import logging
import string 
import unicodedata
import urllib # }}}
# Third party {{{
from google.appengine.api import users # }}}
# Local {{{
#from permascroll.registry import components
from permascroll.exception import * # }}}


logger = logging.getLogger(__name__)

# Tumbler, Address and Offset as in x88 {{{
class Tumbler: 
    
    """A numbering system that permits addressing within documents
    so that material may be inserted at any point without renumbering."""

    def __init__(self, *args):
        """Construct from a list of tumbler digits or a string."""
        if len(args) == 1 and type(args[0]) is type("a"):
            self.digits = map(string.atol, string.split(args[0], "."))
        else:
            if len(args) == 1 and type(args[0]) is type([]):
                digits = args[0]
            else:
                digits = list(args)
            for digit in digits:
                if type(digit) not in [type(1), type(1L)]:
                    raise TypeError, repr(digits) + \
                        "is not a string or list of integers"
            self.digits = map(long, digits)

    def isroot(self):
        return len(self) == 1
    isroot = property(isroot)

    def __repr__(self):
        """Return a Python expression which will reconstruct this tumbler."""
        return self.__class__.__name__ + \
            "(" + string.join(map(repr, self.digits), ", ") + ")"

    def __str__(self):
        """Return the period-separated string representation of the tumbler."""
        return string.join(map(strl, self.digits), ".")

    def __getitem__(self, index):
        return self.digits[index]

    def __len__(self):
        return len(self.digits)

    def __nonzero__(self):
        for digit in self.digits:
            if digit != 0: return 1
        return 0

    def __add__(self, other):
        for i in range(len(self)):
            if other[i] != 0:
                return Tumbler(self.digits[:i] +
                               [self[i] + other[i]] +
                               other.digits[i+1:])
        for i in range(len(self), len(other)):
            if other[i] != 0:
                return Tumbler(self.digits + other.digits[len(self):])
        return Tumbler(self.digits)

    def __sub__(self, other):
        for i in range(min(len(self), len(other))):
            if self[i] < other[i]:
                raise ValueError, "%s is larger than %s" % (other, self)
            if self[i] > other[i]:
                return Tumbler([0] * i +
                               [self[i] - other[i]] +
                               self.digits[i+1:])
        if len(self) < len(other):
            raise ValueError, "%s is larger than %s" % (other, self)
        if len(self) > len(other):
            return Tumbler([0] * len(other) +
                           self.digits[len(other):])
        return NOWIDTH

    def __cmp__(self, other):
        """Compare two address tumblers or offset tumblers."""
        if not istype(Tumbler, other): return cmpid(self, other)
        for i in range(min(len(self), len(other))):
            if self[i] > other[i]: return 1
            if self[i] < other[i]: return -1
        if len(other) > len(self): return 1
        if len(other) < len(self): return -1
        return 0

    def __hash__(self):
        return hash(str(self))

class Address(Tumbler):
    """An address within the Udanax object space.  Immutable."""

    def __add__(self, offset):
        """Add an offset to a tumbler."""
        if not istype(Offset, offset):
            raise TypeError, "%s is not an offset" % repr(offset)
        return Address(Tumbler.__add__(self, offset).digits)

    def __sub__(self, address):
        """Subtract a tumbler from another tumbler to get an offset."""
        if not istype(Address, address):
            raise TypeError, "%s is not an address" % repr(address)
        return Offset(Tumbler.__sub__(self, address).digits)

    def split(self):
        """For a global address, return the docid and local components."""
        delim = len(self.digits) - 1
        while self.digits[delim] != 0: delim = delim - 1
        return Address(self.digits[:delim]), Address(self.digits[delim+1:])

    def split_all(self):
        "Split address into its tumbler components. "
        tumblers = []
        start = 0
        for i in range(0,len(self)):
            if self.digits[i] == 0:
                tumblers.append(self.digits[start:i])
                start = i+1
        if start:                
            tumblers.append(self.digits[start:])
        return map(Tumbler, tumblers)

    def globalize(self, other):
        """Return an global address given a local address into this one, a
        global width given a local width, or global span given a local span."""
        if istype(Address, other):
            return Address(self.digits + [0] + other.digits)
        if istype(Offset, other):
            return Offset([0] * len(self.digits) + [0] + other.digits)
        if istype(Span, other):
            return Span(self.globalize(other.start),
                        self.globalize(other.width))
        raise TypeError, "%s is not an address, offset, or span" % repr(other)

    def localize(self, other):
        """Return a local address given a global address under this one, a
        local width given a global width, or local span given a global span."""
        if istype(Address, other):
            if len(other) > len(self) and \
               self.digits[:len(self)] + [0] == other.digits[:len(self)+1]:
                return Address(other.digits[len(self)+1:])
            else:
                raise ValueError, "%s is not within %s" % (other, self)
        if istype(Offset, other):
            if [0] * len(self) + [0] == other.digits[:len(self)+1]:
                return Offset(other.digits[len(self)+1:])
            else:
                raise ValueError, "%s extends outside of %s" % (other, self)
        if istype(Span, other):
            return Span(self.localize(other.start),
                        self.localize(other.width))
        raise TypeError, "%s is not an address, offset, or span" % repr(other)

class Offset(Tumbler):
    """An offset between addresses in the Udanax object space.  Immutable."""

    def __add__(self, offset):
        """Add an offset to an offset."""
        if not istype(Offset, offset):
            raise TypeError, "%s is not an offset" % repr(offset)
        return Offset(Tumbler.__add__(self, offset).digits)

    def __sub__(self, offset):
        """Subtract a tumbler from another tumbler to get an offset."""
        if not istype(Offset, offset):
            raise TypeError, "%s is not an offset" % repr(offset)
        return Offset(Tumbler.__sub__(self, offset).digits)

class Span:
    """A range of Udanax objects in the global address space.  Immutable."""

    def __init__(self, start, other):
        """Construct from either a starting and ending address, or
        a starting address and a width offset."""
        if not istype(Address, start):
            raise TypeError, "%s is not an address" % repr(start)
        self.start = start
        if istype(Address, other):
            self.width = other - start
        elif istype(Offset, other):
            self.width = other
        else:
            raise TypeError, "%s is not an address or offset" % repr(other)

    def __repr__(self):
        return "Span(" + repr(self.start) + ", " + repr(self.width) + ")"

    def __str__(self):
        return "<Span at " + str(self.start) + " for " + str(self.width) + ">"

    def __len__(self):
        return int(self.width.digits[-1])

    def __nonzero__(self):
        return self.width and 1 or 0

    def __cmp__(self, other):
        """Compare two spans (first by starting address, then by width)."""
        if not istype(Span, other): return cmpid(self, other)
        cmp = self.start.__cmp__(other.start)
        if cmp != 0: return cmp
        return self.width.__cmp__(other.width)

    def __hash__(self):
        return hash((self.start, self.width))

    def __and__(self, span):
        """Return the intersection of this span with another span."""
        if istype(VSpan, span):
            span = span.globalize()
        elif not istype(Span, span):
            raise TypeError, "%s is not a span" % repr(span)
        if self.start in span:
            if self.end in span:
                return Span(self.start, self.width)
            else:
                return Span(self.start, span.end)
        elif self.end in span:
            return Span(span.start, self.end)
        elif span.start in self:
            return Span(span.start, span.width)
        else:
            return Span(NOWHERE, NOWIDTH)

    def contains(self, spec):
        """Return true if the given spec lies entirely within this span."""
        if istype(Address, spec):
            return self.start <= spec < self.end()
        elif istype(Span, spec):
            return self.start <= spec.start <= spec.end() <= self.end()
        elif istype(VSpan, spec):
            return self.contains(spec.globalize())
        else:
            raise TypeError, "%s is not an address or span" % repr(spec)

    def write(self, stream):
        """Write a span to an 88.1 protocol stream."""
        self.start.write(stream)
        self.width.write(stream)

    def end(self):
        """Return the first address after the start not in this span."""
        return self.start + self.width

    def localize(self):
        """Return this span as a vspan within one document."""
        docid, local = self.start.split()
        return VSpan(docid, docid.localize(self))

class VSpan:
    """A range within a given document.  Immutable."""

    def __init__(self, docid, span):
        """Construct from a document id and a local span."""
        if not istype(Address, docid):
            raise TypeError, "%s is not a document address" % repr(docid)
        if not istype(Span, span):
            raise TypeError, "%s is not a span" % repr(span)
        self.docid = docid
        self.span = span

    def __repr__(self):
        return "VSpan(" + repr(self.docid) + ", " + repr(self.span) + ")"

    def __str__(self):
        return "<VSpan in %s at %s for %s>" % (
            self.docid, self.span.start, self.span.width)

    def __cmp__(self, other):
        """Compare two vspans (first by document address, then by span)."""
        if not istype(VSpan, other): return cmpid(self, other)
        cmp = self.docid.__cmp__(other.docid)
        if cmp != 0: return cmp
        return self.span.__cmp__(other.span)

    def __hash__(self):
        return hash((self.docid, self.span))

    def __and__(self, span):
        """Return the intersection of this span with another span."""
        return self.globalize() & span

    def start(self):
        return self.docid.globalize(self.span.start)

    def end(self):
        return self.docid.globalize(self.span.end())

    def contains(self, spec):
        """Return true if the given spec lies entirely within this span."""
        return self.globalize().contains(spec)

    def globalize(self):
        """Return this vspan as a span with a global starting address
        and width within this document."""
        return Span(self.docid.globalize(self.span.start),
                    self.docid.globalize(self.span.width))


NOWHERE = Address()
NOWIDTH = Offset()

def strl(longnum):
    """Convert a long integer to a string without the trailing L."""
    strval = str(longnum)
    if strval[-1] not in string.digits:
        return strval[:-1]
    return strval

def istype(klass, object):
    """Return whether an object is a member of a given class."""
    return klass == object.__class__


# }}}

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

def conv_tumbler(arg): # {{{
    t = Tumbler(arg)
    return t
    # }}}

def conv_span(arg):
    assert arg.count('~') == 1, arg
    tumblers = arg.split('~')
    assert tumblers[1].startswith('0'), tumblers[1]
    start = Address(tumblers[0])
    offset = Offset(tumblers[1])
    return Span(start, offset)

def conv_span_or_address(arg):
    if '~' in arg:
        return conv_span(arg)
    else:
        return conv_tumbler(arg)

def conv_blob(arg):
    pass # TODO
    return arg

def conv_mime(arg):
    pass # TODO
    return arg


data_convertor = {
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
    'span': conv_span,
    'span_or_address': conv_span_or_address,
    'cslist': cs_list,
    'blob': conv_blob,
    'mime': conv_mime,
}

def get_convertor(type_name):
    if ',' in type_name:
        complextype_names = type_name.split(',')
        basetype = data_convertor[complextype_names.pop(0)]
        return basetype + tuple([ data_convertor[n] 
                for n in complextype_names ])
    else:
        return data_convertor[type_name]

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

def mime(method):
    mediatype = 'text/plain'
    #global mediatypes
    #@functools.wraps(method)
    def mime_handler(self, *args, **kwds):
        media = method(self, *args, **kwds)
        assert isinstance(media, basestring), type(media)
        #assert mediatype in mediatypes,\
        #        "Unknown mediatype %r.  " % mediatype
        logger.info("Serving %s bytes as %s", len(media), mediatype)
        self.response.headers['MIME-Version'] = '1.0'
        self.response.headers['Content-Length'] = "%d" % len(media)
        self.response.headers['Content-Type'] = mediatype
        #self.response.headers['Content-ID']
        self.response.out.write(media)
    return mime_handler

def catch(method):
    def error_resp_handler(self, *args, **kwds):
        data = None
        try:
            data = method(self, *args, **kwds)
        except Exception, e:
            self.response.set_status(500)
            self.response.out.write(repr(e))
            traceback.print_exc()
        if not data: data = ''
        return str(data)
    return mime(error_resp_handler)

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

    Unnamed fields are positional arguments from the URL path, matched by
    the handler dispatcher.

    Named fields are taken from the GET query or the (urlencoded) POST entity.
    Field names are converted to name IDs, but the '-' are replaced by '_' 
    (to convert the name ID to a Python identifier).

    '_' is treated as a special convertor to ignore an arg/kwd.

    `qwd_method` may be 'auto', 'both', or 'GET' or 'POST'. Default is 'auto'.

    .. raw:: python

       class ExampleRequestHandler:
           pattern = '^/version/([0-9]+)/([^/]+)/(0|1)/([^\.]+)(\.test)$'

           @http(':int',':_',':bool',':unicode',':ext', 'kwd1:unicode', 'kwd2:text', test='pickle')
           def myhandle(self, v, arg1, arg2, arg3, kwd1=None, **otherkwds):
               pass
    """
    qwd_method = kwds.get('qwd_method', 'auto')
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
                    logger.warning(e)
                # always replace argument
                args = args[:idx-ignorespecs] + (value,) + args[idx-ignorespecs+1:]
            logger.debug("Converted arguments %s", args)
            # take keyword arguments from GET query or POST entity
            items = []
            m = self.request.method
            if qwd_method == 'auto' and m in ('POST','GET'):
                items = getattr(self.request, m).items()
            elif qwd_method == 'both' or qwd_method.lower() == 'get':
                items += self.request.GET.items()
            if qwd_method == 'both' or qwd_method.lower() == 'post':
                items += self.request.POST.items()
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
                        logger.warning(e)
                    if value: # update/add keyword
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


def make_id(string):
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

