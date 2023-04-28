from odoo import fields, models


class DigestTip(models.Model):
    _inherit = 'digest.tip'

    active = fields.Boolean(string="Active", default=True)
