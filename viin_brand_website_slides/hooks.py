from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('website_slides')
    env['viin.brand.base'].update_menu_icon('website_slides', 'website_slides.website_slides_menu_root')
    