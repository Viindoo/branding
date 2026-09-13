from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        # Real-session marker for the SettingsPage brand-icon lookup (see
        # static/src/js/settings_page.js): the get_viin_brand_modules_icon RPC
        # must only fire in genuine webclient sessions. Core SettingsFormView
        # QUnit suites assert exact RPC sequences and the key is absent from
        # their mock sessions (runbot 223235/396399, 6 SettingsFormView tests).
        result['viin_brand_settings_icons'] = self.env.user._is_internal()
        return result
