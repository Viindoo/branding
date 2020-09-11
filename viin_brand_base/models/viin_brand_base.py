from odoo import models

class ViinBrandBase(models.AbstractModel):
    _name = 'viin.brand.base'
    _description = 'Viindoo Brand Base model'
    
    
    def update_icon(self, module_name, module_branding, menu_xml_id, icon_path = 'static/description/icon.png'):
        '''
        Update new icon for module
        
        @param module_name: module name want to change icon
        @param module_branding: module name contains icon file and handle
        @param menu_xml_id: xml id of menuitem, example: crm.crm_menu_root
        @param icon_path: file icon, default: static/description/icon.png
        '''
        menu = self.env['ir.ui.menu'].search([('id', '=', self.env.ref(menu_xml_id).id)], limit=1)
        menu.write({'web_icon' :  module_branding + ',' + icon_path})
        
        module = self.env['ir.module.module'].search([('name', '=', module_name)], limit=1)
        module.write({'icon' : '/' + module_branding + '/' + icon_path})
        module._get_icon_image()
    
    def restore_icon(self, module_name, menu_xml_id, icon_path = 'static/description/icon.png'):
        '''
        Restore original icon of module
        
        @param module_name: module name want to restore icon
        @param menu_xml_id: full xml id of menuitem web_icon, example: crm.crm_menu_root
        @param icon_path: file icon default, default: static/description/icon.png
        '''
        module_icon = self.env['ir.module.module'].search([('name', '=', module_name)], limit=1)
        module_icon.write({'icon' : '/' + module_name + '/' + icon_path})
        module_icon._get_icon_image()
        
        module_icon_menu = self.env['ir.ui.menu'].search([('id', '=', self.env.ref(menu_xml_id).id)], limit=1)
        module_icon_menu.write({'web_icon' : module_name + ',' + icon_path})
        

        
    