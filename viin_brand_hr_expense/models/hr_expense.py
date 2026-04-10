from odoo import models
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    def _get_base_account(self):
        try:
            return super()._get_base_account()
        except UserError as e:
            raise UserError(str(e).replace('Odoo', 'The system')) from None
