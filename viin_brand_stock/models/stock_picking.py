from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    auto_show_reception_report = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically show the reception report (if there are moves to allocate to) when validating.")
    auto_print_delivery_slip = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the delivery slip of a picking when it is validated.")
    auto_print_return_slip = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the return slip of a picking when it is validated.")
    auto_print_product_labels = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the product labels of a picking when it is validated.")
    auto_print_lot_labels = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the lot/SN labels of a picking when it is validated.")
    auto_print_reception_report = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the reception report of a picking when it is validated and has assigned moves.")
    auto_print_reception_report_labels = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the reception report labels of a picking when it is validated.")
    auto_print_packages = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the packages and their contents of a picking when it is validated.")
    auto_print_package_label = fields.Boolean(
        help="If this checkbox is ticked, the system will automatically print the package label when \"Put in Pack\" button is used.")
