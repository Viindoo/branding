from odoo import models

from ..tools import debrand_exception


class IrRule(models.Model):
    _inherit = 'ir.rule'

    def _make_access_error(self, operation, records):
        return debrand_exception(super()._make_access_error(operation, records))
