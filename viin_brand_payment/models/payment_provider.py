from odoo import fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    capture_manually = fields.Boolean(
        help="Capture the amount from the system, when the delivery is completed.\n"
        "Use this if you want to charge your customers cards only when\n"
        "you are sure you can ship the goods to them.")

    support_refund = fields.Selection(
        help="Refund is a feature allowing to refund customers directly from the payment in the system.")
