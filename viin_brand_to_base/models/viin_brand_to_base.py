from odoo import models

class ViinBrandToBase(models.AbstractModel):
    _name = 'viin.brand.to.base'
    _description = 'Viindoo Brand Base model'
    
    def set_icon(self, menu_icons={}, module_icons={}):
        '''
        Method to set icon menu and module
        
        @param menu_icons: Dict has format {xml_id: value_icon}
        @param module_icons: Dict has format {module_name: value_icon}
        '''
        
        # Set icon module
        for module_name, icon in module_icons.items():
            module = self.sudo().env['ir.module.module'].search([('name', '=', module_name)], limit=1)
            module.write({'icon' : icon})
            module._get_icon_image()
        
        #set icon menu
        for xml_id, icon in menu_icons.items():
            menu = self.sudo().env['ir.ui.menu'].search([('id', '=', self.sudo().env.ref(xml_id).id)], limit=1)
            menu.write({'web_icon' : icon})