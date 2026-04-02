from odoo import models, fields


class Users(models.Model):
    _inherit = 'res.users'

    # Override to branding
    odoobot_state = fields.Selection(string='ViindooBot Status')
