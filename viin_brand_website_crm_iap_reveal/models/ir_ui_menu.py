from odoo import api, models

# The menus of visits to leads, a paid service of Odoo S.A.
HIDDEN_MENU_XMLIDS = [
    'website_crm_iap_reveal.crm_reveal_rule_menu_action',
    'website_crm_iap_reveal.crm_reveal_view_menu_action',
]


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _get_hidden_menu_xmlids(self):
        return super()._get_hidden_menu_xmlids() + HIDDEN_MENU_XMLIDS
