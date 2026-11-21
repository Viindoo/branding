from unittest.mock import MagicMock, patch

from odoo.addons.sms.tools.sms_api import SmsApi
from odoo.addons.sms_twilio.tools.sms_api import SmsApiTwilio
from odoo.addons.sms_twilio.tests.common import MockSmsTwilio
from odoo.exceptions import RedirectWarning, UserError
from odoo.tests.common import tagged
from odoo.tools import mute_logger
from odoo.tools.translate import code_translations


@tagged('post_install', '-at_install')
class TestSmsNotConfigured(MockSmsTwilio):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_admin.sudo().write({
            'sms_provider': 'twilio',
            'sms_twilio_account_sid': False,
            'sms_twilio_auth_token': False,
        })

    def _make_composer(self, user=None):
        composer = self.env['sms.composer'].with_user(user or self.env.user).create({
            'composition_mode': 'numbers',
            'numbers': self.twilio_valid_phone_number,
            'body': 'Hello',
        })
        return composer

    def test_a_manual_send_stops_before_any_sms_is_created_and_offers_the_settings(self):
        composer = self._make_composer(self.user_admin)
        sms_count = self.env['sms.sms'].sudo().search_count([])
        with patch.object(SmsApi, '_contact_iap') as contact_iap, \
             self.assertRaises(RedirectWarning) as caught:
            composer.with_user(self.user_admin).action_send_sms()
        contact_iap.assert_not_called()
        self.assertEqual(self.env['sms.sms'].sudo().search_count([]), sms_count)
        action = caught.exception.args[1]
        self.assertEqual(action['res_model'], 'res.config.settings')

    def test_the_sentence_names_the_setting_where_the_twilio_account_is_entered(self):
        message = self.company_admin.with_context(lang='en_US')._get_sms_not_configured_message()
        self.assertIn('Settings > General Settings > Contacts > Send SMS', message)
        self.assertNotIn('General Settings > SMS', message)

    def test_a_user_who_cannot_configure_reads_the_same_sentence_without_a_button(self):
        composer = self._make_composer(self.basic_user)
        with self.assertRaises(UserError) as caught:
            composer.action_send_sms()
        self.assertNotIsInstance(caught.exception, RedirectWarning)
        self.assertEqual(str(caught.exception), self.company_admin._get_sms_not_configured_message())

    def test_an_automatic_sms_fails_with_the_server_failure_and_the_sentence(self):
        message = self.valid_partner._message_sms('Delivery notice', partner_ids=self.valid_partner.ids)
        notification = message.notification_ids
        self.assertEqual(notification.notification_status, 'exception')
        self.assertEqual(notification.failure_type, 'sms_server')
        self.assertEqual(notification.failure_reason, self.company_admin._get_sms_not_configured_message())

    def test_an_automation_rule_sms_does_not_interrupt_the_record_change(self):
        template = self.env['sms.template'].create({
            'name': 'Automation SMS',
            'model_id': self.env['ir.model']._get_id('res.partner'),
            'body': 'Hello',
        })
        action = self.env['ir.actions.server'].create({
            'name': 'Send SMS',
            'model_id': self.env['ir.model']._get_id('res.partner'),
            'state': 'sms',
            'sms_template_id': template.id,
            'sms_method': 'sms',
        })
        action.with_context(active_model='res.partner', active_id=self.valid_partner.id).run()

    def test_a_company_with_a_twilio_account_still_sends(self):
        self._setup_sms_twilio(self.company_admin)
        composer = self._make_composer(self.user_admin)
        with self.mock_sms_twilio_gateway():
            composer.with_user(self.user_admin).action_send_sms()
        self.assertEqual([sms['number'] for sms in self._sms], [self.twilio_valid_phone_number])

    def test_the_test_sms_of_the_twilio_wizard_is_signed_viindoo(self):
        self._setup_sms_twilio(self.company_admin)
        wizard = self.env['sms.twilio.account.manage'].with_user(self.user_admin).create({
            'test_number': '+32455001122',
        })
        with self.mock_sms_twilio_send():
            wizard.action_send_test()
        self.assertIn('Viindoo', self._sms[0]['body'])
        self.assertNotIn('Odoo', self._sms[0]['body'])

    def test_credentials_without_a_sender_number_are_not_a_configured_account(self):
        self._setup_sms_twilio(self.company_admin)
        self.company_admin.sudo().sms_twilio_number_ids.unlink()
        composer = self._make_composer(self.user_admin)
        with self.assertRaises(RedirectWarning):
            composer.with_user(self.user_admin).action_send_sms()

    def test_the_sentence_names_the_company_that_cannot_send(self):
        self.assertIn(self.company_admin.name, self.company_admin._get_sms_not_configured_message())

    def _make_partner_of_company(self, company):
        return self.env['res.partner'].create({
            'name': 'Partner of %s' % company.name,
            'phone': self.twilio_valid_phone_number,
            'company_id': company.id,
        })

    def _make_record_composer(self, partner):
        self.env.user.sudo().company_ids |= partner.company_id
        return self.env['sms.composer'].with_context(
            allowed_company_ids=(self.company_admin | partner.company_id).ids,
        ).create({
            'composition_mode': 'comment',
            'res_model': 'res.partner',
            'res_id': partner.id,
            'body': 'Hello',
        })

    def test_a_message_on_a_record_of_a_configured_company_is_not_stopped_by_the_current_company(self):
        company = self.env['res.company'].sudo().create({'name': 'Configured Company'})
        self._setup_sms_twilio(company)
        composer = self._make_record_composer(self._make_partner_of_company(company))
        with self.mock_sms_twilio_gateway():
            composer.action_send_sms()
        self.assertEqual([sms['number'] for sms in self._sms], [self.twilio_valid_phone_number])

    def test_a_message_on_a_record_of_an_unconfigured_company_is_stopped_whatever_the_current_company(self):
        self._setup_sms_twilio(self.company_admin)
        company = self.env['res.company'].sudo().create({'name': 'Unconfigured Company'})
        composer = self._make_record_composer(self._make_partner_of_company(company))
        with self.assertRaises(RedirectWarning) as caught:
            composer.action_send_sms()
        self.assertIn(company.name, caught.exception.args[0])

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

    def test_the_test_sms_of_the_wizard_reaches_twilio_even_without_a_sender_number(self):
        self._setup_sms_twilio(self.company_admin)
        self.company_admin.sudo().sms_twilio_number_ids.unlink()
        wizard = self.env['sms.twilio.account.manage'].with_user(self.user_admin).create({
            'test_number': '+32455001122',
        })
        with self.mock_sms_twilio_send():
            wizard.action_send_test()
        self.assertEqual(len(self._sms), 1)

    @mute_logger('odoo.addons.sms_twilio.tools.sms_api')
    def test_a_reason_answered_by_twilio_is_kept_as_the_vendor_wrote_it(self):
        self._setup_sms_twilio(self.company_admin)
        response = MagicMock(ok=False)
        response.json.return_value = {'code': 1, 'message': 'Odoo is named in this vendor message'}
        with patch.object(SmsApiTwilio, '_sms_twilio_send_request', return_value=response):
            message = self.valid_partner._message_sms('Delivery notice', partner_ids=self.valid_partner.ids)
        self.assertEqual(message.notification_ids.failure_reason, 'Odoo is named in this vendor message')
