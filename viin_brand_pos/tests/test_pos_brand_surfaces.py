# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open

from odoo.addons.point_of_sale.models.pos_config import PosConfig


@tagged("post_install", "-at_install")
class TestHeaderStyle(TransactionCase):

    def test_pos_stylesheet_leaves_the_header_background_to_core(self):
        bundle = self.env["ir.qweb"]._get_asset_bundle("point_of_sale._assets_pos", css=True, js=False)
        css = "".join((attachment.raw or b"").decode("utf-8", "replace") for attachment in bundle.css())
        self.assertTrue(css.strip())
        self.assertNotIn("pos-topheader", css, "the header keeps the background core gives it")


@tagged("post_install", "-at_install")
class TestClothesScenario(TransactionCase):

    def _sneakers(self, name="Odoo Sneakers"):
        with file_open("point_of_sale/static/img/product_odoo_sneakers.png", "rb") as image:
            core_image = base64.b64encode(image.read())
        product = self.env["product.product"].create({"name": name, "image_1920": core_image})
        self.env["ir.model.data"].create({
            "module": "point_of_sale",
            "name": "product_odoo_sneakers",
            "model": "product.product",
            "res_id": product.id,
        })
        return product, product.image_1920

    def test_loading_the_clothes_scenario_gives_the_sneakers_a_neutral_name_and_image(self):
        product, core_image = self._sneakers()
        config = self.env["pos.config"].create({"name": "Shop of the test"})
        with patch.object(PosConfig, "_load_onboarding_clothes_demo_data", return_value=None):
            config._load_onboarding_clothes_demo_data()
        self.assertEqual(product.name, "Sneakers")
        self.assertTrue(product.image_1920)
        self.assertNotEqual(product.image_1920, core_image)

    def test_installing_the_module_renames_sneakers_a_demo_database_already_holds(self):
        product, core_image = self._sneakers()
        self.env["pos.config"]._debrand_clothes_scenario()
        self.assertEqual(product.name, "Sneakers")
        self.assertNotEqual(product.image_1920, core_image)

    def test_sneakers_the_user_renamed_are_left_as_they_are(self):
        product, core_image = self._sneakers(name="My own sneakers")
        self.env["pos.config"]._debrand_clothes_scenario()
        self.assertEqual(product.name, "My own sneakers")
        self.assertEqual(product.image_1920, core_image)
