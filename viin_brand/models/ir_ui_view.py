from odoo import models, api

from ..__init__ import _get_debranding_words_map


class View(models.Model):
    _inherit = 'ir.ui.view'

    def _viindoo_debrand(self):
        words_map = _get_debranding_words_map()
        for word_origin, word_new in words_map:
            for r in self.filtered_domain([('type', '=', 'qweb')]):
                if r.arch != r.arch.replace(word_origin, word_new):
                    r.arch = r.arch.replace(word_origin, word_new)
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(View, self).create(vals_list)
        res._viindoo_debrand()
        return res
    
    def write(self, vals):
        res = super(View, self).write(vals)
        self._viindoo_debrand()
        return res
