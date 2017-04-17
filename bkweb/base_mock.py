import cherrypy
from cherrypy.test import helper
import os
import pkg_resources
import shutil
import tarfile
import tempfile
import unittest
from urllib import urlencode
from future.utils import native_str
from bkweb.bkw_app import BkwebApp

__author__ = 'tok'

"""
    Mock class for testing purposes
"""


class BkwebAppTestCase(unittest.Testcase):

    enabled_plugins = ['SQLite']
    default_config = {}
    reset_app = True
    reset_testcases = False
    REPO = 'testcases/'
    USERNAME = None
    PASSWORD = None

    def setUp(self):
        self.app = FakeBkwebApp(self.enabled_plugins, self.default_config)
        if self.reset_app:
            self.app.reset(self.USERNAME, self.PASSWORD)
        if self.reset_testcases:
            self.app.reset_testcases()
        unittest.TestCase.setUp()


    def tearDown(self):
        self.app.clear_db()
        if self.reset_testcases:
            self.app.clear_testcases()
        unittest.TestCase.tearDown(self)


class FakeBkwebApp(BkwebApp):
    def __init__(self, enabled_plugins=['SQLite'], default_config={}):
        assert enabled_plugins is None or isinstance(enabled_plugins, list)
        self.enabled_plugins = enabled_plugins
        assert default_config is None or isinstance(default_config, dict)
        self.default_config = default_config

        # Call parent constructor
        BkwebApp.__init__(self)

    def delete_db(self):
        if hasattr(self, 'database_dir'):
            shutil.rmtree(self.database_dir)
            delattr(self, 'database_dir')

    def delete_testcases(self):
        if hasattr(self, 'testcases'):
            shutil.rmtree(native_str(self.testcases))

    def load_config(self, configFile=None):
        BkwebApp.load_config(self, None)

        #Enable given plugins
        for plugin_name in self.enabled_plugins:
            self.cfg.set_config('%sEnabled' % plugin_name, 'True')

        #Create temp db
        if 'SQLite' in self.enabled_plugins:
            self.database_dir = tempfile.mkdtemp(prefix='bkweb_mock_db_')
            self.cfg.set_config('SQLiteDBFile', os.path.join(self.database_dir, 'bkweb.tmp.db'))

        #Create a mock LDAP
        if 'Ldap' in self.enabled_plugins:
            self.cfg.set_config('LdapUri', '__default__')
            self.cfg.set_config('LdapBaseDn', 'dc=nodomain')

        # Set config
        for key, val in list(self.default_config.items()):
            self.cfg.set_config(key, val)

    def reset(self, username=None, password=None):
        """
        Reset the application. Delete all data from database.
        """
        # Delete all user from database
        for user in self.userdb.list():
            self.userdb.delete_user(user)

        # Create new user admin
        if self.userdb.supports('add_user') and username and password:
            user = self.userdb.add_user(username, password)
            user.is_admin = True

    def reset_testcases(self):
        """Extract testcases."""
        # Extract 'testcases.tar.gz'
        testcases = pkg_resources.resource_filename('bkweb.tests', 'testcases.tar.gz')
        new = str(tempfile.mkdtemp(prefix='bkweb_tests_'))
        tarfile.open(testcases).extractall(native_str(new))

        # Register repository
        for user in self.userdb.list():
            user.user_root = new
            user.repos = ['testcases/']

        self.testcases = new


class BkwebNavTestCase(helper.CPWebcase):
    """
    Helper class for the bkweb test suite.
    """

    REPO = 'testcases'
    USERNAME = 'admin'
    PASSWORD = 'admin123'
    interactive = False
    login = False
    reset_app = False
    reset_testcases = False

    @classmethod
    def setUpClass(cls):
        super(helper.CPWebCase, cls).setUpClass()
        cls.setup_class()

    @classmethod
    def tearDownClass(cls):
        cls.teardown_class()
        app = cherrypy.tree.apps['']
        app.delete_db()

    @classmethod
    def setup_server(cls, enabled_plugins=['SQLite'], default_config={}):
        app = FakeBkwebApp(enabled_plugins, default_config)
        cherrypy.tree.mount(app)

    def setUp(self):
        helper.CPWebCase.setUp(self)
        if self.reset_app:
            self.app.reset(self.USERNAME, self.PASSWORD)
        if self.reset_testcases:
            self.app.reset_testcases()
        if self.login:
            self._login()

    def _login(self, username=USERNAME, password=PASSWORD):
        self.getPage("/login/", method='POST', body={'login': username, 'password': password})
        self.assertStatus('303 See Other')

    def getPage(self, url, headers=None, method="GET", body=None,
                protocol=None):
        if headers is None:
            headers = []
        # When body is a dict, send the data as form data.
        if isinstance(body, dict) and method in ['POST', 'PUT']:
            data = [(k.encode(encoding='latin1'), v.encode(encoding='utf-8'))
                    for k, v in body.items()]
            body = urlencode(data)
        # Send back cookies if any
        if hasattr(self, 'cookies') and self.cookies:
            headers.extend(self.cookies)
        helper.CPWebCase.getPage(self, url, headers, method, body, protocol)

    @property
    def app(self):
        """
        Return reference to Bkweb application.
        """
        return cherrypy.tree.apps['']

    @property
    def baseurl(self):
        return 'http://%s:%s' % (self.HOST, self.PORT)