from odoo import models

from ..tools import debrand_exception


class IrAccess(models.Model):
    _inherit = 'ir.access'

    def _make_record_access_error(self, records, operation):
        return debrand_exception(super()._make_record_access_error(records, operation))
