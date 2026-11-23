# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from urllib.parse import urlparse

from lxml import etree

from odoo.tests.common import HttpCase, TransactionCase, tagged


PNG_PIXEL = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


@tagged("post_install", "-at_install")
class TestProductVideoDefaultName(HttpCase):

    def _create_product(self, name):
        """A product whose first extra media is an image: core refuses a video as the main image."""
        product = self.env["product.template"].create({"name": name})
        self.env["product.image"].create({
            "name": "Picture", "image_1920": PNG_PIXEL, "product_tmpl_id": product.id, "sequence": 0,
        })
        return product

    def _add_video(self, product, **media_values):
        self.authenticate("admin", "admin")
        self.make_jsonrpc_request("/shop/product/extra-media", {
            "media": [{"video_url": "https://www.youtube.com/watch?v=aqz-KE-bpKQ", **media_values}],
            "type": "video",
            "product_product_id": False,
            "product_template_id": product.id,
        })

    def test_product_video_without_a_name_gets_a_neutral_name(self):
        product = self._create_product("Video Product")

        self._add_video(product)

        videos = product.product_template_image_ids.filtered("video_url")
        self.assertEqual(videos.mapped("name"), [self.env._("Video")])

    def test_product_video_keeps_the_name_the_editor_sends(self):
        product = self._create_product("Named Video Product")

        self._add_video(product, name="Unboxing")

        videos = product.product_template_image_ids.filtered("video_url")
        self.assertEqual(videos.mapped("name"), ["Unboxing"])


@tagged("post_install", "-at_install")
class TestShopFooterPromotion(TransactionCase):

    def test_shop_footer_promotion_offers_the_viindoo_page_not_the_odoo_one(self):
        footer = str(self.env["ir.qweb"]._render("web.brand_promotion", {}))
        links = [urlparse(href) for href in etree.HTML(footer).xpath("//a/@href")]
        viindoo_paths = [link.path for link in links if link.netloc == "viindoo.com"]
        self.assertIn("/intro/ecommerce", viindoo_paths)
        self.assertNotIn("/app/ecommerce", [link.path for link in links])


@tagged("post_install", "-at_install")
class TestDeliverySettings(TransactionCase):

    def test_the_delivery_setting_offers_no_search_for_providers_in_the_apps_list(self):
        arch = etree.fromstring(self.env["res.config.settings"].get_view(view_type="form")["arch"])
        delivery_setting = arch.xpath("//setting[@id='website_delivery_setting']")
        self.assertEqual(len(delivery_setting), 1)
        self.assertEqual(delivery_setting[0].xpath(".//button[@name='action_install_more_provider']"), [])

    def test_the_delivery_setting_keeps_the_way_to_configure_the_methods(self):
        arch = etree.fromstring(self.env["res.config.settings"].get_view(view_type="form")["arch"])
        buttons = arch.xpath("//setting[@id='website_delivery_setting']//button[@type='action']")
        self.assertEqual(len(buttons), 1)
