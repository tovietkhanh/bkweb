import cherrypy
from cherrypy.lib.static import serve_file, mimetypes
import os

__author__ = 'tok'


def static(path):
    """
    Create a page handler to serve static files. Disable authentication.
    """
    assert isinstance(path, str)
    assert os.path.exists(path), "%r doesn't exists" % path
    content_type = None
    if os.path.isfile(path):
        # Set content-type based on filename extension
        ext = ""
        i = path.rfind('.')
        if i != -1:
            ext = path[i:].lower()
        content_type = mimetypes.types_map.get(ext, None)

    @cherrypy.expose
    @cherrypy.config(**{'tools.authform.on': False})
    def handler(*args, **kwargs):
        if cherrypy.request.method not in ('GET', 'HEAD'):
            return None
        filename = os.path.join(path, *args)
        assert filename.startswith(path)
        return serve_file(filename, content_type)

    return handler