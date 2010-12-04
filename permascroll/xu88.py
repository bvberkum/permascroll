import string 

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
        if not isinstance(other, Tumbler): return cmpid(self, other)
        for i in range(min(len(self), len(other))):
            if self[i] > other[i]: return 1
            if self[i] < other[i]: return -1
        if len(other) > len(self): return 1
        if len(other) < len(self): return -1
        return 0

    def __hash__(self):
        return hash(str(self))

    def write(self, stream):
        """Write a tumbler to an 88.1 protocol stream."""
        exp = 0
        for exp in range(len(self.digits)):
            if self.digits[exp] != 0: break
        dump = "%d" % exp
        for digit in self.digits[exp:]:
            dump = dump + "." + strl(digit)
        stream.write(dump + "~")

class Address(Tumbler):
    """
    An address within the Udanax object space. Immutable.
    The address is represented as a multiple tumblers in one Tumbler instance,
    each component separated by a zero.
    """
    def __init__(self, *args, **kwds):
        if args and isinstance(args[0], Tumbler):
            args = ['.0.'.join(map(str, args))]
        Tumbler.__init__(self, *args, **kwds)

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
        return Address(self.digits[:delim]), \
                Address(self.digits[delim+1:])

    def parent(self):
        """Return the address, excluding the lowest component. """
        if 0 in self.digits:
            return Address(*self.split_all()[:-1])

    def depth(self):
        "Return number of components in Address, ie. len(self.split_all()). "
        return self.digits.count(0)+1

    def paths(self):
        "Return a list with the Address for each component, top down."
        cp = []
        ccp = Address()
        for t in self.split_all():
            ccp = ccp.subcomponent(t)
            cp.append(ccp)
        return cp

    def subcomponent(self, component):
        """Append component. """
        if isinstance(component, (Tumbler, str, int, long)):
            if self and component:
                return Address(str(self) +'.0.'+ str(component))
            elif component:
                return Address(str(component))
        else:
            raise TypeError, "Need tumbler: %s" % type(component)

    def split_all(self):
        "Split 0-separated address into its tumbler components. "
        tumblers = []
        # add every component ended by a '.0.'
        start = 0
        for i in range(0, len(self)):
            if self.digits[i] == 0:
                tumblers.append(self.digits[start:i])
                start = i+1
        if start: # append last component
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

def cmpid(a, b):
    """Compare two objects by their Python id."""
    if id(a) > id(b): return 1
    if id(a) < id(b): return -1
    return 0

# }}}


