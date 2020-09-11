from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('crm', 'viin_brand_crm')
    env['viin.brand.base'].update_menu_icon('crm', 'viin_brand_crm', 'crm_menu_root')
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].restore_module_icon('crm')
    env['viin.brand.base'].restore_menu_icon('crm', 'crm_menu_root')
    