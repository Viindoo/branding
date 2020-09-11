from odoo import models
from pip._internal import self_outdated_check

class ViinBrandBase(models.AbstractModel):
    _name = 'viin.brand.base'
    _description = 'Viindoo Brand Base model'
    
    
    def update_module_icon(self, module_name, module_brand, icon_path = 'static/description/icon.png'):
        self._modify_module_icon(module_name, module_brand, icon_path)
    
    def update_menu_icon(self, module_name, module_branding, xml_id, icon_path = 'static/description/icon.png'):
        full_xml_id = self._full_xml_id(module_name, xml_id)
        self._modify_menu_icon(module_branding, full_xml_id, icon_path)
        
    def restore_module_icon(self, module_name, icon_path = 'static/description/icon.png'):
        '''
        When restore icon module, set param `module_brand` = False
        '''
        self._modify_module_icon(module_name, False, icon_path)
    
    def restore_menu_icon(self, module_name, xml_id, icon_path = 'static/description/icon.png'):
        full_xml_id = self._full_xml_id(module_name, xml_id)
        self._modify_menu_icon(module_name, full_xml_id, icon_path)
        
    def _modify_module_icon(self, module_name, module_brand, icon_path):
        '''
        Change module icon
        
        @param module_name: module name want to set icon
        @param module_brand: module name contains icon file and handle
        @param icon_path: path file icon
        '''
        
        module = self.env['ir.module.module'].search([('name', '=', module_name)], limit=1)
        module.write({'icon' : '/' + (module_brand or module_name) + '/' + icon_path})
        module._get_icon_image()
        
    def _modify_menu_icon(self, module_name, full_xml_id, icon_path):
        '''
        Change menu icon
        
        @param module_name: module name want to set icon
        @param full_xml_id: FULL xml id of menuitem web_icon, example: crm.crm_menu_root
        @param icon_path: path file icon
        '''
        
        module_icon_menu = self.env['ir.ui.menu'].search([('id', '=', self.env.ref(full_xml_id).id)], limit=1)
        module_icon_menu.write({'web_icon' : module_name + ',' + icon_path})
        
    def _full_xml_id(self, module_name, xml_id):
        '''
        Get full xml_id
        '''
        if xml_id.split('.')[0] and module_name == xml_id.split('.')[0]:
            full_xml_id = xml_id
        else:
            full_xml_id = module_name + '.' + xml_id
            
        return full_xml_id
    