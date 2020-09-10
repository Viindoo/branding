from odoo import models
import os

class ViinBrandBase(models.AbstractModel):
    _name = 'viin.brand.base'
    _description = 'Viindoo Brand Base model'
    
    
    def update_icon(self, module_name, module_branding, icon = 'icon.png'):
        module = self.sudo().env['ir.module.module'].search([('name', '=', module_name)], limit=1)
        module.write({'icon' : '/' + module_branding + '/static/description/' + icon})
        module._get_icon_image()
    
    def restore_icon(self, full_xml_id, icon = 'icon.png'):
        module_name = full_xml_id.split('.')[0]
        module_icon = self.sudo().env['ir.module.module'].search([('name', '=', module_name)], limit=1)
        module_icon.write({'icon' : '/'+module_name+'/static/description/'+icon})
        module_icon._get_icon_image()
        
        module_icon_menu = self.sudo().env['ir.ui.menu'].search([('id', '=', self.sudo().env.ref(full_xml_id).id)], limit=1)
        module_icon_menu.write({'web_icon' : module_name+',static/description/'+icon})
    