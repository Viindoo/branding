# Part of Odoo. See LICENSE file for full copyright and licensing details.
from lxml import html

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMailGatewayAllowedHelp(TransactionCase):
    """The Allowed List screen of the mail gateway opens and its empty help names the loop limits."""

    def _help(self):
        action = self.env.ref("mail.mail_gateway_allowed_action")
        # the window action builds its help through the model, which `read` does for a full read only
        return action.read()[0]["help"]

    def _help_text(self):
        return html.fromstring(str(self._help())).text_content()

    def assertShows(self, text, number):
        self.assertRegex(text, r"(?<!\d)%d(?!\d)" % number)

    def test_the_empty_help_shows_the_configured_loop_limits(self):
        params = self.env["ir.config_parameter"]
        params.set_int("mail.gateway.loop.minutes", 37)
        params.set_int("mail.gateway.loop.threshold", 11)
        help_text = self._help_text()
        self.assertShows(help_text, 11)
        self.assertShows(help_text, 37)

    def test_the_empty_help_shows_the_default_loop_limits_when_none_is_configured(self):
        params = self.env["ir.config_parameter"]
        params.set_int("mail.gateway.loop.minutes", None)
        params.set_int("mail.gateway.loop.threshold", None)
        help_text = self._help_text()
        self.assertShows(help_text, 20)
        self.assertShows(help_text, 120)

    def test_the_empty_help_names_viindoo(self):
        help_message = self._help()
        self.assertIn("Viindoo", help_message)
        self.assertNotIn("Odoo", help_message)
