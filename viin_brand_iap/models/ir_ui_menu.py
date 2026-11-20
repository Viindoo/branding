from odoo import api, models

HIDDEN_MENU_XMLIDS = ['iap.iap_root_menu']


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _get_hidden_menu_xmlids(self):
        return super()._get_hidden_menu_xmlids() + HIDDEN_MENU_XMLIDS
