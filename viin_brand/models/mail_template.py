from odoo import models, api


class MailTemplate(models.Model):
    _inherit = 'mail.template'
    
    def _prepare_word_replace(self):
        return [
            ('Odoo', 'Viindoo EOS'),
            ('www.odoo.com', 'www.viindoo.com'),
            ('www.openerp.com', 'www.viindoo.com')
        ]
    
    def replace_brand(self):
        word = self._prepare_word_replace()  
        for word_origin, word_new in word:
            for r in self.filtered(lambda m: m.body_html):
                if r.body_html != r.body_html.replace(word_origin, word_new):
                    r.body_html = r.body_html.replace(word_origin, word_new)
    
    @api.model
    def create(self, vals):
        res = super(MailTemplate, self).create(vals)
        res.replace_brand()
        return res
    
    def write(self, vals):
        res = super(MailTemplate, self).write(vals)
        self.replace_brand()
        return res
