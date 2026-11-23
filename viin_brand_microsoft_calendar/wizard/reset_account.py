from odoo import fields, models


class MicrosoftCalendarAccountReset(models.TransientModel):
    _inherit = 'microsoft.calendar.account.reset'

    delete_events = fields.Boolean(string="Delete synced events from Viindoo")
