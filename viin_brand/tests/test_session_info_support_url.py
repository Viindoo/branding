import re

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSessionInfoSupportUrl(HttpCase):

    def test_support_url_points_to_viindoo_pricing(self):
        """The session info of an internal user carries the Viindoo pricing page as support url."""
        self.authenticate("admin", "admin")
        body = self.url_open("/odoo").text
        match = re.search(r'"support_url"\s*:\s*"([^"]+)"', body)
        self.assertTrue(match, "the web client bootstrap must embed the session info")
        self.assertEqual(match.group(1), "https://viindoo.com/pricing")
