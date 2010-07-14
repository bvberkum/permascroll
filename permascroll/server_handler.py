"""
Server handler, handlers for URL endpoints.
Together with Form handler contains main HTTP serving routines.
"""
import wsgiref
from cgi import parse_qs
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
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

        self.response.out.write(template.render(
                rc.TEMPLATES[tpl], data))

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


class AbstractNodeHandler(AbstractHandler):

    def update(self, *tumblers, **props):
        node = self.fetch(*tumblers)
        api.update_node(node, **props)
        return node

    def delete(self, *tumblers):
        node = api.get(*tumblers)
        node.delete()
        return node


# Concrete handlers

class NodeHandler(AbstractNodeHandler):

    @util.catch
    @util.http_q(':tumbler',':tumbler',':tumbler')
    def get(self, *tumblers):
        "Get the Node at address node(/channel(/entry)). "
        v = api.get(*tumblers)
        logger.info(v)
        return v

    @util.catch
    @util.http_q(':tumbler',':tumbler',':tumbler','title:unicode')
    def post(self, *tumblers, **props):
        "Create new Node under address. "
        #logging.info(tumblers)
        #self.response.out.write('node: '+`tumblers`)
        tcnt = len(tumblers)
        newcroot = self.request.uri.endswith('/')
        kind = 'node'
        if tcnt == 1:
            if newcroot: kind = 'channel'
        elif tcnt == 2:
            if not newcroot: kind = 'channel'
            else: kind = 'entry'
        elif tcnt == 3:
            if not newcroot: kind = 'entry'
            else: assert False, "route error"
        return api.create_node(kind=kind, *tumblers, **props)

    @util.catch
    @util.http_q(':tumbler',':tumbler',':tumbler','title:unicode')
    def put(self, *tumblers, **props):
        "Update the Node at address `tumbler`. "
        return self.update(*tumblers, **props)

    @util.catch
    @util.http_q(':tumbler',':tumbler',':tumbler')
    def delete(self, *tumblers):
        "Delete the Node at address `tumbler`. "
        return self.delete_(*tumblers)


class QueryHandler(AbstractHandler):

    @util.catch
    @util.http_q(':span_or_address', ':span_or_address', ':span_or_address')
    def get(self, *args):
        logging.info(args)
        self.response.out.write('q:'+`args`)
        return
        "Get the Nodes at address `tumbler`. "
        return api.get(t_node, t_channel, t_item)


class ContentHandler(AbstractNodeHandler):

    @util.catch
    @util.http_q(':tumbler',':tumbler',':tumbler',':span_or_address')
    #def get(self, t_node, t_channel, t_item, t_v):
    def get(self, *args):
        logging.info(args)
        self.response.out.write('content: '+`args`)
    #    "Get the Content at address `tumbler`. "
    #    return api.deref(t_node, t_channel, t_item, t_vrange)

    @util.catch
    @util.http_q(':tumbler',':tumbler',':tumbler','data:blob','type:mime')
    def post(self, t_node, t_channel, t_item, **props):
        "Create a Content under address `tumbler`. "
        return self.create(base_tumbler, **props)

    @util.catch
    @util.http_q(':tumbler',':tumbler',':tumbler',':span',
            'data:blob', 'type:mime')
    def put(self, t_node, t_channel, t_item, t_vrange, **props):
        "Update the Content at address `tumbler`. "
        return self.update(t_node, t_channel, t_item, t_vrange, **props)


class FrontPage(AbstractHandler):

    def options(self):
        return

    def head(self):
        return

    def get(self):
        self.print_tpl(
                content_id='frontpage',
                title='Transfinite frantic space',
                doc_body='<p class="first">Welcome, the permanent scroll is %i virtual '
                'positions and growing.  '
                '</p><p>Positions are accumulated from %i distinct items within %i subspaces. '
                'Among the items, %i are actual unique records.  '
                'There is neither <em>transclusion</em> nor <em>parallel markup</em>&mdash;'
                'All Your Bytestreams Are Belong To <del>XUL</del><ins>HTML</ins>.  </p>'
                ' <form id="_home_nav" method="GET"> '
                ' <input type="hidden" id="feed-URI" value="/feed/%s" /> '
                ' <input type="hidden" id="find-entity" value="/?id=%s" /> '
                '<p>Visit your <a href="/user" title="User page">homepage</a> to list your subspace, '
                'or enter a <input id="feed-number" size="11" value="feed number" type="text" /> (with or without entry number) '
                'or an <input id="entity-ID" size="9" maxlength="500" value="entity ID" type="text" /> to '
                '<input type="submit" value="get" /> the corresponding page.  '
                '</p>'
                ' </form> ',
                header='<p class="crumbs">Permascroll &raquo; Frontpage </p>',footer='' )


