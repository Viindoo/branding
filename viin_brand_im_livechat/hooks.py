from odoo import api, SUPERUSER_ID

def _uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].update_module_icon('im_livechat')
    env['viin.brand.base'].update_menu_icon('im_livechat', 'im_livechat.menu_livechat_root')
    