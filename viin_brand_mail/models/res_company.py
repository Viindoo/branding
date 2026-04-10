from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    email_secondary_color = fields.Char(default='#7f4282')
