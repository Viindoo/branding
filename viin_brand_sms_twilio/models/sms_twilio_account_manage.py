from odoo import models


class SmsTwilioAccountManage(models.TransientModel):
    _inherit = 'sms.twilio.account.manage'

    def action_send_test(self):
        return super(SmsTwilioAccountManage, self.with_context(viin_brand_sms_twilio_test=True)).action_send_test()
