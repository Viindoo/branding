from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('contacts')
    env['viin.brand.base'].update_menu_icon('contacts', 'contacts.menu_contacts')
    