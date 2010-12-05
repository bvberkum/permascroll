"""
Permascroll EDL format, similar to Translit EDL.

Status: primitive parser, working. Not much beyond that.


An EDL contains an ordered list of links with at most 4 parts.
Links are numbered or prefixed '@', and may run multiple lines,
including as many components as possible up to the next prefix. 

Its generic syntax is that of a bulleted or numbered list.
::

    ([-\*@]|[1-0]+\.) ...
      ...
      from ...
        ...
      to ...
      at ...

Where each ... is a reference or set of references.
The first set is a special component determining the links type.
The reference ':type' is built-in, and should be used to define additional 
link types. 

::

    @ : from :1.1~0.4 at 1~0.1


The '#' character marks a (one) line as comment and may appear anywhere.

Link types
-----------

@ : at 1.1.0.1.0.2
@ : from :1.1~0.4 to :1.1~0.1 at 2~0.1
@ :type from :1.5~0.4 at 2~0.1

Special links
-------------
@ : at 1.1
@ 

"""
import sys, re


CRLF = '\r\n'
LINK_re = r'([\@\*-])|([1-9][0-9]*\.)(?=\s+)'
TYPE_re = '(.+)'#(.+(?:\s+.+)*)'
FROM_re = '\s+from\s+(.+)'
TO_re = '\s+to\s+(.+)'
AT_re = '\s+at\s+(.+)'

for ptrn in 'link','type','from','to','at':
    mod = sys.modules[__name__]
    compiled = re.compile(getattr(mod, ptrn.upper()+'_re'),re.M|re.S)
    setattr(mod, ptrn.upper()+'', compiled)


class PEDLDoc(object):
    
    def __init__(self, **init):
        self.init(**init)

    def init(self, address=None, vstreams=[]):
        self.address = address
        self.vstreams = vstreams
   
    def append(self, obj):
        pass#print 'append', obj


class CLink(object):
    
    def __init__(self, typeset, fromset, toset, address=None):
        self.typeset = typeset
        self.fromset = fromset
        self.toset = toset
        self.address = address

        print typeset, fromset, toset, address


class PEDLParser(object):

    links = None
    nl = None

    def __init__(self, data=None, nl=CRLF):
        self.init(data, nl=nl)

    def init(self, data=None, nl=nl):
        self.nl = nl
        self.buf = []
        self.links = PEDLDoc()
        if data: self.feed(data)
        self.__clink = [None for i in xrange(0,5)]

    def feed(self, data):
        self.buf += [ l for l in data.split(self.nl) 
                if not l.lstrip().startswith('#') ]

    def parse(self, data=None): 
        if data:
            self.feed(data)
        for l in self._parse():
            self.links.append(CLink(*l[1:]))

    def finalize(self):
        self.parse()
        return self.links

    def parse_all(self, data=None):
        self.parse(data)
        return self.finalize()

    # Actual parser
    def _parse(self):
        while self.buf:
            yield self._parse_link()

    __clink = [None,None,None,None,None,] # marker, type, from, to, at
    def _parse_link(self):
        self._parse_ident()
        data_length = self._find_ident()
        #print 'TTTTT',data_length, ' '.join(self.buf)[:data_length]
        self._parse_components(data_length)
        cl = self.__clink
        self.__clink = [None,None,None,None,None,]
        if cl[2:4] == [-1,-1]:
            cl = [cl[0], ':transclude', cl[1], -1, cl[4]]
        if cl[0][0].isdigit():
            cl[0] = int(cl[0].strip('.'))
        return cl            

    def _find_ident(self):
        buf = ' '.join(self.buf)
        line_header = LINK.search(buf)
        if not line_header:
            return len(buf)
        return line_header.start()

    def _parse_ident(self):
        buf = ' '.join(self.buf)
        line_header = LINK.search(buf)
        h = max(line_header.groups())
        self.buf = [buf[line_header.end():]]
        self.__clink[0] = h

    def _parse_components(self, data_length):
        # parse backward, from data_length offset
        data = ' '.join(self.buf) 
        for idx, exp in (4,AT),(3,TO),(2,FROM),(1,TYPE):
            #print '---', idx
            #print data
            match = exp.search(data[:data_length])
            if match:
                #print data_length*'|'
                #print idx, data[match.start():data_length]
                s, e = match.span()
                #print s*'>'+(e-s)*'+'+(data_length-e)*'<'
                #print match.end()*'<'
                self.__clink[idx] = match.group(1).strip()
                data = (data[:match.start()] +' '+ data[data_length:]).rstrip()
                if data:                
                    self.buf = [data]
                else:
                    self.buf = []
                    break
                data_length -= match.end()-match.start()-1
            else:
                self.__clink[idx] = -1


class PEDLError(Exception):
    pass

class PEDLSyntaxError(PEDLError):
    pass

class IllegalLinkType(PEDLError):
    pass



def parse(edlstr, resolve=False):
    """
    """
    ls = []
    p = PEDLParser(edlstr, nl='\n')
    rawlinks = p.finalize()
    return rawlinks
    for l in rawlinks:
        print l
    return text, links, medialinks


if __name__ == '__main__':
    INIT = './2010/08/11/permascroll.init.edl'
    LD = './2010/08/11/permascroll.linkdoc.edl'

    #parse(open(INIT).read())

    p = PEDLParser(open(LD).read(), nl='\n')
    l = p.finalize()
    print
    print l

