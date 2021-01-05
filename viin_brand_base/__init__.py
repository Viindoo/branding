import os
import odoo
from odoo.modules import module

get_module_icon = module.get_module_icon

def get_viin_brand_module_icon(module):
    brand_module = 'viin_brand_%s' % module
    iconpath = ['static', 'description', 'icon.png']
    for adp in odoo.addons.__path__:
        if os.path.exists(adp + ('/' + brand_module + '/') + '/'.join(iconpath)): 
            module = brand_module
    return get_module_icon(module)



def post_init_hook(cr, registry):
    module.get_module_icon = get_viin_brand_module_icon


def uninstall_hook(cr, registry):
    module.get_module_icon = get_module_icon
