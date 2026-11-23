# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Core's colour tests of the editor read the content palette from the unit-test bundle
# (web.assets_unit_tests_setup) and compare it with core's own colour. That bundle is compiled from
# core's seed of the palette, while the bundles users load keep the brand's. The tests read the
# compiled bundles, as a browser would; that the bundles users load keep the brand's colour is
# test_brand_scheme.test_content_palette_o_color_1_is_the_brand_purple.
import re

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_path

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    BACKGROUND_PROPS,
    _computed_value,
    _normalize_colour,
)

UNIT_SETUP_BUNDLE = "web.assets_unit_tests_setup"
CORE_CONTENT_O_COLOR_1 = "#714b67"
PIN_SCSS = "viin_brand_html_editor/static/tests/scss/core_palette_pin.scss"
CORE_PRIMARY_VARIABLES = "web/static/src/scss/primary_variables.scss"
SEED_RE = re.compile(r"^\$o-enterprise-color:\s*(#[0-9A-Fa-f]{6})\b", re.MULTILINE)


def _swatch(css_class):
    return {"classes": frozenset({css_class}), "ancestors": frozenset(), "prev_sibling": frozenset()}


@tagged("post_install", "-at_install")
class TestCorePalettePin(TransactionCase):

    def _css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in (bundle.css() or [])
        )
        self.assertTrue(css.strip(), "%s compiled to empty CSS" % bundle_name)
        return css

    def _background(self, bundle_name, css_class):
        value = _computed_value(self._css(bundle_name), [_swatch(css_class)], BACKGROUND_PROPS)
        self.assertIsNotNone(value, "%s paints no .%s" % (bundle_name, css_class))
        return _normalize_colour(value)

    def test_unit_test_bundle_compiles_the_content_palette_from_core_seed(self):
        """The editor content swatch of the unit-test bundle is core's colour, so core's tests measure core."""
        self.assertEqual(self._background(UNIT_SETUP_BUNDLE, "bg-o-color-1"), CORE_CONTENT_O_COLOR_1)

    def test_pin_is_the_seed_core_ships(self):
        """A core update that changes the seed fails here, instead of leaving the pin on a stale colour."""
        with open(file_path(CORE_PRIMARY_VARIABLES), encoding="utf-8") as core, \
                open(file_path(PIN_SCSS), encoding="utf-8") as pin:
            core_seed = SEED_RE.search(core.read())
            pinned = SEED_RE.search(pin.read())

        self.assertTrue(core_seed, "core does not declare $o-enterprise-color in %s" % CORE_PRIMARY_VARIABLES)
        self.assertTrue(pinned, "%s does not pin $o-enterprise-color" % PIN_SCSS)
        self.assertEqual(pinned.group(1).lower(), core_seed.group(1).lower())
