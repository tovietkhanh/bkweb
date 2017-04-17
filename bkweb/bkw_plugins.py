import logging
import pkg_resources

__author__ = 'tok'

# Define logger for this module
logger = logging.getLogger(__name__)


class PluginsMgr(object):
    def run(self, param):
        pass


class IBkwebPlugin(object):
    """
        Defines interface for all plugins
    """

    CATEGORY = "Undefined"

    def activate(self):
        logger.info("Activate plugin object [%s]",
            self.__class__.__name__)

    def deactivate(self):
        logger.info("Deactivate plugin object [%s]",
                    self.__class__.__name__)

    def get_localesdir(self):
        """
        Return the location of the locales directory. Default implementation
        return the "locales" directory if exists. Otherwise return None.
        """
        if pkg_resources.resource_isdir(self.__module__, 'locales'):
            return pkg_resources.resource_filename(self.__module__, 'locales')
        return False

    def get_templatesdir(self):
        """
        Return the location of the templates director. Default implementation
        return the "templates" director if exists. Otherwise return None.
        """
        if pkg_resources.resource_isdir(self.__module__, 'templates'):
            return pkg_resources.resource_filename(self.__module__, 'templates')
        return False

