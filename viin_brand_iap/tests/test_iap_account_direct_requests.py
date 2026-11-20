from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from odoo import modules, tools
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged

REQUESTS_POST = 'odoo.addons.iap.models.iap_account.requests.post'


@tagged('post_install', '-at_install')
class TestIapAccountDirectRequests(TransactionCase):
    """The account methods that post to the IAP of Odoo S.A. without going through the JSON-RPC helper."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account = cls.env['iap.account'].create({
            'name': 'Credits',
            'service_id': cls.env.ref('iap.iap_service_reveal').id,
        })

    @contextmanager
    def _outside_test_mode(self):
        """Lift the test-mode answers of core so that a request would really be sent."""
        with patch.object(modules.module, 'current_test', None), \
             patch.dict(tools.config.options, {'test_enable': False}), \
             patch(REQUESTS_POST) as post:
            response = MagicMock()
            response.json.return_value = {'url': 'https://customer.example/credits'}
            post.return_value = response
            yield post

    def test_no_request_asks_the_iap_of_odoo_for_a_credits_page(self):
        with self._outside_test_mode() as post:
            url = self.env['iap.account'].get_credits_url('reveal', account_token='token')
        self.assertEqual(url, '')
        post.assert_not_called()

    def test_the_buttons_that_open_the_iap_of_odoo_are_refused(self):
        for method in ('action_manage', 'action_buy_credits', 'action_rotate_token'):
            with self.subTest(method=method), self._outside_test_mode() as post:
                with self.assertRaises(AccessError) as caught:
                    getattr(self.account, method)()
                self.assertIn('Viindoo', str(caught.exception))
                post.assert_not_called()

    def test_the_list_of_services_of_odoo_is_refused(self):
        with self._outside_test_mode() as post, self.assertRaises(AccessError):
            self.env['iap.account'].action_view_my_services()
        post.assert_not_called()

    def test_an_endpoint_moved_by_the_customer_is_not_refused(self):
        self.env['ir.config_parameter'].sudo().set_param('iap.endpoint', 'https://iap.customer.example')
        with self._outside_test_mode() as post:
            url = self.env['iap.account'].get_credits_url('reveal', account_token='token')
        self.assertEqual(url, 'https://customer.example/credits')
        self.assertEqual(post.call_count, 1)
