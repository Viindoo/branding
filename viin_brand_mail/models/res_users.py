from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'
    
    notification_type = fields.Selection(
        selection_add=[('email',), ('inbox', 'Handle in Viindoo')])
