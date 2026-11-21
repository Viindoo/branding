from odoo import models

from odoo.addons.sms_twilio.tools.sms_api import SmsApiTwilio

from ..tools.sms_api import SmsApiNotConfigured


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    def _split_by_api(self):
        for sms_api, sms in super()._split_by_api():
            # the test SMS of the Twilio wizard is sent to learn whether the account works
            is_wizard_test = self.env.context.get('viin_brand_sms_twilio_test')
            if (
                isinstance(sms_api, SmsApiTwilio) and not is_wizard_test
                and not sms_api.company._is_sms_twilio_configured()
            ):
                not_configured_api = SmsApiNotConfigured(self.env)
                not_configured_api._set_company(sms_api.company)
                yield not_configured_api, sms
            else:
                yield sms_api, sms
