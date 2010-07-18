"""Configuration
"""

PATH = '2009/12/31/permascroll'

TEMPLATES = {
    #'main': './' + PATH + '.main.xhtml.dj.tpl',
    'base': 'permascroll.base.xhtml.dj.tpl',
    'main': 'permascroll.main.xhtml.dj.tpl',
    'node': 'permascroll.node.xhtml.dj.tpl',
    'http-error': 'permascroll.http-error.xhtml.dj.tpl',
}

DATETIME = "%Y-%m-%d %H:%M:%S"
#ISODATETIME = "%Y-%m-%dT%H:%M:%SZ"

# exact ref prefixes
P_UUID = 'urn:uuid:'
P_HTTPS = 'https:'
P_HTTP = 'http:'
P_FILE_N = 'file://'
P_FILE = 'file:'
P_TUMBLER = 'tumbler:'
P_HASH = 'urn:hash:'

HASH = {
	'Reference': 'md5',
	'Content': 'sha1'
}

DATE_HEADERS = (
    'Expires',
      #..
    'Last-Modified',
      #..
)

HEADERS = DATE_HEADERS + (
#    'Allow', #: GET, HEAD, ...
      #Supported methods for resource
#    'Content-Encoding', #: (gzip|..)
      #Contents have been encoded if not 'identity'
    'Content-Language',
      #A list of natural languages used by entity
#    'Content-Length',
      #The decimal number of octets
    'Content-Location',
      #A URI ref. for the entity (URL)
    'Content-MD5',
      #A base64 encoded MD5 digest [RFC 1864]
    'Content-Range', # 123-45/`length`
      #Body represents partial entity, applied to range.
      #Length '*' if undetermined
    'Content-Type',
      #Media type for entity
)

HOST = 'permascroll.appspot.com'
