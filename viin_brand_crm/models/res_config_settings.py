from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _get_hidden_setting_xpaths(self):
        """Hide the Odoo IAP settings of CRM (lead enrichment, mining, visitor reveal)."""
        return super()._get_hidden_setting_xpaths() + [
            '//field[@name="%s"]/ancestor::setting[1]' % field_name
            for field_name in ('module_crm_iap_enrich', 'module_crm_iap_mine', 'module_website_crm_iap_reveal')
        ]
