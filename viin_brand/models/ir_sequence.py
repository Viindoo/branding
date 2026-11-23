from odoo import fields, models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    padding = fields.Integer(
        help="Viindoo will automatically add some '0' on the left of the "
             "'Next Number' to get the required padding size.")
