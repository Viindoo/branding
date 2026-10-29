from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _get_hidden_setting_xpaths(self):
        """Hide the "Pay after" row: its selector only opens the Enterprise upsell."""
        return super()._get_hidden_setting_xpaths() + ['//div[@id="self-payment-after"]']
