from odoo.addons.sms_twilio.tools.sms_api import SmsApiTwilio
from odoo.tools.translate import LazyTranslate

# The failure reason core writes when Twilio gives no answer, looked up in the catalog of the core
# module that owns it so that it equals what core wrote in every language.
CORE_NO_ANSWER_REASON = LazyTranslate('sms_twilio')("Unknown failure at sending, please contact Odoo support")


class SmsApiTwilioViindoo(SmsApiTwilio):
    """Twilio provider whose failure reasons written by Odoo send the user to Viindoo for support.

    The reasons that Twilio answers are the vendor's text and stay as they came.
    """

    def _send_sms_batch(self, messages, delivery_reports_url=False):
        results = super()._send_sms_batch(messages, delivery_reports_url=delivery_reports_url)
        no_answer_reason = CORE_NO_ANSWER_REASON._translate(self.env.lang or 'en_US')
        for result in results:
            if result.get('failure_reason') == no_answer_reason:
                result['failure_reason'] = no_answer_reason.replace('Odoo', 'Viindoo')
        return results

    def _get_sms_api_error_messages(self):
        return {
            failure_type: message.replace('Odoo', 'Viindoo')
            for failure_type, message in super()._get_sms_api_error_messages().items()
        }
