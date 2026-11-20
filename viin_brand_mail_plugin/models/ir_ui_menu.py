from odoo import api, models

# The partner enrichment menu, which is served by a paid service of Odoo.
HIDDEN_MENU_XMLIDS = ['mail_plugin.res_partner_iap_menu']


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _get_hidden_menu_xmlids(self):
        return super()._get_hidden_menu_xmlids() + HIDDEN_MENU_XMLIDS
