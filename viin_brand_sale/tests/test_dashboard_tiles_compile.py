# Compiled-CSS guard for the tiles above the Quotations list ("To Confirm", "To Deliver", "To Invoice"),
# which the website shop dashboard reuses. The component is sale's own (`sale.Dashboard`): a pale
# fill and a deep number per colour in light, and the same ramp rungs read by sale's dark stylesheet.
# The tiles are the only reader of Bootstrap's hue ramps in core, and the dark bundle has to flip
# those ramps (viin_brand dark_theme_tints.scss): otherwise the fill stays pale under the near-white
# label of the scheme.
import re

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BUNDLE,
    WCAG_AA_NORMAL_TEXT,
    _contrast_ratio,
)

TILE_COLOURS = ("purple", "orange", "cyan", "red")
# The label is the `.btn` text colour: the body tier of the scheme.
LIGHT_LABEL = "#212529"
DARK_LABEL = "#edf4f5"


@tagged("post_install", "-at_install")
class TestDashboardTilesCompile(TransactionCase):

    def _css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace")
            for attachment in (bundle.css() or self.env["ir.attachment"])
        )
        self.assertTrue(css.strip(), "%s compiled to empty CSS" % bundle_name)
        self.assertNotIn("css_error_message", css, "%s did not compile" % bundle_name)
        return css

    def _tile_fill(self, css, name, dark):
        """The fill a tile takes: the dark stylesheet sets the custom property on every tile, the
        light one leaves the fallback of the colour rule."""
        if dark:
            match = re.search(
                r"\.o_dashboard_card\s*\{[^}]*--DashboardCard__%s-bg-color:\s*(#[0-9a-fA-F]{6})" % name, css,
            )
        else:
            match = re.search(
                r"\.o_dashboard_card\.o_dashboard_card_%s\s*\{[^}]*--btn-bg:\s*var\([^,]+,\s*(#[0-9a-fA-F]{6})\)"
                % name, css,
            )
        self.assertTrue(match, "no tile fill compiled for %s (dark=%s)" % (name, dark))
        return match.group(1).lower()

    def _tile_number(self, css, name):
        match = re.search(
            r"\.o_dashboard_card\.o_dashboard_card_%s\s+\.o_dashboard_card_data\s*\{[^}]*color:\s*"
            r"var\([^,]+,\s*(#[0-9a-fA-F]{6})\)" % name, css,
        )
        self.assertTrue(match, "no tile number colour compiled for %s" % name)
        return match.group(1).lower()

    def test_tile_label_and_number_read_on_the_tile_fill_in_both_schemes(self):
        """In each scheme the label ("To Confirm") and the big number read on the tile fill at AA.

        Light: a pale fill under the dark body label and a deep number. Dark: a deep fill under the
        near-white body label and a pale number, which is the flipped hue ramp of the dark bundle.
        With the light ramp in dark the fill was pale under the near-white label, 1.1:1 to 1.7:1.
        """
        for arm, bundle_name, label in (
            ("light", BACKEND_BUNDLE, LIGHT_LABEL), ("dark", DARK_BUNDLE, DARK_LABEL),
        ):
            css = self._css(bundle_name)
            for name in TILE_COLOURS:
                with self.subTest(arm=arm, tile=name):
                    fill = self._tile_fill(css, name, arm == "dark")
                    number = self._tile_number(css, name)
                    self.assertGreaterEqual(
                        _contrast_ratio(label, fill), WCAG_AA_NORMAL_TEXT,
                        "The %s tile label %s on the %s fill %s is %.2f:1 in the %s scheme."
                        % (name, label, name, fill, _contrast_ratio(label, fill), arm),
                    )
                    self.assertGreaterEqual(
                        _contrast_ratio(number, fill), WCAG_AA_NORMAL_TEXT,
                        "The %s tile number %s on the fill %s is %.2f:1 in the %s scheme."
                        % (name, number, fill, _contrast_ratio(number, fill), arm),
                    )
