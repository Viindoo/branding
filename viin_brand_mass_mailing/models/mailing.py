from odoo import fields, models


class MassMailing(models.Model):
    _inherit = 'mailing.mailing'

    # override
    mail_server_id = fields.Many2one(help="Use a specific mail server in priority. Otherwise Viindoo relies on the first outgoing mail server available (based on their sequencing) as it does for normal mails.")
