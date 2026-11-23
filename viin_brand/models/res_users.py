from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.http import request

from ..tools import debrand_exception


class ResUsers(models.Model):
    _inherit = 'res.users'

    # The 'viin_' prefix keeps the field apart from core's `color_scheme` cookie and ir.http concept.
    # 'auto' defers to the device preference, so the server keeps the core resolution for it.
    viin_color_scheme = fields.Selection(
        selection=[('light', "Light"), ('dark', "Dark"), ('auto', "System")],
        string="Color Scheme",
        default='light',
        help="Backend appearance: Light, Dark, or System (follow the device preference).",
        user_writeable=True,
    )

    def write(self, vals):
        # Keeps the color_scheme cookie following the current user's own preference. 'auto' leaves
        # the cookie alone: the client resolves the device preference and stores the effective
        # light or dark value there, and core reads it for graph colours, the colour picker, the
        # ace editor and the pdf.js viewer.
        res = super().write(vals)
        scheme = vals.get('viin_color_scheme')
        if request and self.env.user in self and scheme in ('light', 'dark'):
            request.future_response.set_cookie('color_scheme', scheme)
        return res

    @api.ondelete(at_uninstall=True)
    def _unlink_except_master_data(self):
        try:
            super()._unlink_except_master_data()
        except UserError as error:
            raise debrand_exception(error)
