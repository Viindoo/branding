import re

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAnalyticBrandHelp(TransactionCase):

    def test_analytic_items_empty_state_names_viindoo_not_odoo(self):
        for xmlid in (
            'analytic.account_analytic_line_action',
            'analytic.account_analytic_line_action_entries',
        ):
            with self.subTest(action=xmlid):
                help_text = self.env.ref(xmlid).help
                self.assertTrue(help_text)
                self.assertNotRegex(help_text, r'\bOdoo\b')
                self.assertIsNotNone(re.search(r'In Viindoo,', help_text))
