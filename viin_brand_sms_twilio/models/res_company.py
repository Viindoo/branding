from odoo import fields, models
from odoo.exceptions import RedirectWarning, UserError

from odoo.addons.sms_twilio.tools.sms_api import SmsApiTwilio

from ..tools.sms_api import SmsApiTwilioViindoo


class ResCompany(models.Model):
    _inherit = 'res.company'

    sms_provider = fields.Selection(default='twilio')

    def _get_sms_api_class(self):
        api_class = super()._get_sms_api_class()
        return SmsApiTwilioViindoo if api_class is SmsApiTwilio else api_class

    def _is_sms_twilio_configured(self):
        """Tell whether the company can send SMS through its Twilio account.

        :return: ``True`` when the company does not send through Twilio (its provider is not ours to
            judge) or when it has an account SID, an auth token and a sender number
        """
        self.ensure_one()
        # sudo: the SID and the token are readable by administrators only, and any sender may ask
        company = self.sudo()
        if company.sms_provider != 'twilio':
            return True
        return bool(company.sms_twilio_account_sid and company.sms_twilio_auth_token and company.sms_twilio_number_ids)

    def _get_sms_not_configured_message(self):
        self.ensure_one()
        return self.env._(
            "SMS sending is not configured for %(company)s. An administrator has to enter the Twilio account "
            "in Settings > General Settings > Contacts > Send SMS.",
            company=self.name,
        )

    def _raise_if_sms_not_configured(self):
        """Stop a manual send before any SMS is created when none of the companies can send.

        :raises RedirectWarning: for an administrator, with a button that opens the settings
        :raises UserError: for any other user, with the same sentence
        """
        if not self or any(company._is_sms_twilio_configured() for company in self):
            return
        message = self[0]._get_sms_not_configured_message()
        if not self.env.user.has_group('base.group_system'):
            raise UserError(message)
        action = self.env['ir.actions.act_window']._for_xml_id('base_setup.action_general_configuration')
        raise RedirectWarning(message, action, self.env._("Open Settings"))
