from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    allow_operation_dependencies = fields.Boolean(
        help="Create operation level dependencies that will influence both planning and the status of work orders upon MO confirmation. If this feature is ticked, and nothing is specified, the system will assume that all operations can be started simultaneously.")


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    manual_consumption = fields.Boolean(
        help="When activated, then the registration of consumption for that component is recorded manually exclusively.\n"
        "If not activated, and any of the components consumption is edited manually on the manufacturing order, the system assumes manual consumption also.")
