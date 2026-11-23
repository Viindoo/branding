from odoo import fields, models


class GoogleCalendarAccountReset(models.TransientModel):
    _inherit = 'google.calendar.account.reset'

    delete_events = fields.Boolean(string="Delete synced events from Viindoo")
