from odoo import api, SUPERUSER_ID


def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icon = env['ir.module.module'].search([('name', '=', 'hr_holidays')], limit=1)
    module_icon.write({'icon' : '/viin_brand_hr_holidays/static/description/icon.png'})
    module_icon._get_icon_image()
    
def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_icon = env['ir.module.module'].search([('name', '=', 'hr_holidays')], limit=1)
    module_icon.write({'icon' : '/hr_holidays/static/description/icon.png'})
    module_icon._get_icon_image()
    
    rule_id = env.ref('hr_holidays.menu_hr_holidays_root').id
    module_icon_menu = env['ir.ui.menu'].search([('id', '=', rule_id)], limit=1)
    module_icon_menu.write({'web_icon' : 'hr_holidays,static/description/icon.png'})