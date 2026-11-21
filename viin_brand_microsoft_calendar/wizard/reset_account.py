from odoo import fields, models


class MicrosoftCalendarAccountReset(models.TransientModel):
    _inherit = 'microsoft.calendar.account.reset'

    delete_policy = fields.Selection(selection_add=[('delete_odoo', "Delete from Viindoo")])
