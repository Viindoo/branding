from odoo import models, api
from ..__init__ import _get_debranding_words_map


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    def _viindoo_debrand(self):
        words_map = _get_debranding_words_map()
        for word_origin, word_new in words_map:
            for r in self.filtered(lambda m: m.body_html and m.body_html != m.body_html.replace(word_origin, word_new)):
                r.body_html = r.body_html.replace(word_origin, word_new)
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(MailTemplate, self).create(vals_list)
        res._viindoo_debrand()
        return res
    
    def write(self, vals):
        res = super(MailTemplate, self).write(vals)
        self._viindoo_debrand()
        return res
