from odoo import models

class ViinBrandBase(models.AbstractModel):
    _name = 'viin.brand.base'
    _description = 'Viindoo Brand Base model'
    
        
    def modify_module_icon(self, module_name, module_brand = '', icon_path = 'static/description/icon.png'):
        '''
        Change module icon
        
        @param module_name: module name want to restore icon
        @param module_brand: module name contains icon file and handle,
        @param icon_path: file icon default, default: static/description/icon.png
        '''
        
        module = self.env['ir.module.module'].search([('name', '=', module_name)], limit=1)
        module.write({'icon' : '/' + (module_brand or module_name) + '/' + icon_path})
        module._get_icon_image()
        
    def modify_menu_icon(self, module_name, menu_xml_id, icon_path = 'static/description/icon.png'):
        '''
        Change menu icon
        
        @param module_name: module name want to restore icon
        @param menu_xml_id: full xml id of menuitem web_icon, example: crm.crm_menu_root
        @param icon_path: file icon default, default: static/description/icon.png
        '''

        module_icon_menu = self.env['ir.ui.menu'].search([('id', '=', self.env.ref(menu_xml_id).id)], limit=1)
        module_icon_menu.write({'web_icon' : module_name + ',' + icon_path})
    