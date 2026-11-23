# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestGoogleCalendarDebrand(TransactionCase):

    def test_reset_wizard_option_is_labelled_after_viindoo(self):
        field = self.env["google.calendar.account.reset"].fields_get(["delete_events"])["delete_events"]
        self.assertEqual(field["type"], "boolean")
        self.assertNotRegex(field["string"], BRAND_NAME)
        self.assertIn("Viindoo", field["string"])
