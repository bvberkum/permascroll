"""
Server handler, handlers for URL endpoints.
Together with Form handler contains main HTTP serving routines.
"""
import uuid
import wsgiref
from cgi import parse_qs
import logging

from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

from permascroll import rc, model, util, api
from permascroll.exception import *


logger = logging.getLogger(__name__)

class AbstractHandler(webapp.RequestHandler):

    """
    Abstract request handler.
    """

    DATA = {
        'django_version': template.django.VERSION[1],
        'permascroll_version': '0.1',
        'title': 'Permascroll',
        'rc': rc,
        'content_id': '@@@TODO@@@',
        'closure': '<span class="version">Permascroll/0.1</span>',
        'doc_body' :
"""<pre>This is the body speaking...                                 79 characters wide
</pre>
<pre>This is the body speaking...                                 79 characters wide
</pre>
""",
        'footer': """<p>Footer</p>
<pre>                                                                     also 93 characters wide
</pre>""",
        'header': """<pre>This is the header speaking...                                            93 characters wide
                                                                            Whats with that?
</pre>"""
    }

    def print_tpl(self, **kwds):
        "Helper function for outputting template formatted from keywords."

        data = util.merge( AbstractHandler.DATA.copy(), **kwds )

        tpl = 'main'
        if 'template' in data:
            tpl = data['template']
            del data['template']

        output = template.render(
                rc.TEMPLATES[tpl], data)
        self.response.out.write(output)

        etag = uuid.uuid4()
        #model.page_cache[etag] = output
        return etag

    def print_form(self, fields=[], form={}, **kwds):
        "Helper function for outputting a form"

        data = util.merge( AbstractHandler.DATA.copy(), **kwds )

        if fields:
            form.update({'fields': fields})

        if form:
            data['form'].update( form )

        self.response.out.write(template.render(
            rc.TEMPLATES['form'], data))

    def print_not_found(self, **kwds):
        self.error(404)
        kwds = util.merge( kwds, **{'title':'Document Not Found','doc_info':{'HTTP Status': 404}} )

        data = util.merge( AbstractHandler.DATA.copy(), **kwds )

        self.response.out.write(template.render(
            rc.TEMPLATES['http-error'], data))

    def is_cached(self, etag):
        return etag in model.page_cache

    def invalidate_cache(self, etag):
        del model.page[cache]


# Concrete handlers

class TumblerTestHandler(webapp.RequestHandler):

    @util.catch
    @util.http_q(':tumbler',':span_or_address')
    def get(self, *args):
        logging.info(args)
        self.response.out.write('TumblerTestHandler: '+`args`)


class NodeHandler(AbstractHandler):

    @util.conneg
    @util.http_q(':address')
    def get(self, t_addr):
        "Get the Node at address node(/channel(/entry)). "
        v = api.get(t_addr)
        return v

    @util.catch
    @util.http_q(':address','title:unicode')
    def post(self, t_addr=None, **props):
        "Create new Node under address. "
        # determine node type based on components
        kind = 'node'
        if t_addr:
            tcnt = t_addr.digits.count(0)+1
            newcroot = self.request.uri.endswith('/')
            logger.info([t_addr, tcnt, newcroot])
            if tcnt == 1:
                if newcroot: kind = 'channel'
            elif tcnt == 2:
                if not newcroot: kind = 'channel'
                else: kind = 'entry'
            elif tcnt == 3:
                if not newcroot: kind = 'entry'
                else: assert False, "route error"
        return api.create(t_addr, kind=kind, **props)

    @util.catch
    @util.http_q(':span_or_address','title:unicode')
    def put(self, span_or_address, **props):
        "Update the Node at address `tumbler`. "
        assert not hasattr(span_or_address, 'start'), "Span not supported?"
        return api.update(span_or_address, **props)

    #@util.catch
    #@util.http_q(':tumbler',':tumbler',':tumbler')
    #def delete(self, *tumblers):
    #    "Delete the Node at address `tumbler`. "
    #    return api.delete_node(*tumblers)


