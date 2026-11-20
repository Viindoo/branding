from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _get_hidden_setting_xpaths(self):
        """Hide the row that sells sending invoices and payment follow-ups by post."""
        return super()._get_hidden_setting_xpaths() + ['//setting[@id="send_invoices_followups"]']
