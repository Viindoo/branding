from odoo import api, SUPERUSER_ID
from . import models


def uninstall_brand_icon(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['viin.brand.base'].restore_icon('base.menu_administration', icon='settings.png')
    env['viin.brand.base'].restore_icon('base.menu_management', icon='modules.png')
    