from odoo import api, SUPERUSER_ID
from . import models

def update_module_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].modify_menu_icon('viin_brand_base', 'base.menu_administration', icon_path='static/description/settings.png')
    env['viin.brand.base'].modify_menu_icon('viin_brand_base', 'base.menu_management', icon_path='static/description/modules.png')
    

def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].modify_menu_icon('base', 'base.menu_administration', icon_path='static/description/settings.png')
    env['viin.brand.base'].modify_menu_icon('base', 'base.menu_management', icon_path='static/description/modules.png')
    