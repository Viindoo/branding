from lxml import html

from odoo.tests.common import HttpCase, TransactionCase, new_test_user, tagged


def _invitation(root):
    """Return the text of the paragraph that invites the user to link a database."""
    return "".join(root.xpath("(//form//p[contains(@class, 'text-center')])[1]")[0].itertext())


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
        text = _invitation(html.fromstring(response.text))
        self.assertIn("Viindoo", text, "mail-plugin auth page must invite the user to link a Viindoo database")
        self.assertNotIn("Odoo", text, "mail-plugin auth page must not fall back to core's Odoo wording")


@tagged("-at_install", "post_install")
class AppAuthComposeInAnotherLanguageTest(TransactionCase):

    def test_auth_page_composes_in_a_language_that_translates_the_product_name(self):
        view = self.env.ref("mail_plugin.app_auth")
        self.env["res.lang"]._activate_lang("ar_001")
        translations, _context = view.get_field_translations("arch_db", ["ar_001"])
        sources = {t["source"] for t in translations if "Odoo" in t["source"]}
        self.assertTrue(sources)
        view.update_field_translations(
            "arch_db", {"ar_001": {source: source.replace("Odoo", "\u0623\u0648\u062f\u0648") for source in sources}},
        )

        arabic = _invitation(view.with_context(lang="ar_001")._get_combined_arch())
        english = _invitation(view.with_context(lang="en_US")._get_combined_arch())

        self.assertIn("Viindoo", arabic)
        self.assertNotIn("Odoo", arabic)
        self.assertEqual(arabic, english, "a language that only renames the product keeps the branded paragraph")
