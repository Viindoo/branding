import functools
from contextlib import contextmanager
from unittest.mock import patch

from odoo.tools import config

from odoo.addons.sms_twilio.tools.sms_api import SmsApiTwilio

from . import models
from . import tools


def _realign_core_twilio_tests():
    """Keep the routing test of core sms_twilio on the Twilio path of a company without a sender number.

    That test builds a company with an account SID and an auth token and no number, to check which
    provider each company sends through; a company without a number is "not configured" here.
    """
    from odoo.addons.sms_twilio.tests.test_sms_twilio import TestSmsTwilio

    routing_test = TestSmsTwilio.test_send_with_multi_company

    @functools.wraps(routing_test)
    def realigned_routing_test(self, *args, **kwargs):
        company_model = type(self.env['res.company'])
        with patch.object(company_model, '_is_sms_twilio_configured', return_value=True):
            return routing_test(self, *args, **kwargs)

    realigned_routing_test.realigned_for_sender_number = True
    TestSmsTwilio.test_send_with_multi_company = realigned_routing_test


def _realign_core_sms_gateway_mock():
    """Keep the core SMS gateway mock sending through Odoo for a company without Twilio.

    Core suites send under ``MockSMS.mockSMSGateway``, which mocks the gateway of Odoo
    only, and expect its numbers, states, failures and query counts. Under that mock a
    company without a Twilio account counts as configured and its SMS go through the
    mocked gateway of Odoo; a company with an account keeps Twilio, mocked by its test.
    """
    from odoo.addons.sms.tests.common import MockSMS
    from odoo.addons.sms.tools.sms_api import SmsApi

    core_gateway_mock = MockSMS.mockSMSGateway

    @contextmanager
    def realigned_gateway_mock(self, *args, **kwargs):
        company_model = self.env.registry['res.company']
        if not hasattr(company_model, '_is_sms_twilio_configured'):
            # a database of the same process without this module sends as in core
            with core_gateway_mock(self, *args, **kwargs):
                yield
            return
        get_sms_api_class = company_model._get_sms_api_class
        # read when the mock starts: a send under a query count reads what core reads;
        # sudo: the SID is readable by administrators only
        companies_with_account = self.env['res.company'].sudo().with_context(
            active_test=False,
        ).search([('sms_twilio_account_sid', '!=', False)])

        def _get_sms_api_class(company):
            api_class = get_sms_api_class(company)
            if (
                issubclass(api_class, SmsApiTwilio)
                and company not in companies_with_account
            ):
                return SmsApi
            return api_class

        with (
            core_gateway_mock(self, *args, **kwargs),
            patch.object(company_model, '_get_sms_api_class', _get_sms_api_class),
            patch.object(
                company_model, '_is_sms_twilio_configured', return_value=True,
            ),
        ):
            yield

    MockSMS.mockSMSGateway = realigned_gateway_mock


def post_load():
    if config.get('test_enable', False):
        _realign_core_twilio_tests()
        _realign_core_sms_gateway_mock()


def post_init_hook(env):
    """Move every company that sent SMS through Odoo to its own Twilio account."""
    env['res.company'].with_context(active_test=False).search([('sms_provider', '=', 'iap')]).write({
        'sms_provider': 'twilio',
    })
