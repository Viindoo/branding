# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestMassMailingDebrand(TransactionCase):

    def test_portal_layout_title_is_viindoo(self):
        arch = self.env.ref("mass_mailing.layout")._get_combined_arch()

        self.assertEqual([title.text for title in arch.xpath("//title")], ["Viindoo"])

    def test_view_in_browser_fallback_page_is_titled_viindoo(self):
        title = self.env.ref("mass_mailing.mailing_view_generic")._get_combined_arch().xpath("//header/title")
        self.assertEqual([t.text for t in title], ["Viindoo"])

    def test_dedicated_mail_server_help_names_viindoo(self):
        helps = [
            self.env["mailing.mailing"].fields_get(["mail_server_id"])["mail_server_id"]["help"],
            self.env["res.config.settings"].fields_get(["mass_mailing_outgoing_mail_server"])[
                "mass_mailing_outgoing_mail_server"
            ]["help"],
        ]
        for text in helps:
            self.assertNotRegex(text, BRAND_NAME)
            self.assertIn("Viindoo", text)

    def test_dedicated_mail_server_setting_block_names_viindoo(self):
        arch = etree.fromstring(self.env["res.config.settings"].get_view(view_type="form")["arch"])
        blocks = arch.xpath("//setting[@name='dedicated_server_setting_container']")
        self.assertEqual(len(blocks), 1)
        self.assertNotRegex(blocks[0].get("title"), BRAND_NAME)
        self.assertIn("Viindoo", blocks[0].get("title"))

    def test_empty_states_of_the_mailing_lists_and_campaigns_name_viindoo(self):
        for xmlid in (
            "mass_mailing.action_view_mass_mailing_lists",
            "mass_mailing.action_view_mass_mailings_from_campaign",
            "mass_mailing.action_create_mass_mailings_from_campaign",
        ):
            help_text = self.env.ref(xmlid).with_context(lang="en_US").help
            self.assertNotRegex(help_text, BRAND_NAME, xmlid)
            self.assertIn("Viindoo", help_text, xmlid)
