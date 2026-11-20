# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re
from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestMicrosoftCalendarDebrand(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["calendar.event"].with_context(no_mail_to_attendees=True).create({
            "name": "Sync",
            "start": "2026-03-02 09:00:00",
            "stop": "2026-03-02 10:00:00",
        })

    def test_reset_wizard_option_is_labelled_after_viindoo(self):
        field = self.env["microsoft.calendar.account.reset"].fields_get(["delete_policy"])["delete_policy"]
        labels = dict(field["selection"])
        self.assertNotRegex(labels["delete_odoo"], BRAND_NAME)
        self.assertIn("Viindoo", labels["delete_odoo"])

    def test_organizer_error_names_viindoo(self):
        other_user = self.env["res.users"].create({"name": "Organizer", "login": "ms_organizer"})
        current_uid = self.env.uid

        def only_the_current_user_is_synced(event):
            return event.env.uid == current_uid

        with patch.object(
            type(self.event), "_check_microsoft_sync_status", only_the_current_user_is_synced,
        ), self.assertRaises(ValidationError) as caught:
            self.event._check_organizer_validation(other_user, True)
        self.assertNotRegex(str(caught.exception), BRAND_NAME)
        self.assertIn("Viindoo", str(caught.exception))

    def test_recurrence_update_error_names_viindoo(self):
        with self.assertRaises(UserError) as caught:
            self.event._forbid_recurrence_update()
        self.assertNotRegex(str(caught.exception), BRAND_NAME)
        self.assertIn("Viindoo", str(caught.exception))

    def test_attendee_without_email_error_names_viindoo(self):
        partner = self.env["res.partner"].create({"name": "No Email"})
        event = self.event
        event.partner_ids = [(6, 0, partner.ids)]
        event.attendee_ids.partner_id.email = False
        with self.assertRaises(ValidationError) as caught:
            event._ensure_attendees_have_email()
        self.assertNotRegex(str(caught.exception), BRAND_NAME)
        self.assertIn("Viindoo", str(caught.exception))
