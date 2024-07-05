from odoo import fields, models


class AliasDomain(models.Model):
    _inherit = 'mail.alias.domain'

    name = fields.Char(help="Email domain e.g. 'example.com' in 'viindoo@example.com'")
