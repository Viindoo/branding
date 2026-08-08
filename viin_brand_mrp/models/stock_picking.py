from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    auto_print_done_production_order = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the production order of a MO when it is done.")
    auto_print_done_mrp_product_labels = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the product labels of a MO when it is done.")
    auto_print_done_mrp_lot = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the lot/SN label of a MO when it is done.")
    auto_print_mrp_reception_report = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the allocation report of a MO when it is done and has assigned moves.")
    auto_print_mrp_reception_report_labels = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the allocation report labels of a MO when it is done.")
