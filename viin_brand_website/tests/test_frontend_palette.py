# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# The frontend primary of a website is the Viindoo purple until the editor of the website picks a
# palette of its own: then the palette of the website wins. The compiled web.assets_frontend of the
# website is read, as the page of a visitor loads it.
import re

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import _iter_rules, _normalize_colour
from odoo.addons.viin_brand.tests.test_brand_ssot import BRAND_VARIABLES_SCSS, _resolve_scss_hex

FRONTEND_BUNDLE = "web.assets_frontend"
BRAND_PURPLE = "#7f4282"
CUSTOM_PRIMARY = "#4a6a90"
WHITE = "#ffffff"
USER_PALETTE_SCSS = "/website/static/src/scss/options/colors/user_color_palette.scss"


@tagged("post_install", "-at_install")
class TestWebsiteFrontendPalette(TransactionCase):

    def _frontend_css(self, website):
        """web.assets_frontend as ``website`` serves it, its own customized files included."""
        bundle = self.env["ir.qweb"].with_context(website_id=website.id)._get_asset_bundle(
            FRONTEND_BUNDLE, css=True, js=False
        )
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace")
            for attachment in (bundle.css() or self.env["ir.attachment"])
        )
        self.assertTrue(css.strip(), "web.assets_frontend of website %s compiled to empty CSS" % website.id)
        return css

    def _rule_prop(self, css, selector, prop):
        """The last value of the custom property ``--<prop>`` declared on ``selector`` rules."""
        pattern = re.compile(r"--%s\s*:\s*([^;}]+)" % re.escape(prop))
        values = [
            match.group(1).strip().lower()
            for _order, rule_selector, body in _iter_rules(css) if rule_selector == selector
            for match in pattern.finditer(body)
        ]
        return _normalize_colour(values[-1]) if values else None

    def test_a_website_with_the_stock_palette_renders_the_viindoo_purple_as_primary(self):
        website = self.env["website"].search([], order="id", limit=1)

        css = self._frontend_css(website)

        self.assertEqual(self._rule_prop(css, ":root", "primary"), BRAND_PURPLE)

    def test_a_website_whose_editor_picked_a_palette_keeps_the_primary_of_that_palette(self):
        """A customised o-color-1 keeps driving the buttons, the links and the primary blocks.

        A secondary button that set its colour but no border keeps the default border of its own
        colour, not the border of the stock palette."""
        website = self.env["website"].search([], order="id", limit=1)

        self.env["website.assets"].with_context(website_id=website.id).make_scss_customization(
            USER_PALETTE_SCSS,
            {"o-color-1": CUSTOM_PRIMARY.upper(), "o-color-5": WHITE.upper(), "o-cc1-btn-secondary": "'o-color-5'"},
        )
        css = self._frontend_css(website)

        self.assertEqual(self._rule_prop(css, ":root", "primary"), CUSTOM_PRIMARY)
        self.assertEqual(self._rule_prop(css, ".btn-secondary", "btn-border-color"), WHITE)

    def test_the_frontend_palette_and_the_dark_text_of_the_tabs_are_the_brand_colours(self):
        """The website builder tests of core expect core's colours here; the site of a visitor is branded.

        The first colour of the stock palette is the brand purple, and the label colour core picks
        on a light fill (the links of the tabs) is the brand's dark text, not core's gray-900."""
        website = self.env["website"].search([], order="id", limit=1)

        css = self._frontend_css(website)
        with open(BRAND_VARIABLES_SCSS, encoding="utf-8") as scss_file:
            contrast_dark = _resolve_scss_hex(scss_file.read(), "$color-contrast-dark").lower()

        self.assertEqual(self._rule_prop(css, ":root", "o-color-1"), BRAND_PURPLE)
        self.assertRegex(css.lower(), r"var\(--tabs-link-color,\s*%s\)" % contrast_dark)
