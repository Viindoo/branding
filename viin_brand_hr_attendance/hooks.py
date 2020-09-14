from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('hr_attendance')
    env['viin.brand.base'].update_menu_icon('hr_attendance', 'hr_attendance.menu_hr_attendance_root')
    