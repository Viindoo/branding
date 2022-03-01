from odoo import models
from odoo.addons.http_routing.models.ir_http import slugify



class Module(models.Model):
    _inherit = 'ir.module.module'
    
    def make_url(self):
        """
        Convert module's name to compatible string for web url
        E.g: Discuss=> discuss
        Live Chat => live-chat
        Accounting & Finance => accounting-finance
        """
        self.ensure_one()
        module_name_url = slugify(self.shortdesc)

        #set value for exist landing page viindoo
        if module_name_url == 'accounting-finance':
            module_name_url = 'accounting'
        if module_name_url == 'contacts':
            module_name_url = 'contact'
        if module_name_url == 'surveys':
            module_name_url = 'survey'
        if module_name_url == 'manufacturing':
            module_name_url = 'mrp'
        if module_name_url == 'elearning':
            module_name_url = 'e-learning'
        if module_name_url == 'events':
            module_name_url = 'event'
        if module_name_url == 'expenses':
            module_name_url = 'expense'
        if module_name_url == 'point-of-sale':
            module_name_url = 'pos'
        if module_name_url == 'forum':
            module_name_url = 'app-forum'
        if module_name_url == 'meal-orders':
            module_name_url = 'hr-meal'
        if module_name_url == 'repairs':
            module_name_url = 'repair'
        return module_name_url
