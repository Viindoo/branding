import os
import odoo
from odoo import api, SUPERUSER_ID
from odoo.modules import module

from . import models


get_module_icon = module.get_module_icon


def get_viin_brand_module_icon(module):
    module_icon = '/viin_brand/static/img/%s.png' % module
    for adp in odoo.addons.__path__:
        if os.path.exists(adp + module_icon): 
            return module_icon
    return get_module_icon(module)


def post_load():
    module.get_module_icon = get_viin_brand_module_icon


def _update_web_icon(env):
    menus = env['ir.ui.menu'].search([('web_icon', '!=', False)])
    for m in menus:
        paths = m.web_icon and m.web_icon.split(',') or []
        if len(paths) == 2:
            web_icon = False
            module_icon = '/viin_brand/static/img/%s.png' % paths[0]
            for adp in odoo.addons.__path__:
                if os.path.exists(adp + module_icon): 
                    web_icon = 'viin_brand,static/img/%s.png' % paths[0]
                    m.write({'web_icon': 'viin_brand,static/img/%s.png' % paths[0]})
                    break

def _update_module_icon(env):
    modules = env['ir.module.module'].search([])
    for m in modules:
        icon = get_viin_brand_module_icon(m.icon.split('/')[1])
        m.write({'icon': icon})


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_module_icon(env)
    
    #for compatibility with to_backend_theme module
    _update_web_icon(env)

#TODOS: Handling when removing the module
def uninstall_hook(cr, registry):
    pass


