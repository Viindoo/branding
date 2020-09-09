from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icon = env['ir.module.module'].search([('name', '=', 'website')], limit=1)
    module_icon.write({'icon' : '/viin_brand_website/static/description/icon.png'})
    module_icon._get_icon_image()
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icon = env['ir.module.module'].search([('name', '=', 'website')], limit=1)
    module_icon.write({'icon' : '/website/static/description/icon.png'})
    module_icon._get_icon_image()
    
    module_icon_menu = env['ir.ui.menu'].search([('name', '=', 'Websites')], limit=1)
    module_icon_menu.write({'web_icon' : 'website,static/description/icon.png'})