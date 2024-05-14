from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    apps_menu_theme = fields.Selection(selection_add=[('viindoo', 'Viindoo')],
        ondelete={'viindoo': 'set default'},
        default='viindoo'
    )
