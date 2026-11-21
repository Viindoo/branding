# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestMarketingCardDebrand(TransactionCase):

    def test_shared_card_page_is_powered_by_viindoo(self):
        arch = self.env.ref("marketing_card.card_campaign_preview")._get_combined_arch()
        anchors = arch.xpath("//footer//a")
        self.assertEqual(len(anchors), 1)
        self.assertNotRegex(anchors[0].get("href"), BRAND_NAME)
        self.assertEqual(anchors[0].text, "Viindoo")

    def test_campaign_form_placeholders_are_neutral_examples(self):
        view = self.env["card.campaign"].get_view(
            view_id=self.env.ref("marketing_card.card_campaign_view_form").id, view_type="form",
        )
        arch = etree.fromstring(view["arch"].encode())
        for name in ("name", "content_header"):
            field = arch.xpath("//field[@name='%s']" % name)[0]
            self.assertNotRegex(field.get("placeholder"), BRAND_NAME, name)
            self.assertNotIn("Viindoo", field.get("placeholder"), name)
        self.assertEqual(arch.xpath("//field[@name='name']/@placeholder"), ["e.g. Annual Customer Talks"])
        self.assertEqual(
            arch.xpath("//field[@name='content_header']/@placeholder"), ["e.g. Join our Customer Day 2024"],
        )
