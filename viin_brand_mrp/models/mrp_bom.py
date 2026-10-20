from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    allow_operation_dependencies = fields.Boolean(
        help="Create operation level dependencies that will influence both planning and the status of work orders upon MO confirmation. If this feature is ticked, and nothing is specified, the system will assume that all operations can be started simultaneously.")
