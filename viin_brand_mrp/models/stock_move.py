from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    manual_consumption = fields.Boolean(
        help="When activated, then the registration of consumption for that component is recorded manually exclusively.\n"
        "If not activated, and any of the components consumption is edited manually on the manufacturing order, Viindoo assumes manual consumption also.")
