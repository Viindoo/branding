from odoo import http

from odoo.addons.web.controllers.home import Home

from ..tools import VIINDOO_TWITTER_HANDLE


class ViindooHome(Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        response = super().web_login(redirect=redirect, **kw)
        # A redirect carries no template context: only the rendered login page names the handle.
        qcontext = getattr(response, 'qcontext', None)
        if qcontext is not None:
            qcontext['twitter_handle'] = VIINDOO_TWITTER_HANDLE
        return response
