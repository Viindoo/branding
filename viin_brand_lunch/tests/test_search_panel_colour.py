# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""The section icons of the search panel of the lunch products follow the branding palette.

``viin_brand_lunch_search_panel_colour_<scheme>`` (static/tests/tours/search_panel_colour_tour.js)
opens each screen that shows the panel and reads the computed colour of its icons.
"""
from odoo.tests import HttpCase, tagged

SCREENS = ("lunch.lunch_product_action_order", "lunch.lunch_product_action")


@tagged("post_install", "-at_install")
class TestSearchPanelColour(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = cls.env.ref("base.user_admin")
        cls.admin.group_ids |= cls.env.ref("lunch.group_lunch_manager")
        supplier = cls.env["lunch.supplier"].create({
            "partner_id": cls.env["res.partner"].create({"name": "Colour Diner"}).id,
            "send_by": "mail",
        })
        category = cls.env["lunch.product.category"].create({"name": "Colour Snacks"})
        cls.env["lunch.product"].create({
            "name": "Colour Sandwich",
            "category_id": category.id,
            "supplier_id": supplier.id,
            "price": 3.0,
        })

    def _open_every_screen(self, scheme):
        self.admin.viin_color_scheme = scheme
        for action in SCREENS:
            with self.subTest(scheme=scheme, action=action):
                self.start_tour(
                    f"/odoo/action-{action}",
                    f"viin_brand_lunch_search_panel_colour_{scheme}",
                    login="admin",
                )

    def test_the_section_icons_follow_the_palette_in_the_light_scheme(self):
        self._open_every_screen("light")

    def test_the_section_icons_follow_the_palette_in_the_dark_scheme(self):
        self._open_every_screen("dark")
