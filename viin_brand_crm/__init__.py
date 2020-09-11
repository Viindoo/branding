from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('crm', 'viin_brand_crm')
    env['viin.brand.base'].update_menu_icon('viin_brand_crm', 'crm.crm_menu_root')
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].restore_icon('crm', 'crm.crm_menu_root')
    