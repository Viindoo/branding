from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('hr_recruitment')
    env['viin.brand.base'].update_menu_icon('hr_recruitment', 'hr_recruitment.menu_hr_recruitment_root')
    