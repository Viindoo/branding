from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _get_hidden_setting_xpaths(self):
        return super()._get_hidden_setting_xpaths() + ['//setting[@id="iap_credits_setting"]']
