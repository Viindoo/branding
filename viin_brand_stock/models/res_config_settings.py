from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _get_hidden_setting_xpaths(self):
        """Hide the "Find a Delivery Provider" button, which lists the shipping connectors of Enterprise."""
        return super()._get_hidden_setting_xpaths() + ['//setting[@id="delivery"]/button[@type="action"]']
