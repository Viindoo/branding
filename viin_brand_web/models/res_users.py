from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    # TODO: remove in 20.0
    # The field is declared by `viin_brand`. This declaration stays so that a database on which
    # this module is still installed keeps the field owned by an installed module.
    viin_color_scheme = fields.Selection(
        selection=[('light', "Light"), ('dark', "Dark"), ('auto', "System")],
        string="Color Scheme",
        default='light',
        help="Backend appearance: Light, Dark, or System (follow the device preference).",
    )
