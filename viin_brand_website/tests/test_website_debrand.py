# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import ast
import re

from lxml import etree, html

from odoo.tests.common import HttpCase, TransactionCase, tagged
from odoo.tools import file_open
from odoo.tools import convert_file

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


def _text(arch):
    return " ".join(etree.tostring(arch, method="text", encoding="unicode").split())


@tagged("post_install", "-at_install")
class TestWebsiteDebrand(TransactionCase):

    def _combined_arch(self, xmlid):
        return self.env.ref(xmlid)._get_combined_arch()

    def _translate_product_name(self, view, lang="ar_001", marker="Odoo", renamed="\u0623\u0648\u062f\u0648"):
        """Give the terms of the view that name the product a translation that no longer carries it."""
        self.env["res.lang"]._activate_lang(lang)
        translations, _context = view.get_field_translations("arch_db", [lang])
        sources = {t["source"] for t in translations if marker in t["source"]}
        self.assertTrue(sources, "the view must have a term that names the product")
        view.update_field_translations(
            "arch_db", {lang: {source: source.replace(marker, renamed) for source in sources}},
        )
        return view.with_context(lang=lang)

    def test_snippets_compose_in_a_language_that_translates_the_product_name(self):
        """The anchors do not depend on the text that translators change."""
        for xmlid, expected in (
            ("website.s_table_of_content", "Design templates easily"),
            ("website.s_form_aside", "our apps, services, and company"),
        ):
            view = self._translate_product_name(self.env.ref(xmlid))
            text = _text(view._get_combined_arch())
            self.assertIn(expected, text, xmlid)

    def test_cta_mobile_snippet_is_sample_copy_of_the_customer(self):
        text = _text(self._combined_arch("website.s_cta_mobile"))
        self.assertNotRegex(text, BRAND_NAME)
        self.assertIn("Trusted by companies like yours.", text)
        self.assertNotIn("trust Viindoo", text)

    def test_call_to_action_snippets_are_sample_copy_of_the_customer(self):
        expected = {
            "website.s_call_to_action": "Join the companies that grow their business with us.",
            "website.s_cta_box": "Join the companies that grow their business with us.",
            "website.s_cta_card": "Join the companies that grow their business with us.",
            "website.s_cta_mockups": "Trusted by companies like yours.",
        }
        for xmlid, sentence in expected.items():
            text = _text(self._combined_arch(xmlid))
            self.assertIn(sentence, text, xmlid)
            self.assertNotIn("Viindoo", text, xmlid)
            self.assertNotRegex(text, BRAND_NAME, xmlid)

    def test_table_of_content_snippet_names_no_product(self):
        text = _text(self._combined_arch("website.s_table_of_content"))
        self.assertIn("Design templates easily", text)
        self.assertNotIn("Viindoo", text)
        self.assertNotRegex(text, BRAND_NAME)

    def test_footer_call_to_action_is_sample_copy_of_the_customer(self):
        footer = self.env.ref("website.template_footer_call_to_action")
        footer.active = True
        text = _text(self._combined_arch("website.layout"))
        self.assertNotIn("companies run Odoo", text)
        self.assertIn("Join the companies that grow their business with us.", text)
        self.assertNotIn("companies run Viindoo", text)

    def test_instagram_block_preview_is_a_neutral_image_of_the_module(self):
        snippet = self._combined_arch("website.snippets").xpath("//t[@t-snippet='website.s_instagram_page']")[0]
        preview = snippet.get("t-image-preview")
        self.assertEqual(preview, "/viin_brand_website/static/src/img/s_instagram_preview.webp")
        with file_open(preview.lstrip("/"), "rb") as image:
            self.assertEqual(image.read(4), b"RIFF", "the registered preview file exists and is a WebP image")

    def test_instagram_snippet_defaults_to_the_viindoo_account_and_stays_a_default(self):
        section = self._combined_arch("website.s_instagram_page").xpath("//section")[0]
        self.assertEqual(section.get("data-instagram-page"), "officialviindoo")
        self.assertEqual(
            section.get("data-instagram-page-is-default"), "true",
            "a website with an Instagram account of its own must still win over the default",
        )

    def test_mega_menu_snippets_are_not_called_after_odoo(self):
        for xmlid in ("website.s_mega_menu_odoo_menu",):
            self.assertNotRegex(self.env.ref(xmlid).name, BRAND_NAME)

    def test_form_aside_snippet_is_sample_copy_of_the_customer(self):
        text = _text(self._combined_arch("website.s_form_aside"))
        self.assertNotRegex(text, BRAND_NAME)
        self.assertNotIn("Viindoo", text)
        self.assertIn("our apps, services, and company", text)

    def test_seo_digest_tip_names_viindoo_not_the_system(self):
        tip = self.env.ref("website.digest_tip_website_2")
        text = " ".join(html.fragment_fromstring(tip.tip_description, create_parent="div").text_content().split())
        self.assertNotRegex(text, BRAND_NAME)
        self.assertNotIn("the system", text)
        self.assertIn("Viindoo will recommend", text)

    def test_resource_editor_warning_names_viindoo_not_the_system(self):
        with file_open("viin_brand_website/static/src/components/resource_editor/resource_editor_warning.xml") as f:
            source = f.read()
        self.assertNotIn("system upgrade", source)
        self.assertIn("Viindoo upgrade", source)

    def test_robots_setting_keeps_the_help_of_core(self):
        view = self.env["res.config.settings"].get_view(
            view_id=self.env.ref("website.res_config_settings_view_form").id, view_type="form",
        )
        settings = etree.fromstring(view["arch"].encode()).xpath("//setting[@id='robots_setting']")
        self.assertEqual(len(settings), 1)
        self.assertNotIn(
            "Sitemap", settings[0].get("help") or "",
            "the Robots.txt setting must not describe sitemap.xml",
        )


@tagged("post_install", "-at_install")
class TestCookiePolicyPage(HttpCase):

    def test_cookie_policy_page_lists_the_cookies_as_viindoo_cookies(self):
        """The page every visitor reads once the cookies bar is on, anonymous."""
        self.env.ref("website.default_website").cookies_bar = True

        response = self.url_open("/cookie-policy")

        self.assertEqual(response.status_code, 200)
        text = " ".join(re.sub(r"<[^>]+>", " ", response.text).split())
        self.assertNotIn("(Odoo)", text)
        for cookie in ("session_id", "frontend_lang", "utm_campaign", "utm_source", "utm_medium"):
            self.assertIn("%s (Viindoo)" % cookie, text)


@tagged("post_install", "-at_install")
class TestWebsiteAppsAreFreeOfEnterpriseModules(TransactionCase):

    def test_website_apps_action_hides_enterprise_module_stubs_after_its_data_is_reloaded(self):
        action = self.env.ref("website.action_website_add_features")
        action.domain = "['!', ('name', '=like', 'theme_%')]"

        convert_file(self.env, "viin_brand_website", "data/ir_module_module_data.xml", None, mode="init")

        self.assertIn("to_buy", action.domain)
        stub = self.env["ir.module.module"].create(
            {"name": "enterprise_stub_website_apps", "to_buy": True, "state": "uninstallable"},
        )
        self.assertFalse(self.env["ir.module.module"].search(
            [("id", "=", stub.id)] + ast.literal_eval(action.domain)),
        )
