from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    quick_edit_total_amount = fields.Monetary(
        help='Use this field to encode the total amount of the invoice.\n'
        'Viindoo will automatically create one invoice line with default values to match it.',
    )
