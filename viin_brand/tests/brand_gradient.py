# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Not a test module: the shared check of the branding modules that repaint a gradient of core, which
# core builds from the Odoo purple written as a literal. Imported by the tests of those modules.
import colorsys
import re

from odoo.tests.common import TransactionCase

from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR

from .test_brand_cascade_compile import _COMMENT_RE, _winning_declaration

CORE_ODOO_PURPLE = "#875a7b"
FRONTEND_BUNDLE = "web.assets_frontend"
_GRADIENT_RE = re.compile(
    r"linear-gradient\(\s*(\d+)deg\s*,\s*(#[0-9a-fA-F]{6})\s*,\s*(#[0-9a-fA-F]{6})\s*\)"
)


def _hls(colour):
    channels = [int(colour[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    return colorsys.rgb_to_hls(*channels)


class BrandGradientCase(TransactionCase):
    """Base of the tests that read the gradient a stylesheet of the branding gives to a banner."""

    def assertBrandGradient(self, classes, ancestors, bundle=FRONTEND_BUNDLE):
        """Assert the banner of ``classes`` is painted with core's gradient in the content purple.

        The shape is core's: the same angle, and a second stop that is the first one darkened by 10%.

        :param classes: classes of the banner element
        :param ancestors: classes of the ancestors its rule is scoped to
        """
        asset_bundle = self.env["ir.qweb"]._get_asset_bundle(bundle, css=True, js=False)
        attachments = asset_bundle.css() or self.env["ir.attachment"]
        css = _COMMENT_RE.sub("", "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        ))
        element = {
            "classes": frozenset(classes), "ancestors": frozenset(ancestors), "prev_sibling": frozenset(),
        }
        value = _winning_declaration(css, element, ("background-image",))
        self.assertIsNotNone(value, "No compiled rule paints the banner %s." % sorted(classes))
        gradient = _GRADIENT_RE.match(value.strip())
        self.assertIsNotNone(gradient, "%r is not a two-stop linear-gradient of hex colours." % value)
        angle, first, second = gradient.groups()
        self.assertEqual(angle, "120")
        self.assertEqual(first.lower(), VIINDOO_BRAND_COLOR.lower())
        self.assertNotIn(CORE_ODOO_PURPLE, value.lower())
        hue, lightness, saturation = _hls(first)
        second_hue, second_lightness, second_saturation = _hls(second)
        self.assertAlmostEqual(second_lightness, lightness - 0.10, delta=0.01)
        self.assertAlmostEqual(second_hue, hue, delta=0.01)
        self.assertAlmostEqual(second_saturation, saturation, delta=0.02)
