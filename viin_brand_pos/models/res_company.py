from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    point_of_sale_use_ticket_qr_code = fields.Boolean(
        help="Print information on the receipt to allow the customer to easily access the invoice anytime, from the customer portal.")
