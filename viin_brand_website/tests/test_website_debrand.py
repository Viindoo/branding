# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re
from urllib.parse import parse_qs, urlparse

from lxml import etree, html

from odoo.tests.common import HttpCase, TransactionCase, tagged
from odoo.tools import file_open

from odoo.addons.viin_brand.tools import VIINDOO_SOCIAL_LINKS

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
        for xmlid in ("website.s_table_of_content", "website.s_form_aside"):
            source_text = _text(self.env.ref(xmlid).with_context(lang="en_US")._get_combined_arch())
            view = self._translate_product_name(self.env.ref(xmlid))
            text = _text(view._get_combined_arch())
            self.assertEqual(text, source_text, xmlid)
            self.assertNotRegex(text, BRAND_NAME, xmlid)

    def test_cta_mobile_snippet_is_sample_copy_of_the_customer(self):
        text = _text(self._combined_arch("website.s_cta_mobile"))
        self.assertNotRegex(text, BRAND_NAME)
        self.assertNotIn("trust Viindoo", text)

    def test_call_to_action_snippets_are_sample_copy_of_the_customer(self):
        for xmlid in (
            "website.s_call_to_action", "website.s_cta_box", "website.s_cta_card", "website.s_cta_mockups",
        ):
            text = _text(self._combined_arch(xmlid))
            self.assertNotIn("Viindoo", text, xmlid)
            self.assertNotRegex(text, BRAND_NAME, xmlid)

    def test_cta_centered_snippet_names_no_product(self):
        text = " ".join(self._combined_arch("website.s_cta_centered").itertext())
        self.assertNotRegex(text, BRAND_NAME)
        self.assertNotIn("Viindoo", text)

    def test_table_of_content_snippet_names_no_product(self):
        text = _text(self._combined_arch("website.s_table_of_content"))
        self.assertNotIn("Viindoo", text)
        self.assertNotRegex(text, BRAND_NAME)

    def test_footer_call_to_action_is_sample_copy_of_the_customer(self):
        footer = self.env.ref("website.template_footer_call_to_action")
        footer.active = True
        text = _text(self._combined_arch("website.layout"))
        self.assertNotIn("companies run Odoo", text)
        self.assertNotIn("companies run Viindoo", text)

    def test_social_block_previews_are_neutral_images_of_the_module(self):
        """The block picker and the drag ghost of the Instagram and Facebook blocks show a mockup."""
        snippets = self._combined_arch("website.snippets")
        for snippet, preview in (
            ("website.s_instagram_page", "/viin_brand_website/static/src/img/s_instagram_preview.webp"),
            ("website.s_facebook_page", "/viin_brand_website/static/src/img/s_facebook_preview.webp"),
        ):
            nodes = snippets.xpath("//t[@t-snippet='%s']" % snippet)
            previews = {
                node.get(attribute) for node in nodes
                for attribute in ("t-image-preview", "t-drag-image-preview") if node.get(attribute)
            }
            self.assertEqual(previews, {preview}, snippet)
            with file_open(preview.lstrip("/"), "rb") as image:
                self.assertEqual(image.read(4), b"RIFF", "the registered preview file exists and is a WebP image")

    def test_facebook_block_previews_the_viindoo_page(self):
        arch = self._combined_arch("website.s_facebook_page")
        iframe = arch.xpath("//iframe[hasclass('o_facebook_page_preview')]")[0]
        src = iframe.get("src")
        self.assertNotRegex(src, BRAND_NAME)
        page = parse_qs(urlparse(src).query)["href"][0]
        self.assertEqual(page, VIINDOO_SOCIAL_LINKS["social_facebook"])

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

    def test_digest_tips_name_no_product_and_load_no_image_from_the_cdn_of_odoo(self):
        tip_ids = self.env["ir.model.data"].search([
            ("module", "=", "website"), ("model", "=", "digest.tip"),
        ]).mapped("res_id")
        tips = self.env["digest.tip"].browse(tip_ids)
        self.assertTrue(tips, "the module website ships digest tips")
        for tip in tips:
            content = html.fragment_fromstring(tip.tip_description, create_parent="div")
            self.assertNotRegex(" ".join(content.text_content().split()), BRAND_NAME, tip.name)
            sources = content.xpath("//img/@src")
            self.assertTrue(sources, tip.name)
            for source in sources:
                self.assertTrue(source.startswith("/"), "%s loads %s from another host" % (tip.name, source))
                self.assertNotRegex(source, r"odoocdn|odoo\.com", tip.name)

    def test_seo_digest_tip_names_viindoo(self):
        tip = self.env.ref("website.digest_tip_website_2")
        text = " ".join(html.fragment_fromstring(tip.tip_description, create_parent="div").text_content().split())
        self.assertNotRegex(text, BRAND_NAME)
        self.assertIn("Viindoo", text)


@tagged("post_install", "-at_install")
class TestCookiePolicyPage(HttpCase):

    def test_cookie_policy_page_lists_the_cookies_as_viindoo_cookies(self):
        """The page every visitor reads once the cookies bar is on, anonymous."""
        self.env.ref("base.default_website").cookies_bar = True

        response = self.url_open("/cookie-policy")

        self.assertEqual(response.status_code, 200)
        text = " ".join(re.sub(r"<[^>]+>", " ", response.text).split())
        self.assertNotIn("(Odoo)", text)
        for cookie in ("session_id", "frontend_lang", "tz", "utm_campaign", "utm_source", "utm_medium"):
            self.assertIn("%s (Viindoo)" % cookie, text)
