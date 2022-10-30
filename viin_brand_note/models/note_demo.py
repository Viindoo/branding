from odoo import fields, models

class NoteDeno(models.Model):
    _inherit = 'note.note'

    active = fields.Boolean(string="Active", default=True)
