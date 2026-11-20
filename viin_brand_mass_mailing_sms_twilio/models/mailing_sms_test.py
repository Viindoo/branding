from odoo import models


class MailingSmsTest(models.TransientModel):
    _inherit = 'mailing.sms.test'

    def action_send_sms(self):
        self.env.company._raise_if_sms_not_configured()
        return super().action_send_sms()
