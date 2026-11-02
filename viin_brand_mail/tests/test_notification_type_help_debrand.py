# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNotificationTypeHelpDebrand(TransactionCase):
    """The help of ``res.users.notification_type`` names Viindoo, not Odoo."""

    def test_notification_type_help_is_debranded(self):
        field_info = self.env["res.users"].fields_get(["notification_type"])
        help_text = field_info["notification_type"]["help"]
        self.assertIn(
            "Viindoo",
            help_text,
            "notification_type help must mention Viindoo",
        )
        self.assertNotIn(
            "Odoo",
            help_text,
            "notification_type help must not keep the core 'Odoo' wording",
        )
