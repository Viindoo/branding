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
        # Resolution order (dark mode): request `color_scheme` cookie > stored user
        # preference (explicit light/dark) > super() as the final fallback. 'auto' is NOT
        # forced here; it falls through to super() so the client / OS decides. Always
        # returns a value (never a missing return - find_override_point anti-pattern).
        scheme = request.httprequest.cookies.get('color_scheme') if request else None
        if scheme in ('light', 'dark'):
            return scheme
        user_scheme = self.env.user.viin_color_scheme
        if user_scheme in ('light', 'dark'):
            return user_scheme
        return super().color_scheme()
