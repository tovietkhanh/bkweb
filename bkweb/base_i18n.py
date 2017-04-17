import cherrypy

__author__ = 'tok'


def get_cur_lang():
    """
    Return the lang being currently served to the user.
    """
    if not hasattr(cherrypy.response, "i18n"):
        return "en"
    return cherrypy.response.i18n._lang