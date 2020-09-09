from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icon = env['ir.module.module'].search([('name', '=', 'fleet')], limit=1)
    module_icon.write({'icon' : '/viin_brand_fleet/static/description/icon.png'})
    module_icon._get_icon_image()
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icon = env['ir.module.module'].search([('name', '=', 'fleet')], limit=1)
    module_icon.write({'icon' : '/fleet/static/description/icon.png'})
    module_icon._get_icon_image()
    
    menu_id = env.ref('fleet.menu_root').id
    module_icon_menu = env['ir.ui.menu'].search([('id', '=', menu_id)], limit=1)
    module_icon_menu.write({'web_icon' : 'fleet,static/description/icon.png'})