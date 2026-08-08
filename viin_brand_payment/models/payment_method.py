from odoo import fields, models


class PaymentMethod(models.Model):
    _inherit = 'payment.method'

    support_refund = fields.Selection(
        help="Refund is a feature allowing to refund customers directly from the payment in the system.")
