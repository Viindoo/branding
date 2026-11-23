from unittest.mock import MagicMock, patch

from odoo.tests.common import tagged
from odoo.tools import mute_logger
from odoo.tools.translate import code_translations

from odoo.addons.sms_twilio.tests.common import MockSmsTwilio
from odoo.addons.sms_twilio.tools.sms_api import SmsApiTwilio


@tagged('post_install', '-at_install')
class TestTwilioSmsDebrand(MockSmsTwilio):
    """The SMS that go through Twilio name Viindoo, and a company without a Twilio account is not blocked."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # sudo: the SID and the auth token are written by administrators only
        cls.company_admin.sudo().write({
            'sms_provider': 'twilio',
            'sms_twilio_account_sid': False,
            'sms_twilio_auth_token': False,
        })

    def test_a_manual_send_of_a_company_without_twilio_account_is_not_stopped(self):
        composer = self.env['sms.composer'].with_user(self.user_admin).create({
            'composition_mode': 'numbers',
            'numbers': self.twilio_valid_phone_number,
            'body': 'Hello',
        })

        with mute_logger('odoo.addons.sms.models.sms_sms'):
            composer.action_send_sms()

        # sudo: the SMS log is read as the test administrator
        sms = self.env['sms.sms'].sudo().search([('number', '=', self.twilio_valid_phone_number)])
        self.assertEqual(sms.mapped('state'), ['error'], 'the SMS is kept, failed by the answer of Twilio')

    def test_the_test_sms_of_the_twilio_wizard_is_signed_viindoo(self):
        self._setup_sms_twilio(self.company_admin)
        wizard = self.env['sms.twilio.account.manage'].with_user(self.user_admin).create({
            'test_number': '+32455001122',
        })
        with self.mock_sms_twilio_send():
            wizard.action_send_test()
        self.assertIn('Viindoo', self._sms[0]['body'])
        self.assertNotIn('Odoo', self._sms[0]['body'])

    def test_a_twilio_failure_without_an_answer_sends_the_user_to_viindoo_support(self):
        self._setup_sms_twilio(self.company_admin)
        with patch.object(SmsApiTwilio, '_sms_twilio_send_request', return_value=None):
            message = self.valid_partner._message_sms('Delivery notice', partner_ids=self.valid_partner.ids)
        reason = message.notification_ids.failure_reason
        self.assertIn('Viindoo', reason)
        self.assertNotIn('Odoo', reason)

    def test_a_failure_without_an_answer_is_rewritten_in_a_language_where_core_translates_it(self):
        self._setup_sms_twilio(self.company_admin)
        self.env['res.lang']._activate_lang('vi_VN')
        core_text = 'Unknown failure at sending, please contact Odoo support'
        translated = 'Loi khong xac dinh khi gui, vui long lien he ho tro Odoo'
        messages = [{'content': 'Hello', 'numbers': [{'uuid': 'u1', 'number': self.twilio_valid_phone_number}]}]
        api = self.company_admin._get_sms_api_class()(self.env(context=dict(self.env.context, lang='vi_VN')))
        with patch.dict(code_translations.python_translations, {('sms_twilio', 'vi_VN'): {core_text: translated}}), \
             patch.object(SmsApiTwilio, '_sms_twilio_send_request', return_value=None):
            results = api._send_sms_batch(messages)
        self.assertEqual(results[0]['failure_reason'], translated.replace('Odoo', 'Viindoo'))

    def test_a_twilio_error_message_sends_the_user_to_viindoo_support(self):
        self._setup_sms_twilio(self.company_admin)
        api = self.company_admin._get_sms_api_class()(self.env)
        for failure_type, message in api._get_sms_api_error_messages().items():
            with self.subTest(failure_type=failure_type):
                self.assertNotIn('Odoo', message)

    @mute_logger('odoo.addons.sms_twilio.tools.sms_api')
    def test_a_reason_answered_by_twilio_is_kept_as_the_vendor_wrote_it(self):
        self._setup_sms_twilio(self.company_admin)
        response = MagicMock(ok=False)
        response.json.return_value = {'code': 1, 'message': 'Odoo is named in this vendor message'}
        with patch.object(SmsApiTwilio, '_sms_twilio_send_request', return_value=response):
            message = self.valid_partner._message_sms('Delivery notice', partner_ids=self.valid_partner.ids)
        self.assertEqual(message.notification_ids.failure_reason, 'Odoo is named in this vendor message')
