from bkweb.base_core import Component
from bkweb.base_i18n import get_cur_lang

__author__ = 'tok'

"""
    Navigation main page
"""


class MainPage(Component):
    def _compile_template(self, template_name, **kwargs):
        """
            Generate a standard html page using a given template.
            Used by subclasses to provide default template value.
        :param template_name:
        :param kwargs:
        :return:
        """
        parms = {
            "lang": get_cur_lang(),
            "version": self.app.get_version(),
            "extra_head_templates": [],
        }

        if self.app.curuser:
            parms.update({
                "is_login": False,
                "username": self.app.curuser.username,
                "is_admin": self.app.curuser.is_admin,

            })

        # Append custom attributes
        parms["header_logo"] = hasattr(self.app.Bkwebroot.static, "header_logo")
        header_name = self.app.cfg.get_config("HeaderName")
        if header_name:
            parms["header_name"] = header_name

        # Append template params
        parms.update(kwargs)

        # Filter params using plugins
        self.app.plugins.run(

        )