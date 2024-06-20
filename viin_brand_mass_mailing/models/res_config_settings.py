from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mass_mailing_outgoing_mail_server = fields.Boolean(
        help='Use a specific mail server in priority. Otherwise Viindoo relies on the first outgoing mail server available (based on their sequencing) as it does for normal mails.')
