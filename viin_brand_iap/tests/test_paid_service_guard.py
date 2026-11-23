from unittest.mock import MagicMock, patch

import requests

import odoo.addons.iap as iap
from odoo import modules
from odoo.addons.iap.tools import iap_tools
from odoo.addons.viin_brand_iap import post_load
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged

PAID_URLS = [
    'https://iap.odoo.com/iap/1/balance',
    'https://iap-services.odoo.com/iap/lead/enrich',
    'https://partner-autocomplete.odoo.com/api/dnb/1/search_by_name',
    'https://sms.api.odoo.com/api/sms/3/send',
    'https://iap-snailmail.odoo.com/iap/snailmail/1/print',
]
FREE_URLS = [
    'https://website.api.odoo.com/api/website/2/configurator/industries',
    'https://olg.api.odoo.com/api/olg/1/chat',
    'https://ots.api.odoo.com/api/html_editor_translate/1/google_translate',
]


@tagged('post_install', '-at_install')
class TestPaidServiceGuard(TransactionCase):

    def _call_with_network(self, url, call=None, **kwargs):
        """Run ``call`` on ``url`` with the test-mode refusal of core lifted and the network replaced."""
        response = MagicMock()
        response.json.return_value = {'result': 'reached'}
        response.elapsed.total_seconds.return_value = 0.0
        with patch.object(modules.module, 'current_test', None), \
             patch.object(iap_tools.requests, 'post', return_value=response) as post:
            try:
                result = (call or iap_tools.iap_jsonrpc)(url, params={}, **kwargs)
            except (requests.RequestException, UserError):
                result = None
        return result, post

    def test_credit_based_services_of_odoo_never_leave_the_server(self):
        for url in PAID_URLS:
            with self.subTest(url=url):
                result, post = self._call_with_network(url)
                self.assertIsNone(result)
                post.assert_not_called()

    def test_the_refusal_is_the_failure_of_an_unreachable_service_and_names_viindoo(self):
        with patch.object(modules.module, 'current_test', None):
            with self.assertRaises(requests.RequestException) as caught:
                iap_tools.iap_jsonrpc(PAID_URLS[0], params={})
        self.assertIn('Viindoo', str(caught.exception))
        self.assertNotIn('Odoo', str(caught.exception))

    def test_a_caller_that_asked_for_a_user_error_gets_one(self):
        for kwargs, args in (({'raise_user_error': True}, ()), ({}, ('call', {}, 15, True))):
            with self.subTest(kwargs=kwargs, args=args):
                with patch.object(modules.module, 'current_test', None):
                    with self.assertRaises(UserError) as caught:
                        iap_tools.iap_jsonrpc(PAID_URLS[3], *args, **kwargs)
                self.assertIn('Viindoo', str(caught.exception))
                self.assertNotIn('Odoo', str(caught.exception))

    def test_a_core_caller_that_handles_an_unreachable_service_handles_the_refusal(self):
        self.env['iap.account'].create({
            'name': 'Credits',
            'service_id': self.env.ref('iap.iap_service_reveal').id,
        })
        with patch.object(modules.module, 'current_test', None):
            credit = self.env['iap.account'].get_credits('reveal')
        self.assertEqual(credit, -1)

    def test_free_background_services_are_reached_unchanged(self):
        for url in FREE_URLS:
            with self.subTest(url=url):
                result, post = self._call_with_network(url)
                self.assertEqual(result, 'reached')
                self.assertEqual(post.call_args.args[0], url)

    def test_the_compatibility_alias_is_guarded_too(self):
        result, post = self._call_with_network(PAID_URLS[3], call=iap.jsonrpc)
        self.assertIsNone(result)
        post.assert_not_called()

    def test_the_url_may_be_passed_by_keyword(self):
        with patch.object(modules.module, 'current_test', None):
            with self.assertRaises(requests.RequestException):
                iap_tools.iap_jsonrpc(url=PAID_URLS[1], params={})

    def test_an_endpoint_moved_by_the_customer_to_another_host_is_not_blocked(self):
        result, post = self._call_with_network('https://iap.customer.example/iap/1/balance')
        self.assertEqual(result, 'reached')
        self.assertEqual(post.call_count, 1)

    def test_loading_the_module_twice_wraps_the_entry_point_once(self):
        wrapper = iap_tools.iap_jsonrpc
        post_load()
        self.assertIs(iap_tools.iap_jsonrpc, wrapper)
        self.assertIs(iap.jsonrpc, wrapper)
