from odoo.addons.viin_brand.models.mail_template import MailTemplate
from odoo import models, api


class View(models.Model):
    _inherit = 'ir.ui.view'

    def replace_brand(self):
        word = MailTemplate._prepare_word_replace(self)  
        for word_origin, word_new in word:
            for r in self.filtered_domain([('type', '=', 'qweb')]):
                if r.arch != r.arch.replace(word_origin, word_new):
                    r.arch = r.arch.replace(word_origin, word_new)
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(View, self).create(vals_list)
        res.replace_brand()
        return res
    
    def write(self, vals):
        res = super(View, self).write(vals)
        self.replace_brand()
        return res
