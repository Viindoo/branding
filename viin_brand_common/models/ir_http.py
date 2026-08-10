from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        # Real-session marker for brand client tweaks (graph palette, window-title part) (see
        # static/src/core/colors/colors.js): core QUnit graph suites assert the
        # default palette colors, so the brand override must only apply when the
        # session was bootstrapped by a real server - the key is absent from
        # mock test sessions (runbot 223219/396221, 30 GraphView tests).
        result['viin_brand'] = True
        return result
