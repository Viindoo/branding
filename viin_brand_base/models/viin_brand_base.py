from odoo import models

class ViinBrandBase(models.AbstractModel):
    _name = 'viin.brand.base'
    _description = 'Viindoo Brand Base model'
    
    
    def update_icon(self, module_name, module_branding, icon = 'icon.png'):
        '''
        Update new icon for module
        
        @param module_name: module name want to change icon
        @param module_branding: module name contains icon file and handle
        @param icon: file icon, default: icon.png
        '''
        
        module = self.env['ir.module.module'].search([('name', '=', module_name)], limit=1)
        module.write({'icon' : '/' + module_branding + '/static/description/' + icon})
        module._get_icon_image()
    
    def restore_icon(self, module_name, xml_id, icon = 'icon.png'):
        '''
        Restore original icon of module
        
        @param module_name: module name want to restore icon
        @param xml_id: full xml id of menuitem web_icon, example: crm.crm_menu_root
        @param icon: file icon default, default: icon.png
        '''
        module_icon = self.env['ir.module.module'].search([('name', '=', module_name)], limit=1)
        module_icon.write({'icon' : '/'+module_name+'/static/description/'+icon})
        module_icon._get_icon_image()
        
        module_icon_menu = self.env['ir.ui.menu'].search([('id', '=', self.sudo().env.ref(xml_id).id)], limit=1)
        module_icon_menu.write({'web_icon' : module_name+',static/description/'+icon})
    