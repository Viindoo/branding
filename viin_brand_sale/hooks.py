from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('sale_management')
    env['viin.brand.base'].update_menu_icon('sale_management', 'sale.sale_menu_root')
