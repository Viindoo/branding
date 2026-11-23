from odoo import api, models

# The menus of lead mining, a paid service of Odoo S.A.
HIDDEN_MENU_XMLIDS = [
    'crm_iap_mine.crm_menu_lead_generation',
    'crm_iap_mine.crm_iap_lead_mining_request_menu_action',
]


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _get_hidden_menu_xmlids(self):
        return super()._get_hidden_menu_xmlids() + HIDDEN_MENU_XMLIDS
