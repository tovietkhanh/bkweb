import cherrypy
import logging

__author__ = 'tok'

# Define logger for this module
logger = logging.getLogger(__name__)

def setup_logging(log_file, log_access_file, level):
    """
    Called by `start()` to configure the logging system
    """

    assert isinstance(logging.getLevelName(level), int)

    class NotFilter(logging.Filter):

        """
        Negate logging filter
        """

        def __init__(self, name=''):
            self.name = name
            self.nlen = len(name)

        def filter(self, record):
            if self.nlen == 0:
                return 0
            elif self.name == record.name:
                return 0
            elif record.name.find(self.name, 0, self.nlen) != 0:
                return 1
            return not (record.name[self.nlen] == ".")

    class ContextFilter(logging.Filter):
        """
        This is a filter which injects contextual information into the log.
        """

        def filter(self, record):
            try:
                if hasattr(cherrypy, 'serving'):
                    request = cherrypy.serving.request
                    remote = request.remote
                    record.ip = remote.name or remote.ip
                    # If the request was forware by a reverse proxy
                    if 'X-Forwarded-For' in request.headers:
                        record.ip = request.headers['X-Forwarded-For']
            except:
                record.ip = "none"
            try:
                record.user = cherrypy.session['user'].username  # @UndefinedVariable
            except:
                record.user = "none"
            return True

    logformat = '[%(asctime)s][%(levelname)-7s][%(ip)s][%(user)s][%(threadName)s][%(name)s] %(message)s'
    level = logging.getLevelName(level)
    # Configure default log file.
    if log_file:
        assert isinstance(log_file, str)
        logging.basicConfig(filename=log_file, level=level, format=logformat)
    else:
        logging.basicConfig(level=level, format=logformat)

    # Configure access log file.
    if log_access_file:
        assert isinstance(log_access_file, str)
        logging.root.handlers[0].addFilter(NotFilter("cherrypy.access"))
    logging.root.handlers[0].addFilter(ContextFilter())


def start():
    pass


if __name__ == "__main__":
    start()