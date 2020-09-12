from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('crm')
    env['viin.brand.base'].update_menu_icon('crm', 'crm.crm_menu_root')
    