# Mail-server de-brand guard (ODOO-AI-ETHOS #8). Once viin_brand_base_setup is installed, no Odoo
# wordmark may leak through user-facing field help. Core Odoo 19.0 ir.mail_server.from_filter help
# (OSM-grounded, declared in base) reads:
#     Comma-separated list of addresses or domains for which this server can be used.
#     e.g.: "notification@odoo.com" or "odoo.com"
# carrying the "odoo.com" wordmark twice. The module must restore an ir.mail_server override that
# re-brands that field's help to Viindoo text. This asserts the OBSERVABLE help on the installed
# registry field, not a source literal - so it fails on current (unfixed) code and passes once the
# branded override lands.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class MailServerDebrandTest(TransactionCase):

    def test_from_filter_help_carries_no_odoo_wordmark(self):
        """ir.mail_server.from_filter help must not leak the Odoo wordmark once branding is installed.

        RED-carrier: core help contains "odoo.com" (and thus the bare "odoo" wordmark). The branded
        help must use Viindoo text - note "viindoo" does NOT contain the substring "odoo"
        (v-i-i-n-d-o-o), so a correctly branded help clears this check while core help fails it."""
        help_text = self.env["ir.mail_server"]._fields["from_filter"].help or ""

        # The help must remain informative after re-branding (do not silence the check by blanking
        # it). GREEN today; guards that the branded override keeps meaningful guidance.
        self.assertTrue(
            help_text.strip(),
            "ir.mail_server.from_filter must keep informative help text after de-branding",
        )

        lowered = help_text.lower()
        # RED-carrying assertion: no bare "odoo" wordmark anywhere in the help (this subsumes the
        # "odoo.com" example core ships).
        self.assertNotIn(
            "odoo", lowered,
            "ir.mail_server.from_filter help still carries the Odoo wordmark (%r). "
            "viin_brand_base_setup must override this field's help with Viindoo-branded text "
            "(e.g. an example using \"viindoo.com\")." % help_text,
        )
