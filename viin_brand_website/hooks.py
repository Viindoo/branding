from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('website')
    env['viin.brand.base'].update_menu_icon('website', 'website.menu_website_configuration')
    