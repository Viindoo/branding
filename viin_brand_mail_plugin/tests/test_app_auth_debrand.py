from odoo.tests.common import HttpCase, new_test_user, tagged


@tagged("-at_install", "post_install")
class AppAuthDebrandTest(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # auth="user" + internal-only: an internal user with no dependency on demo data.
        cls.internal_user = new_test_user(cls.env, login="mail_plugin_auth_internal_user")

    def test_auth_page_offers_viindoo_database_not_odoo(self):
        self.authenticate("mail_plugin_auth_internal_user", "mail_plugin_auth_internal_user")
        response = self.url_open("/mail_plugin/auth", params={"friendlyname": "Test Add-in"})
        self.assertEqual(
            response.status_code, 200,
            "auth page must render for an authenticated internal user",
        )
        body = response.text
        self.assertIn(
            "access your Viindoo database", body,
            "mail-plugin auth page must invite the user to link a Viindoo database",
        )
        self.assertNotIn(
            "access your Odoo database", body,
            "mail-plugin auth page must not fall back to core's Odoo wording",
        )
