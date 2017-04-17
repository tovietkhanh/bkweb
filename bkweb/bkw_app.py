import cherrypy
from cherrypy.process.plugins import Monitor
import logging
from cherrypy import Application
import os
import pkg_resources
from future.utils import native_str
import sys
from bkweb import bkw_templating
from bkweb import bkw_plugins
from bkweb import bkw_config
from bkweb.base_dispatch import static
from bkweb.base_users import UserManager
from bkweb.nav_dashboard import DashboardPage
from bkweb import nav_main

__author__ = 'tok'


# Logger definition
logger = logging.getLogger(__name__)

PY3 = sys.version_info[0] == 3

class BkwebApp(Application):
    """
        Application context class
    """

    def __init__(self, configFile=None):

        # Initialise config
        self.load_config(configFile)

        # Initialise template engine
        self.templates = bkw_templating.TemplateMgr()

        # Initialise plugins
        self.plugins = bkw_plugins.PluginsMgr(self.cfg)

        # Initialise application
        config = {
            native_str('/'): {
                'tools.authform.on': True,
                'tools.i18n.on': True,
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.gzip.on': True,
                'tools.sessions.on': True,
                'error_page.default': self.error_page,
            }
        }

        # To work around the new behaviour in CherryPy >= 5.5.0, force usage of
        # ISO-8859-1 encoding for URL. This avoid any conversion of the
        # URL into UTF-8.
        if PY3 and cherrypy.__version__ >= "5.5.0":
            config[native_str('/')]["request.uri_encoding"] = "ISO-8859-1"

        self._setup_session_storage(config)
        Application.__init__(self, root=BkwebRoot(self), config=config)

        # Activate loaded plugins
        self.plugins.run(lambda x: self.activate_plugin(x))

        # create user manager
        self.userdb = UserManager(self)

        # Start deamon plugin
        self._start_deamons()

    def load_config(self, configFile=None):
        self.cfg = bkw_config.Configuration(configFile)

        tempdir = self.cfg.get_config("TempDir", default="")
        if tempdir:
            os.environ["TMPDIR"] = tempdir

    def error_page(self, **kwargs):
        """
            Default error page shown when an unexpected error occur
        :param kwargs:
        :return:
        """
        # Log exception
        logger.exception(kwargs.get('message', ''))

        # Validate response
        res_type = cherrypy.tools.accept.callable(['text/html', 'text/plain'])
        if res_type == 'text/plain':
            return kwargs.get('message')

        # Brush up an error page
        try:
            page = nav_main.MainPage(cherrypy.request.app)
            return page._compile_template('error_page_default.html', **kwargs)
        except:
            pass

        # Send the raw if failing
        return kwargs.get('message')

    @property
    def curuser(self):
        """
            Get current user
        :return:
        """
        return cherrypy.serving.request.login

    def _setup_session_storage(self, config):
        # Configure session storage.
        session_storage = self.cfg.get_config("SessionStorage")
        session_dir = self.cfg.get_config("SessionDir")
        if session_storage.lower() != "disk":
            return

        if (not os.path.exists(session_dir) or
                not os.path.isdir(session_dir) or
                not os.access(session_dir, os.W_OK)):
            return

        logger.info("Setting session mode to disk in directory %s", session_dir)
        config.update({
            'tools.sessions.on': True,
            'tools.sessions.storage_type': True,
            'tools.sessions.storage_path': session_dir,
        })

    def activate_plugin(self, plugin_obj):
        """Activate the given plugin object."""
        plugin_obj.app = self
        # Add templates location to the templating engine.
        if plugin_obj.get_templatesdir():
            self.templates.add_templatesdir(plugin_obj.get_templatesdir())
        plugin_obj.activate()

    def _start_deamons(self):
        """
        Start deamon plugins
        """
        logger.debug("starting daemon plugins")

        def start_deamon(p):
            Monitor(cherrypy.engine,
                    p.deamon_run,
                    frequency=p.deamon_frequency,
                    name=p.__class__.__name__).subscribe()

        self.plugins.run(start_deamon, category='Daemon')


class BkwebRoot(DashboardPage):
    def __init__(self, app):
        DashboardPage.__init__(self, app)

        # Register static dir
        static_dir = pkg_resources.resource_filename('bkweb', 'static')
        self.static = static(static_dir)

        # Register favicon.ico
        default_favicon = pkg_resources.resource_filename('bkweb', 'static/favicon.ico')
        favicon = app.cfg.get_config("Favicon", default_favicon)
        self.favicon_ico = static(favicon)

        # Register logo
        header_logo = app.cfg.get_config("HeaderLogo")
        if header_logo:
            self.static.header_logo = static(header_logo)