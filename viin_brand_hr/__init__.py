from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icons = {'hr': '/viin_brand_hr/static/description/icon.png'}
    menu_icons = {'hr.menu_hr_root': 'viin_brand_hr,static/description/icon.png'}
    env['viin.brand.to.base'].set_icon(menu_icons, module_icons)
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icons = {'hr': '/hr/static/description/icon.png'}
    menu_icons = {'hr.menu_hr_root': 'hr,static/description/icon.png'}
    env['viin.brand.to.base'].set_icon(menu_icons, module_icons)
    