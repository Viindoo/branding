from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Core defaults the notification button colour to the legacy Odoo purple, and that stored
    # default paints the button, so the field default itself is re-keyed. White button text on
    # #7f4282 passes WCAG AA contrast.
    email_secondary_color = fields.Char(default='#7f4282')
