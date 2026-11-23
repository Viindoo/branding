# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from lxml import html

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebclientBoot(HttpCase):
    """The first server render of the web client already carries what the shell paints from."""

    def _boot_page(self, cookies=None):
        self.authenticate("admin", "admin")
        for name, value in (cookies or {}).items():
            self.opener.cookies.set(name, value)
        return html.fromstring(self.url_open("/odoo").content)

    def test_density_comes_from_its_cookie_and_defaults_to_comfortable(self):
        self.assertEqual(self._boot_page().get("data-viin-density"), "comfortable")
        self.assertEqual(
            self._boot_page({"viin_density": "compact"}).get("data-viin-density"), "compact"
        )

    def test_the_density_does_not_replace_the_colour_scheme_stamp_of_the_brand(self):
        self.env.ref("base.user_admin").viin_color_scheme = "dark"
        page = self._boot_page()
        self.assertEqual(page.get("data-bs-theme"), "dark")
        self.assertTrue(page.get("data-viin-density"))

    def test_pages_other_than_the_web_client_carry_no_density(self):
        login = html.fromstring(self.url_open("/web/login").content)
        self.assertIsNone(login.get("data-viin-density"))

    def test_the_viewport_lets_the_user_zoom(self):
        content = self._boot_page().xpath("//meta[@name='viewport']/@content")[0]
        self.assertNotIn("user-scalable=no", content.replace(" ", ""))
