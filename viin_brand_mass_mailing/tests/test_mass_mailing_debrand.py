# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com|odoo-mobile")


@tagged("post_install", "-at_install")
class TestMassMailingDebrand(TransactionCase):

    def _arch(self, xmlid):
        return etree.tostring(self.env.ref(xmlid)._get_combined_arch(), encoding="unicode")

    def test_snippets_embed_no_odoo_image_nor_wording(self):
        """Images, their alternative text and the wording of the snippets name no Odoo."""
        for xmlid in ("mass_mailing.s_section_mobile", "mass_mailing.s_customer_quote", "mass_mailing.s_schedule"):
            arch = self.env.ref(xmlid)._get_combined_arch()
            shown = arch.xpath("//text()") + arch.xpath("//img/@src | //img/@data-original-src | //img/@alt")
            self.assertNotRegex(" ".join(shown), BRAND_NAME, xmlid)

    def test_app_advertising_block_shows_a_neutral_mobile_mockup(self):
        """The block is sample content of the customer's newsletter: it carries no product mark."""
        img = self.env.ref("mass_mailing.s_section_mobile")._get_combined_arch().xpath("//img")[0]
        self.assertEqual(img.get("src"), "/viin_brand_mass_mailing/static/src/img/mobile-app.png")
        self.assertEqual(img.get("alt"), "Mobile app")

    def test_app_advertising_store_links_are_placeholders_with_the_badges_kept(self):
        arch = self.env.ref("mass_mailing.s_section_mobile")._get_combined_arch()
        links = arch.xpath("//a[@target='_blank']")
        self.assertEqual([link.get("href") for link in links], ["#", "#"])
        self.assertEqual([link.xpath("string(.//img/@alt)") for link in links], ["Google Play Store", "App Store"])

    def test_schedule_snippet_lists_a_neutral_demo(self):
        arch = self._arch("mass_mailing.s_schedule")
        self.assertIn("Interactive demo", arch)
        self.assertNotIn("Viindoo", arch)

    def test_call_to_action_block_is_sample_copy_of_the_customer(self):
        arch = self.env.ref("mass_mailing.s_call_to_action")._get_combined_arch()
        text = " ".join(etree.tostring(arch, method="text", encoding="unicode").split())

        self.assertIn("Join the companies that grow their business with us.", text)
        self.assertNotIn("Viindoo", text)
        self.assertNotRegex(text, BRAND_NAME)

    def test_portal_layout_title_is_viindoo(self):
        arch = self.env.ref("mass_mailing.layout")._get_combined_arch()

        self.assertEqual([title.text for title in arch.xpath("//title")], ["Viindoo"])

    def test_view_in_browser_fallback_page_is_titled_viindoo(self):
        title = self.env.ref("mass_mailing.mailing_view_generic")._get_combined_arch().xpath("//header/title")
        self.assertEqual([t.text for t in title], ["Viindoo"])
