# De-brand render smoke: the login page's "Powered by" promotion is de-branded to Viindoo via the
# web.login_layout / brand_promotion_message QWeb xpaths. This guards that those views load (no
# ParseError) AND re-brand the server-rendered page.
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
        self.assertIn("viindoo.com?utm_source=db", body, "the promotion must still be on the page")
        self.assertNotIn("odoo.com?utm_source=db", body, "the promotion must not link to Odoo")
        self.assertIn(
            "Viindoo", body,
            "login 'Powered by' promotion must be de-branded to Viindoo (server-rendered), not Odoo",
        )
