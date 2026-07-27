# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNotificationTypeHelpDebrand(TransactionCase):
    """The ``res.users.notification_type`` field help must be Viindoo-branded,
    not Odoo.

    Core (``mail.models.res_users``) defines the field help as:
        "Policy on how to handle Chatter notifications:
        - By Emails: notifications are sent to your email address
        - In Odoo: notifications appear in your Odoo Inbox"

    ``viin_brand_mail`` already overrides the selection LABEL for the
    ``inbox`` option ("Handle in Viindoo"), but left this HELP text
    untouched - so the live Preferences UI kept showing "...In Odoo:
    ...your Odoo Inbox" even after installing this de-branding module. This
    test protects the field's HELP metadata directly (``fields_get``), not
    the rendered form view, so it fails against the un-overridden core help
    and passes once the help itself is de-branded.
    """

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
