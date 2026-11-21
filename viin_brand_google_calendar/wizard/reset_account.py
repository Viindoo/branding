from odoo import fields, models


class GoogleCalendarAccountReset(models.TransientModel):
    _inherit = 'google.calendar.account.reset'

    delete_policy = fields.Selection(selection_add=[('delete_odoo', "Delete from Viindoo")])
