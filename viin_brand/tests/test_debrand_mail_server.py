# Mail-server de-brand guard. Once viin_brand is installed, no Odoo wordmark may leak through
# user-facing field help. Core Odoo 19.0 ir.mail_server.from_filter help reads:
#     Comma-separated list of addresses or domains for which this server can be used.
#     e.g.: "notification@odoo.com" or "odoo.com"
# carrying the "odoo.com" wordmark twice; the module re-brands that help to Viindoo text. This
# asserts the observable help on the installed registry field, not a source literal.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class MailServerDebrandTest(TransactionCase):

    def test_from_filter_help_carries_no_odoo_wordmark(self):
        """ir.mail_server.from_filter help must not leak the Odoo wordmark once branding is installed.

        Core help contains "odoo.com" (and thus the bare "odoo" wordmark). The branded help uses
        Viindoo text; "viindoo" does not contain the substring "odoo" (v-i-i-n-d-o-o)."""
        help_text = self.env["ir.mail_server"]._fields["from_filter"].help or ""

        # The help must stay informative: blanking it would trivially pass the wordmark check.
        self.assertTrue(
            help_text.strip(),
            "ir.mail_server.from_filter must keep informative help text after de-branding",
        )

        lowered = help_text.lower()
        # No bare "odoo" wordmark anywhere in the help (this subsumes the "odoo.com" example).
        self.assertNotIn(
            "odoo", lowered,
            "ir.mail_server.from_filter help still carries the Odoo wordmark (%r). "
            "viin_brand must override this field's help with Viindoo-branded text "
            "(e.g. an example using \"viindoo.com\")." % help_text,
        )
