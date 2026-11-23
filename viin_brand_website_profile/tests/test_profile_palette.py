# Part of Viindoo. See LICENSE file for full copyright and licensing details.
import re

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import _iter_rules, _normalize_colour

FRONTEND_BUNDLE = "web.assets_frontend"
BRAND_PURPLE = "#7f4282"
ODOO_PURPLES = ("#875a7b", "#78516f", "#714b67")
HEADER_SELECTOR = ".o_wprofile_body .o_wprofile_gradient"
PICTURE_SELECTOR = ".o_wprofile_body .o_wprofile_gradient .o_wprofile_pict"


def _shade(colour, ratio):
    """The colour mixed with black, as the stylesheet derives its darker rung of the brand purple."""
    red, green, blue = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(round(channel * (1 - ratio)) for channel in (red, green, blue))


@tagged("post_install", "-at_install")
class TestProfilePalette(TransactionCase):
    """The profile page of a member takes the brand colours, read from the compiled frontend bundle."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        bundle = cls.env["ir.qweb"]._get_asset_bundle(FRONTEND_BUNDLE, css=True, js=False)
        cls.css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in (bundle.css() or [])
        )

    def _bodies(self, selector):
        return [body for _order, rule_selector, body in _iter_rules(self.css) if rule_selector == selector]

    def test_the_header_gradient_runs_between_two_rungs_of_the_brand_purple(self):
        gradients = [
            declaration for body in self._bodies(HEADER_SELECTOR)
            for declaration in re.findall(r"background-image\s*:\s*([^;}]+)", body)
        ]

        self.assertTrue(gradients, "the header of a profile carries a gradient")
        colours = [_normalize_colour(token) for token in re.findall(r"#[0-9a-fA-F]{6}\b", gradients[-1])]
        self.assertIn(BRAND_PURPLE, colours)
        self.assertFalse(set(colours) & set(ODOO_PURPLES), colours)

    def test_the_picture_border_is_a_darker_rung_of_the_brand_purple(self):
        borders = [
            _normalize_colour(match)
            for body in self._bodies(PICTURE_SELECTOR)
            for match in re.findall(r"border-color\s*:\s*(#[0-9a-fA-F]{6})", body)
        ]

        self.assertEqual(borders[-1:], [_shade(BRAND_PURPLE, 0.10)])
