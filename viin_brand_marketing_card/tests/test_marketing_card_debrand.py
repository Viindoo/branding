# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import io
import re

from lxml import etree
from PIL import Image

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestMarketingCardDebrand(TransactionCase):

    def test_shared_card_page_is_powered_by_viindoo(self):
        arch = self.env.ref("marketing_card.card_campaign_preview")._get_combined_arch()
        anchors = arch.xpath("//footer//a")
        self.assertEqual(len(anchors), 1)
        self.assertNotRegex(anchors[0].get("href"), BRAND_NAME)
        self.assertEqual(anchors[0].text, "Viindoo")

    def test_shared_card_page_link_uses_the_viindoo_colour(self):
        arch = self.env.ref("marketing_card.card_campaign_preview")._get_combined_arch()
        style = arch.xpath("//footer//a")[0].get("style")
        self.assertEqual(style.replace(" ", "").rstrip(";").lower(), "color:#7f4282")

    def test_the_app_icon_is_a_viindoo_icon_of_the_size_of_the_core_one(self):
        """The icon is read by the brand of the cluster from the module of the app, at this path."""
        with file_open("viin_brand_marketing_card/static/description/icon.png", "rb") as icon_file:
            icon_bytes = icon_file.read()
        with file_open("marketing_card/static/description/icon.png", "rb") as core_icon_file:
            core_icon_bytes = core_icon_file.read()
        icon = Image.open(io.BytesIO(icon_bytes))
        self.assertEqual(icon.format, "PNG")
        self.assertEqual(icon.size, Image.open(io.BytesIO(core_icon_bytes)).size)
        self.assertNotEqual(icon_bytes, core_icon_bytes)

    def test_campaign_form_placeholders_are_neutral_examples(self):
        view = self.env["card.campaign"].get_view(
            view_id=self.env.ref("marketing_card.card_campaign_view_form").id, view_type="form",
        )
        arch = etree.fromstring(view["arch"].encode())
        for name in ("name", "content_header"):
            field = arch.xpath("//field[@name='%s']" % name)[0]
            self.assertNotRegex(field.get("placeholder"), BRAND_NAME, name)
            self.assertNotIn("Viindoo", field.get("placeholder"), name)
