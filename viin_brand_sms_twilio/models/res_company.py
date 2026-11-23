from odoo import fields, models

from odoo.addons.sms_twilio.tools.sms_api import SmsApiTwilio

from ..tools.sms_api import SmsApiTwilioViindoo


class ResCompany(models.Model):
    _inherit = 'res.company'

    sms_provider = fields.Selection(default='twilio')

    def _get_sms_api_class(self):
        api_class = super()._get_sms_api_class()
        return SmsApiTwilioViindoo if api_class is SmsApiTwilio else api_class
