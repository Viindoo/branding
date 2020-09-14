from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('point_of_sale')
    env['viin.brand.base'].update_menu_icon('point_of_sale', 'point_of_sale.menu_point_root')
