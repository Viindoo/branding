from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icons = {'point_of_sale': '/viin_brand_point_of_sale/static/description/icon.png'}
    menu_icons = {'point_of_sale.menu_point_root': 'viin_brand_point_of_sale,static/description/icon.png'}
    env['viin.brand.to.base'].set_icon(menu_icons, module_icons)
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icons = {'point_of_sale': '/point_of_sale/static/description/icon.png'}
    menu_icons = {'point_of_sale.menu_point_root': 'point_of_sale,static/description/icon.png'}
    env['viin.brand.to.base'].set_icon(menu_icons, module_icons)
    