from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icons = {'utm': '/viin_brand_utm/static/description/icon.png'}
    menu_icons = {'utm.menu_link_tracker_root': 'viin_brand_utm,static/description/icon.png'}
    env['viin.brand.to.base'].set_icon(menu_icons, module_icons)
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icons = {'utm': '/utm/static/description/icon.png'}
    menu_icons = {'utm.menu_link_tracker_root': 'utm,static/description/icon.png'}
    env['viin.brand.to.base'].set_icon(menu_icons, module_icons)
    