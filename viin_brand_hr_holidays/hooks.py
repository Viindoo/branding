from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('hr_holidays')
    env['viin.brand.base'].update_menu_icon('hr_holidays', 'hr_holidays.menu_hr_holidays_root')
    