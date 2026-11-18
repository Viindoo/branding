from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        # The settings page asks for the brand module icons only in a real webclient session;
        # core settings view tests assert exact RPC sequences and carry no such key.
        result['viin_brand_settings_icons'] = self.env.user._is_internal()
        result['support_url'] = 'https://viindoo.com/pricing'
        return result

    def webclient_rendering_context(self):
        # The first webclient response must already carry the resolved scheme: a session without
        # the cookie would otherwise load the light lazy bundle for its first pivot or graph view
        # even when the resolved scheme is dark.
        context = super().webclient_rendering_context()
        scheme = context['color_scheme']
        if request and request.httprequest.cookies.get('color_scheme') != scheme:
            request.future_response.set_cookie('color_scheme', scheme)
        return context

    def color_scheme(self):
        # Resolution order: the user's own light or dark preference, then the `color_scheme`
        # cookie, then core. The cookie ranks below the preference because it belongs to the
        # browser while the preference belongs to the user. It ranks above core because 'auto' is
        # resolved by the client from the device preference and cached in that cookie.
        user_scheme = self.env.user.viin_color_scheme
        if user_scheme in ('light', 'dark'):
            return user_scheme
        scheme = request.httprequest.cookies.get('color_scheme') if request else None
        if scheme in ('light', 'dark'):
            return scheme
        return super().color_scheme()
