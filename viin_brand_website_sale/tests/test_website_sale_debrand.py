# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re
from unittest.mock import patch

from odoo.tests.common import HttpCase, TransactionCase, tagged

BRAND_NAME = re.compile(r"\bOdoo\b|odoo\.com", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestWebsiteSaleMegaMenuName(TransactionCase):

    def test_ecommerce_mega_menu_snippet_is_not_called_after_odoo(self):
        self.assertNotRegex(self.env.ref("website_sale.s_mega_menu_odoo_menu").name, BRAND_NAME)


@tagged("post_install", "-at_install")
class TestProductVideoDefaultName(HttpCase):

    def test_product_video_without_a_name_gets_a_neutral_name(self):
        product = self.env["product.template"].create({"name": "Video Product"})
        self.authenticate("admin", "admin")

        with patch("odoo.addons.website_sale.controllers.main.get_video_thumbnail", return_value=b""):
            self.make_jsonrpc_request("/shop/product/extra-media", {
                "media": [{"src": "https://www.youtube.com/watch?v=aqz-KE-bpKQ"}],
                "type": "video",
                "product_product_id": False,
                "product_template_id": product.id,
            })

        names = product.product_template_image_ids.mapped("name")
        self.assertEqual(names, ["Video"])

    def test_product_video_keeps_the_name_the_editor_sends(self):
        product = self.env["product.template"].create({"name": "Named Video Product"})
        self.authenticate("admin", "admin")

        with patch("odoo.addons.website_sale.controllers.main.get_video_thumbnail", return_value=b""):
            self.make_jsonrpc_request("/shop/product/extra-media", {
                "media": [{"src": "https://www.youtube.com/watch?v=aqz-KE-bpKQ", "name": "Unboxing"}],
                "type": "video",
                "product_product_id": False,
                "product_template_id": product.id,
            })

        self.assertEqual(product.product_template_image_ids.mapped("name"), ["Unboxing"])
