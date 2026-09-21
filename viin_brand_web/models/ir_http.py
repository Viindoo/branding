# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def webclient_rendering_context(self):
        # A session that never received this cookie would otherwise pick the light lazy
        # bundle on its first pivot/graph view even when the resolved scheme is dark - so
        # the very first webclient response must carry the resolution, not just the render.
        context = super().webclient_rendering_context()
        scheme = context['color_scheme']
        if request and request.httprequest.cookies.get('color_scheme') != scheme:
            request.future_response.set_cookie('color_scheme', scheme)
        return context

    def color_scheme(self):
        # Resolution order (dark mode): the user's own explicit light/dark preference, then the
        # `color_scheme` cookie, then super() as the final fallback. The cookie ranks BELOW an
        # explicit preference because it is per-BROWSER while the preference is per-USER - ranked
        # above it, a cookie left behind by one user decides another user's render. It ranks ABOVE
        # super() because 'auto' is the one case the server cannot resolve on its own: only the
        # client knows the OS preference, and it caches that resolution in this same cookie.
        # Always returns a value (never a missing return - find_override_point anti-pattern).
        user_scheme = self.env.user.viin_color_scheme
        if user_scheme in ('light', 'dark'):
            return user_scheme
        scheme = request.httprequest.cookies.get('color_scheme') if request else None
        if scheme in ('light', 'dark'):
            return scheme
        return super().color_scheme()
