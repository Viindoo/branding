# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestGoogleCalendarDebrand(TransactionCase):

    def test_reset_wizard_option_is_labelled_after_viindoo(self):
        field = self.env["google.calendar.account.reset"].fields_get(["delete_policy"])["delete_policy"]
        labels = dict(field["selection"])
        self.assertNotRegex(labels["delete_odoo"], BRAND_NAME)
        self.assertIn("Viindoo", labels["delete_odoo"])
        self.assertEqual(
            set(labels), {"dont_delete", "delete_google", "delete_odoo", "delete_both"},
            "the other options stay as core defines them",
        )

    def test_synchronised_calendar_id_help_names_no_odoo(self):
        for model in ("res.users.settings", "res.users"):
            help_text = self.env[model].fields_get(["google_calendar_cal_id"], attributes=["help"])[
                "google_calendar_cal_id"]["help"]
            self.assertNotRegex(help_text, BRAND_NAME, model)
