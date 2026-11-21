from odoo import models
from odoo.exceptions import UserError

from ..tools import debrand_exception


class ResLang(models.Model):
    _inherit = 'res.lang'

    def write(self, vals):
        try:
            return super().write(vals)
        except UserError as error:
            raise debrand_exception(error)
