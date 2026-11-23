# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# What the editor adds to the compiled bundles: the `--black` it declares on :root keeps its meaning
# in the dark scheme, and the colour of the content palette the editor seeds is the brand purple.
# The tests resolve the values from the compiled bundles, as a browser would.
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    BACKGROUND_PROPS,
    DARK_BUNDLE,
    _computed_value,
    _normalize_colour,
)
from odoo.addons.viin_brand.tests.test_dark_gray_ramp_compile import _root_value

BACKEND_BUNDLE = "web.assets_backend"
BRAND_PURPLE = "#7f4282"
CORE_CONTENT_O_COLOR_1 = "#714b67"
ODOO_COMMUNITY_PURPLE = "#71639e"


@tagged("post_install", "-at_install")
class TestEditorBrandScheme(TransactionCase):

    def _css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in (bundle.css() or [])
        )
        self.assertTrue(css.strip(), "%s compiled to empty CSS" % bundle_name)
        return css

    def test_black_keeps_its_light_scheme_meaning_in_dark(self):
        """`$black` stays real black, which `color-contrast()` reads to pick the label of a fill.

        Only `html_editor` declares `:root --black`; without it the property does not exist.
        """
        value = _root_value(self._css(DARK_BUNDLE), "black")

        self.assertIsNotNone(value, "the dark bundle declares no :root --black")
        self.assertEqual(_normalize_colour(value), "#000000")

    def test_content_palette_o_color_1_is_the_brand_purple(self):
        """The editor content swatch o-color-1 renders the brand purple, not core aubergine.

        The editor seeds the content palette (base-1 o-color-1) from the colour variable the chrome
        reads, so the swatch is the Viindoo purple without a reset. The observable is
        `.bg-o-color-1`, which the editor generates from the o-color-1 entry of the active palette.
        """
        swatch = {
            "classes": frozenset({"bg-o-color-1"}),
            "ancestors": frozenset(),
            "prev_sibling": frozenset(),
        }

        value = _computed_value(self._css(BACKEND_BUNDLE), [swatch], BACKGROUND_PROPS)

        self.assertIsNotNone(value, "no compiled declaration paints the content swatch .bg-o-color-1")
        colour = _normalize_colour(value)
        self.assertEqual(colour, BRAND_PURPLE)
        self.assertNotIn(colour, (CORE_CONTENT_O_COLOR_1, ODOO_COMMUNITY_PURPLE))
