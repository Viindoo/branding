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
    return '/viin_brand/static/img/%s.png' % 'base'


def post_load():
    module.get_module_icon = get_viin_brand_module_icon


def _update_viin_brand_web_icon(env):
    menus = env['ir.ui.menu'].search([('web_icon', '!=', False)])
    for m in menus:
        paths = m.web_icon and m.web_icon.split(',') or []
        if len(paths) == 2:
            web_icon = False
            
            module = paths[1].split('/')[-1][:-4]
            if module == 'settings' or module == 'modules':
                paths[0] = module
            
            module_icon = '/viin_brand/static/img/%s.png' % paths[0]
            for adp in odoo.addons.__path__:
                if os.path.exists(adp + module_icon): 
                    m.write({
                        'web_icon': 'viin_brand,static/img/%s.png' % paths[0],
                        })
                    break

def _update_viin_brand_module_icon(env):
    modules = env['ir.module.module'].search([])
    for m in modules:
        icon = get_viin_brand_module_icon(m.icon.split('/')[1])
        m.write({'icon': icon})


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_viin_brand_module_icon(env)
    _update_viin_brand_web_icon(env)


def _remove_viin_brand_web_icon(env):
    menus = env['ir.ui.menu'].search([('web_icon', 'like', 'viin_brand')])
    for m in menus:
        module = m.web_icon.split('/')[-1][:-4]
        web_icon = False
        if module == 'icon':
            continue
        elif module == 'settings' or module == 'modules':
            web_icon = 'base,static/description/%s.png' % module
        else:
            web_icon = '%s,static/description/icon.png' % module
        
        if web_icon:
            m.write({
                'web_icon': web_icon,
                })


def _remove_viin_brand_module_icon(env):
    modules = env['ir.module.module'].search([('icon', 'like', 'viin_brand')])
    for m in modules:
        module = m.icon.split('/')[-1][:-4]
        icon = False
        if module == 'icon':
            continue
        elif module == 'settings' or module == 'modules':
            icon = '/base/static/description/%s.png' % module
        else:
            icon = '/%s/static/description/icon.png' % module
        
        if icon:
            m.write({
                'icon': icon,
                })


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module.get_module_icon = get_module_icon
    _remove_viin_brand_web_icon(env)
    _remove_viin_brand_module_icon(env)


