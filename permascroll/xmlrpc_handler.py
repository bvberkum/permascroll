from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import xmlrpcserver, StringIO, traceback, logging


class XMLRPCApp:
    def __init__(self):
        pass

    def getName(self, meta):
        return 'Permascrol XML-RPC'

class MultiCallXMLRPCServer(xmlrpcserver.XmlRpcServer):
    def __init__(self, *args, **kwds):
        xmlrpcserver.XmlRpcServer.__init__(self, *args, **kwds)
        self.register('system.multicall', self.system_multiCall)
 
    def system_multiCall(self, meta, methods):
        """Implements the XML-RPC Multi-call functionality"""

        results = []

        for m in methods:
            rpccall = m['methodName']
            params = m['params']
            results.append([self.resolve(rpccall)(meta, *params)])

        return results

class XMLRPCHandler(webapp.RequestHandler):
    rpcserver = None

    def __init__(self):
        self.rpcserver = MultiCallXMLRPCServer()
        app = XMLRPCApp()
        self.rpcserver.register_class('app', app)

    def post(self):
        request = StringIO.StringIO(self.request.body)
        request.seek(0)
        response = StringIO.StringIO()
        try:
            self.rpcserver.execute(request, response, None)
        except Exception, e:
            logging.error('Error executing: '+str(e))
            for line in traceback.format_exc().split('\n'):
                logging.error(line)
        finally:
            response.seek(0)

        rstr = response.read()
        self.response.headers['Content-type'] = 'text/xml'
        self.response.headers['Content-length'] = "%d"%len(rstr)
        self.response.out.write(rstr)


endpoints = [
    ('/api', XMLRPCHandler)
]
application = webapp.WSGIApplication( endpoints,
                                     debug=True)


# Main entry point
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

