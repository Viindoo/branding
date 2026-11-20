from odoo import fields, models


class ResUsersSettings(models.Model):
    _inherit = 'res.users.settings'

    google_calendar_cal_id = fields.Char(
        help="Last Calendar ID who has been synchronized. If it is changed, we remove all links "
             "between GoogleID and Viindoo Google Internal ID",
    )
