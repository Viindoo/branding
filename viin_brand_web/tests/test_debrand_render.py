# De-brand render smoke (DESIGN 4c / 9): once the module is installable, the login page's
# "Powered by" promotion is de-branded to Viindoo via the web.login_layout / brand_promotion_message
# QWeb xpaths. This guards that those de-brand views load (no ParseError) AND actually re-brand the
# server-rendered page.
from odoo.tests.common import HttpCase, tagged


@tagged("-at_install", "post_install")
class DebrandRenderTest(HttpCase):

    def test_login_page_is_debranded_powered_by_viindoo(self):
        """The login page 'Powered by' promotion is de-branded to Viindoo (server-side QWeb)."""
        response = self.url_open("/web/login")
        self.assertEqual(
            response.status_code, 200,
            "login page must render (no ParseError from the de-brand xpath targets)",
        )
        body = response.text
        self.assertIn("Powered by", body, "login page must still show the 'Powered by' promotion")
        self.assertIn(
            "Viindoo", body,
            "login 'Powered by' promotion must be de-branded to Viindoo (server-rendered), not Odoo",
        )