class QueryHandler(AbstractHandler):

    @util.catch
    @util.http_q(':span_or_address')
    def get(self, span_or_address):
        """Print nodes at address or range. """
        if hasattr(span_or_address, 'start'):
            return '\r\n'.join(map(str, api.list_nodes(span_or_address)))
        else:
            return str(api.get(span_or_address))


class ContentHandler(AbstractHandler):

    @util.catch
    @util.http_q(':span_or_address')
    def get(self, span_or_address):
        "Print content for nodes at address or range. "
        return api.deref(span_or_address)

    @util.catch
    @util.http_q(':address','data:blob','type:str')
    def post(self, address, type=None, data=None):
        "Append content under address `tumbler`. "
        if not type: type='literal'
        ccnt = len(address.split_all())
        assert 3 <= ccnt <= 4, address
        if ccnt == 3:
            address = address.subcomponent(
                    {'literal':'1','link':'2','image':'3'}[type])
        assert data, (self.request.uri, data)
        return api.append(address, data=data)

    #@util.catch
    #@util.http_q(':tumbler',':tumbler',':tumbler',':span',
    #        'data:blob', 'type:mime')
    #def put(self, t_node, t_channel, t_item, t_vrange, **props):
    #    "Update the Content at address `tumbler`. "
    #    return self.update(t_node, t_channel, t_item, t_vrange, **props)

    # def delete(self, ):
    #   """Blank data at address or range. """
    # XXX: but does not delete resource so not compatible with HTTP


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    """
    Like ContentHandler, but push content to Google's blobstore.
    Accepts literals, images and audio.
    """

    @util.catch
    @util.http_q(':address')
    def post(self, address):
        "Accepts multipart/form-data"
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        res_key = blob_info.key()
        #self.redirect('/%s' % blob_info.key())


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """
    """
    @util.catch
    @util.http_q(':address')
    def get(self, address):
        res_key = api.resource_key(address)
        blob_info = blobstore.BlobInfo.get(res_key)
        self.send_blob(blob_info)


class FrontPage(AbstractHandler):

    def options(self):
        return

    def head(self):
        return

    def get(self):
        #status = model.get_status()
        #if status.count_updated:
        #    self.invalidate_cache('frontpage')
        #client_etag = None
        #if 'etag' in self.request.headers:
        #    client_etag = self.request.headers['etag']
        #if self.is_cached(client_etag):
        #    self.response.set_status(304)
        #    #self.print_cached(client_etag):
        #    #self.response.headers['ETag'] = client_etag
        #else:
        etag = self.print_tpl(
                    content_id='frontpage',
                    title='Transfinite frantic space',
                    doc_body=''
    #                '<h1 class="title">Transfinite frantic space</h1> '
                    '<h1>Welcome to node <kbd>1.1</kbd>, </h1> '
                    '<p class="first">'
                    'this permascroll is %i virtual positions and growing. </p> '
                    '<ul>'
                    '<li><a href="/node/1.1/1">Visit first directory.</a></li>'
                    '<li><a href="/node/1.1/1/2">Show linktypes defined for this docuverse.</a></li>'
                    '</ul>'
                    '<p>Positions are accumulated from %i distinct entries '
                    'within %i directories. '
    #                'Among the entries, %i are actual unique records.  '
                    'Entries contain at most 2 distinct, '
                    '<strong>append-only</strong> virtual data streams; one for text and one for links. '
    #                'Data is stored by Google blobstore. '
                    'There is neither <em>transclusion</em> nor <em>parallel markup</em>&mdash;'
                    'All Your Bytestreams Are Belong To <del>XUL</del><ins>HTML</ins>.  '
                    '</p>' % (
                        model.get_count('virtual'), model.get_count('entry'),
                        model.get_count('channel'),
                        ),
    #                ' <form id="_home_nav" method="GET"> '
    #                ' <input type="hidden" id="feed-URI" value="/feed/%s" /> '
    #                ' <input type="hidden" id="find-entity" value="/?id=%s" /> '
    #                '<p>Visit your <a href="/user" title="User page">homepage</a> to list your subspace, '
    #                'or enter a <input id="feed-number" size="11" value="feed number" type="text" /> (with or without entry number) '
    #                'or an <input id="entity-ID" size="9" maxlength="500" value="entity ID" type="text" /> to '
    #                '<input type="submit" value="get" /> the corresponding page.  '
    #                '</p>'
    #                ' </form> ',
                    header='<p class="crumbs">Permascroll &raquo; Frontpage </p>',footer='' )
        #    self.response.headers['ETag'] = etag
        