class Permascroll(AbstractHandler):

    def get(self):

        """
        Serve entity/record.
        """

        {
            'home-url': '...',
            'index': 23,
            'parent': 4,
            'length': 123,
        }
        self.print_tpl(
                doc_body='Greetings, there are %i feeds.' % model.get_count('feed'),
                header='',footer='' )

    def post(self):

        """
        Append a new space
        """

        validator = model.validate(self.request.body, self.request.headers,
                model.Feed)
        if validator.next():
            record = validator.next()
            # assign new index
            count = model.get_count('feed')
            record.index = count+1
            record.put()
        else:
            self.error(500)
            print validator.next()


class FeedHandler(AbstractHandler):

    def get(self, idx_feed=None, idx_entry=None):
        if idx_feed:
            feed = self.get_feed(idx_feed)
        else:
            pass

    def get_feed(self, idx_feed):
        feed = model.Space.all().filter('index=', int(idx_feed)).fetch(1)
        if not feed:
            self.print_not_found(doc_body='There is no feed at index <span '
                    'class="feed index">%s</span>.' % idx_feed)
        return feed

    def post(self, idx_feed=None):

        """
        Accept a new feed or entry.
        """

        kind = model.Space
        feed = None
        if idx_feed:
            feed = self.get_feed(idx_feed) # return 404
            if not feed: return
            kind = model.Item

        validator = model.validate(
                    self.request.body, self.request.headers, kind)

        if validator.next():
            record = validator.next()
            # assign new index
            model.increment(kind.node_kind)
            record.index = model.get_count(kind.node_kind)
            if feed:
                record.parent_id = feed.node_id
            record.put()

            self.response.out.write("Recorded new %s: %s\n" % (kind, record.index))
            self.response.out.write("Sharded counter report %s instances." %
                model.get_count(kind.node_kind))
        else:
            self.error(500)

        self.response.out.write(validator.next())

    def put(self, idx_feed, idx_entry=None):

        """
        Accept a new or updated feed or entry record.
        """

        kind = model.Space
        if idx_entry:
            kind = model.Item
            feed = self.get_feed(idx_feed)

        count = model.get_count(kind.node_kind)

        if idx_entry:
            pass

        elif idx_feed:
            if count+1 >= idx_feed:
                validator = model.validate(self.request.body, self.request.headers, kind)
                if validator.next(): # Validated?
                    record = validator.next()
                    # new record
                    if not record.index:
                        record.index = count+1
                    # update or create feed
                    record.put()
                else:
                    self.error(500)
                    print validator.next()

            else:
                self.print_not_found()

class EntryHandler(AbstractHandler):

    def get(self, idx_feed, idx_entry):

        """
        Serve entity.
        """

        entry = model.Entry.all().filter('index=', int(idx_entry)).fetch(1)
        if not entry:
            self.print_not_found(doc_body='There is no entry at index %s for feed number %s.' %
                    (idx_entry, idx_feed))
            return

        {
            'content-type': '...',
            'content': '...'
        }
        feed = Feed.fetch(int(idx_feed))
        entry = Entry.fetch(int(idx_entry))

        #print entry.content

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

        def _redir(self):
            if append:
                path = self.request.uri + path
            self.redirect(path, permanent)

        def get(self):
            self._redir()

        def post(self):
            self._redir()

    return ReDir


# URL - Handler mapping

tumbler = '[1-9][0-9]*(?:\.[1-9][0-9]*)*'
offset = '%7E0\.[1-9][0-9]*'
endpoints = [
    ('/node', reDir('/node/')),
    # nodes
    (r'/node/', NodeHandler),
    (r'/node'+1*'/(%(tumbler)s)/?' % locals(), NodeHandler),
    (r'/node'+2*'/(%(tumbler)s)/?' % locals(), NodeHandler),
    (r'/node'+3*'/(%(tumbler)s)/?' % locals(), NodeHandler),
    #(r'/node/(%(tumbler)s)' % locals(), ReDir),
    #(r'/node/(%(tumbler)s)/(%(tumbler)s)' % locals(), ReDir),
    #(r'/node'+''.join(2*'/(%(tumbler)s)')+'/(%(tumbler)s)', ReDir),
    # node- range queries
    (r'/node/(%(tumbler)s%(offset)s)' % locals(), QueryHandler),
    (r'/node/(%(tumbler)s)/(%(tumbler)s%(offset)s)' % locals(), QueryHandler),
    (r'/node/(%(tumbler)s)/(%(tumbler)s)/(%(tumbler)s%(offset)s)' % locals(), QueryHandler),
    # content and content-range
    (r'/node/(%(tumbler)s)/(%(tumbler)s)/(%(tumbler)s)/(%(tumbler)s%(offset)s)' % locals(),
        ContentHandler),

    #('/feed', reDir('/feed/')),
    #('/feed/', FeedHandler),
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
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
