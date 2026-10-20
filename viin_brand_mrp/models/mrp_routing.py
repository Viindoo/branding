from odoo import fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    cost_mode = fields.Selection(
        help="Determines the way the system calculates the cost of the operation:\n"
        "- Based on Actual time: the cost will be calculated based on tracked time and real employee costs.\n"
        "- Based on Estimated time: the cost will be calculated based on estimated time and costs.")
