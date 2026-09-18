# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.http import request


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Per-user backend color scheme (dark mode). The 'viin_' prefix avoids collision with
    # core's own unprefixed `color_scheme` concept (cookie / ir.http). 'auto' defers to the
    # client / OS, so the server keeps rendering the super() fallback for it (see ir.http).
    viin_color_scheme = fields.Selection(
        selection=[('light', "Light"), ('dark', "Dark"), ('auto', "System")],
        string="Color Scheme",
        default='light',
        help="Backend appearance: Light, Dark, or System (follow the device preference).",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        # A user may read their own color-scheme preference (no admin rights needed).
        return super().SELF_READABLE_FIELDS + ['viin_color_scheme']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        # A user may set their OWN color-scheme preference; the SELF scope pins the write to
        # the current user, so writing another user's field still raises AccessError.
        return super().SELF_WRITEABLE_FIELDS + ['viin_color_scheme']

    def write(self, vals):
        # Keeps the color_scheme cookie converging on the CURRENT user's own preference change
        # (see ir.http.color_scheme()'s cookie > preference precedence) instead of leaving it
        # stuck on whatever an earlier session already wrote, for up to that cookie's own
        # year-long expiry. Scoped to self.env.user's own record so writing someone else's
        # preference never bleeds into the acting user's response. Switching to 'auto' expires
        # the cookie outright instead of writing a value, since the client/OS decides from there.
        res = super().write(vals)
        scheme = vals.get('viin_color_scheme')
        if request and self.env.user in self:
            if scheme in ('light', 'dark'):
                request.future_response.set_cookie('color_scheme', scheme)
            elif scheme == 'auto':
                request.future_response.set_cookie('color_scheme', '', max_age=0)
        return res
