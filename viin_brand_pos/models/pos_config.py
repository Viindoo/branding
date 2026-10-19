from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    sequence_id = fields.Many2one(
        help="This sequence is automatically created by the system but you can change it "
        "to customize the reference numbers of your orders.")
    sequence_line_id = fields.Many2one(
        help="This sequence is automatically created by the system but you can change it "
        "to customize the reference numbers of your orders lines.")
