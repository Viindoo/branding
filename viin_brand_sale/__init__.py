from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icons = {'sale_management': '/viin_brand_sale/static/description/icon.png'}
    menu_icons = {'sale.sale_menu_root': 'viin_brand_sale,static/description/icon.png'}
    env['viin.brand.to.base'].set_icon(menu_icons, module_icons)
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icons = {'sale_management': '/sale_management/static/description/icon.png'}
    menu_icons = {'sale.sale_menu_root': 'sale_management,static/description/icon.png'}
    env['viin.brand.to.base'].set_icon(menu_icons, module_icons)
    