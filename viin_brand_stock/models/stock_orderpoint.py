from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    product_min_qty = fields.Float(
        help="When the virtual stock goes below the Min Quantity specified for this field, the system generates "
        "a procurement to bring the forecasted quantity above of this Min Quantity.")

    product_max_qty = fields.Float(
        help="When the virtual stock goes below the Min Quantity, the system generates "
        "a procurement to bring the forecasted quantity up to (or near to) the Max Quantity specified for this field (or to Min Quantity, whichever is bigger).")
