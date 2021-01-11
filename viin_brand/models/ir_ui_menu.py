import os
import odoo


class IrUiMenu(odoo.models.Model):
    _inherit = 'ir.ui.menu'
    
    
    def _compute_web_icon_data(self, web_icon):
        paths = web_icon.split(',')
        if web_icon and len(paths) == 2:
            module_icon = '/viin_brand/static/img/%s.png' % paths[0]
            for adp in odoo.addons.__path__:
                if os.path.exists(adp + module_icon): 
                    web_icon = 'viin_brand,static/img/%s.png' % paths[0]
                    break
        return super(IrUiMenu, self)._compute_web_icon_data(web_icon)