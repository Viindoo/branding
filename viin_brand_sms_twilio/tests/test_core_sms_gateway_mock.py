from contextlib import contextmanager

from odoo.tests.common import tagged

from odoo.addons.sms.tools.sms_api import SmsApi
from odoo.addons.sms_twilio.tests.common import MockSmsTwilio


@tagged('post_install', '-at_install')
class TestCoreSmsGatewayMock(MockSmsTwilio):
    """The core SMS gateway mock keeps its contract over a company sending via Twilio.

    Core suites send under ``mockSMSGateway`` and expect the numbers, states and
    failures of that mock; a company without a Twilio account reaches it as configured.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_admin.sudo().write({
            'sms_provider': 'twilio',
            'sms_twilio_account_sid': False,
            'sms_twilio_auth_token': False,
        })

    def _send_to_valid_partner(self):
        return self.valid_partner._message_sms(
            'Delivery notice', partner_ids=self.valid_partner.ids,
        )

    def test_an_sms_of_a_company_without_twilio_account_reaches_the_core_mock(self):
        with self.mockSMSGateway():
            message = self._send_to_valid_partner()
        self.assertSMSNotification(
            [{'partner': self.valid_partner}], 'Delivery notice', message,
        )
        self.assertEqual(
            [sms['number'] for sms in self._sms], [self.twilio_valid_phone_number],
        )

    def test_a_failure_simulated_by_the_core_mock_reaches_the_sms_as_in_core(self):
        with self.mockSMSGateway(sim_error='credit'):
            message = self._send_to_valid_partner()
        self.assertSMSNotification(
            [{'partner': self.valid_partner, 'state': 'exception',
              'failure_type': 'sms_credit'}],
            'Delivery notice', message,
        )

    def test_a_manual_send_under_the_core_mock_is_not_stopped(self):
        composer = self.env['sms.composer'].with_user(self.user_admin).create({
            'composition_mode': 'numbers',
            'numbers': self.twilio_valid_phone_number,
            'body': 'Hello',
        })
        with self.mockSMSGateway():
            composer.action_send_sms()
        self.assertEqual(
            [sms['number'] for sms in self._sms], [self.twilio_valid_phone_number],
        )

    def test_a_company_with_a_twilio_account_keeps_twilio_under_the_core_mock(self):
        self._setup_sms_twilio(self.company_admin)
        with self.mockSMSGateway(), self.mock_sms_twilio_send():
            self._send_to_valid_partner()
        self.assertEqual(self._sms_twilio_send_mock.call_count, 1)
        self.assertFalse(self._sms_api_contact_iap_mock.called)

    def test_outside_the_core_mock_a_company_without_twilio_account_cannot_send(self):
        with self.mockSMSGateway():
            self._send_to_valid_partner()
        message = self._send_to_valid_partner()
        notification = message.notification_ids
        self.assertEqual(notification.notification_status, 'exception')
        self.assertEqual(
            notification.failure_reason,
            self.company_admin._get_sms_not_configured_message(),
        )

    @contextmanager
    def _registry_without_this_module(self):
        """Remove the account check of this module, as on a database that lacks it."""
        company_model = self.env.registry['res.company']
        owners = {
            cls: vars(cls)['_is_sms_twilio_configured']
            for cls in company_model.__mro__
            if '_is_sms_twilio_configured' in vars(cls)
        }
        for cls in owners:
            delattr(cls, '_is_sms_twilio_configured')
        try:
            yield company_model
        finally:
            for cls, method in owners.items():
                setattr(cls, '_is_sms_twilio_configured', method)

    def test_a_database_without_this_module_gets_the_core_mock_unchanged(self):
        with (
            self._registry_without_this_module() as company_model,
            self.mockSMSGateway(),
        ):
            self.assertIs(SmsApi._contact_iap, self._sms_api_contact_iap_mock)
            self.assertNotIn('_get_sms_api_class', vars(company_model))
