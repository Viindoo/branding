from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icon = env['ir.module.module'].search([('name', '=', 'survey')], limit=1)
    module_icon.write({'icon' : '/viin_brand_survey/static/description/icon.png'})
    module_icon._get_icon_image()
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icon = env['ir.module.module'].search([('name', '=', 'survey')], limit=1)
    module_icon.write({'icon' : '/survey/static/description/icon.png'})
    module_icon._get_icon_image()
    
    menu_id = env.ref('survey.menu_surveys').id
    module_icon_menu = env['ir.ui.menu'].search([('id', '=', menu_id)], limit=1)
    module_icon_menu.write({'web_icon' : 'survey,static/description/icon.png'})