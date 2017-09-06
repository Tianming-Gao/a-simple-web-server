import os
from http.server import HTTPServer,BaseHTTPRequestHandler


class BaseCase(object):
    '''Parent for case handler'''

    '''Parent for case handlers.'''
    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):

        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'


class CaseNoFile(BaseCase):

    def test(self,handler):
        return not os.path.exists(handler.full_path)

    def act(self,handler):
        raise Exception("'{0}' not found".format(handler.path))


class CaseExistingFile(BaseCase):

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class CaseAlwaysFail(BaseCase):
    def test(self, handler):
        return True

    def act(self, handler):
        raise Exception("Unknown object '{0}'".format(handler.path))


class CaseDirectoryIndexFile(BaseCase):

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler,self.index_path(handler))


class CaseDirectoryNoIndexFile(BaseCase):

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))

    def act(self,handler):
        handler.list_dir(handler.full_path)


class CaseCGIFile(BaseCase):
    '''Something runnable'''
    def test(self,handler):
        return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')

    def act(self,handler):
        handler.run_cgi(handler.full_path)


class RequestHandler(BaseHTTPRequestHandler):
    '''Handle HTTP requests by returning a fixed 'page'.'''
    Cases = [CaseNoFile(), CaseCGIFile(), CaseExistingFile(), CaseDirectoryIndexFile(), CaseDirectoryNoIndexFile(),CaseAlwaysFail()]

    def do_GET(self):
        try:
            # Figure out what exactly is being requested.
            self.full_path = os.getcwd() + self.path
            # Figure out how to handle it.
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break
        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)

    Error_Page = """\
            <html>
            <body>
            <h1>Error accessing {path}</h1>
            <p>{msg}</p>
            </body>
            </html>
            """

    def handle_error(self,msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content,404)

    def send_content(self,content,status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if isinstance(content,str):
            content = str.encode(content)
        self.wfile.write(content)

    # How to display a directory listing.
    Listing_Page = '''\
           <html>
           <body>
           <ul>
           {0}
           </ul>
           </body>
           </html>
           '''

    def list_dir(self,full_path):
        try:
            entries = os.listdir(full_path)
            bullets = [
                '<li>{0}</li>'.format(e)
                for e in entries if not e.startswith('.')
            ]
            page = self.Listing_Page.format('\n'.join(bullets))
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    def run_cgi(self,full_path):
        cmd = "python " + full_path
        child_stdout = os.popen(cmd)
        data = child_stdout.read()
        child_stdout.close()
        self.send_content(data)

# -------------------------------------------------------------------------
if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
