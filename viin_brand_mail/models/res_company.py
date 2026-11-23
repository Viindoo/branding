from odoo import fields, models

from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Core defaults the notification button colour to the legacy Odoo purple, and that stored
    # default paints the button, so the field default itself is re-keyed. White button text on
    # the brand purple passes WCAG AA contrast.
    email_secondary_color = fields.Char(default=VIINDOO_BRAND_COLOR)