class FeedBrowser(AbstractHandler):

    def get(self, ID_feed):
        self.print_tpl(
                doc_body='..here be a browser...',
                header='<p class="crumbs">Permascroll &raquo; Feedbrowser </p>',
                footer='' )

class HomePage(AbstractHandler):

    def get(self, ID_user):
        if not ID_user:
            ID_user = 'anonymous'
        self.print_tpl(
                doc_body='..here be authenticated access...',
                header='<p class="crumbs">Permascroll &raquo; User </p>',footer='User: %s' % ID_user )

class NotFoundPage(AbstractHandler):

    def get(self):
        host = self.request.headers.get('host', 'noname')
        who = wsgiref.util.request_uri(self.request.environ)
        self.print_not_found(
                doc_body='Sorry, but URL &lt;<a href="%s" title="This '
                'page.">%s</a>&gt; is not recognized by this host (%s).' %
                (who, who, host))
        #self.request.path)


def reDir(path, permanent=True, append=False):

    class ReDir(webapp.RequestHandler):

        def _redir(self, path):
            if append:
                path = self.request.uri + path
            self.redirect(path, permanent)

        def get(self):
            self._redir(path)

        def post(self):
            self._redir(path)

    return ReDir


# URL - Handler mapping

d = dict(
        sep = r'(?:/|\.0\.)',
        tumbler = '[1-9][0-9]*(?:\.[1-9][0-9]*)*',
        offset = '%7E0\.[1-9][0-9]*'
)
endpoints = [
    ('/node', reDir('/node/')),
    # nodes
    (r'/node/', NodeHandler),
    (r'/node/(%(tumbler)s)/?' % d, NodeHandler),
    (r'/node/(%(tumbler)s%(sep)s%(tumbler)s)/?' % d, NodeHandler),
    (r'/node/(%(tumbler)s%(sep)s%(tumbler)s%(sep)s%(tumbler)s)' % d, NodeHandler),
    # node- range queries
    (r'/node/(%(tumbler)s%(offset)s)' % d, QueryHandler),
    (r'/node/(%(tumbler)s%(sep)s%(tumbler)s%(offset)s)' % d, QueryHandler),
    (r'/node/(%(tumbler)s%(sep)s%(tumbler)s%(sep)s%(tumbler)s%(offset)s)' % d, 
        QueryHandler),
    # content and content-range
    (r'/node/(%(tumbler)s%(sep)s%(tumbler)s%(sep)s%(tumbler)s%(sep)s?'
      '(?:%(tumbler)s%(sep)s%(tumbler)s)?(?:%(offset)s)?)' % d, 
        ContentHandler),
    # TODO:
    #(r'/node/(%(tumbler)s%(sep)s%(tumbler)s%(sep)s%(tumbler)s%(sep)s'
    #  '(?:%(tumbler)s%(sep)s)?)upload' % d, 
    #    UploadHandler),
    #(r'/node/(%(tumbler)s%(sep)s%(tumbler)s%(sep)s%(tumbler)s%(sep)s'
    #  '%(tumbler)s%(sep)s)download' % d, 
    #    DownloadHandler),

    (r'/.test/(%(tumbler)s%(sep)s%(tumbler)s%(offset)s)' % d, 
        TumblerTestHandler),

    #(r'/feed/([1-9][0-9]*)/entry/([1-9][0-9]*)/?', EntryHandler),
    #(r'/feed/([1-9][0-9]*)/?', FeedHandler),
    #(r'/feed/([1-9][0-9]*|index).html', FeedBrowser),
#    ('xmlrpc', XMLRPCApp),
    #('/user', reDir('/user/')),
    #('/user/(.*)', HomePage),
    ('/', reDir('/frontpage')),
    ('/frontpage', FrontPage),
    ('/.*', NotFoundPage)
]
application = webapp.WSGIApplication( endpoints,
                                     debug=True)

# Main entry point
def main():
    logger.info("Library path: %s", rc.LIB)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
