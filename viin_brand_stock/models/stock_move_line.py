from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    picking_type_use_create_lots = fields.Boolean(
        help="If this checkbox is ticked only, the system will suppose you want to create new Lots/Serial Numbers, so you can provide them in a text field.")
