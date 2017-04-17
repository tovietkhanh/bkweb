from bkweb.base_core import Component

__author__ = 'tok'


class UserManager(Component):
    """
    This class handle all user operation. This class is greatly inspired from
    TRAC account manager class.
    """

    def __init__(self, app):
        Component.__init__(self, app)