from odoo import models

class ViinBrandBase(models.AbstractModel):
    _name = 'viin.brand.base'
    _description = 'Viindoo Brand Base model'
    
        
    def update_module_icon(self, origin_module_name, brand_module_name = '', icon_path = 'static/description/icon.png'):
        '''
        This method used to set origin module's icon by brand module's icon and restore after brand module uninstalled
        
        @param origin_module_name: module name needed to replace icon
        @param brand_module_name: module name contains icon file and handle,
        @param icon_path: default: static/description/icon.png
        
        If it is not passed then it means the method is used to restore module icon to origin
        '''
        
        module = self.env['ir.module.module'].search([('name', '=', origin_module_name)], limit=1)
        module.write({'icon' : '/' + (brand_module_name or origin_module_name) + '/' + icon_path})
        module._get_icon_image()
        
    def update_menu_icon(self, origin_module_name, menu_xml_id, icon_path = 'static/description/icon.png'):
        '''
        This method used to set origin menu module's icon by brand menu module's icon and restore after brand module uninstalled
        
        @param origin_module_name: module name needed to replace icon
        @param menu_xml_id: full xml id of menuitem web_icon, example: crm.crm_menu_root
        @param icon_path: default: static/description/icon.png
        
        If it is not passed then it means the method is used to restore module icon to origin
        '''

        module_icon_menu = self.env['ir.ui.menu'].search([('id', '=', self.env.ref(menu_xml_id).id)], limit=1)
        module_icon_menu.write({'web_icon' : origin_module_name + ',' + icon_path})
    