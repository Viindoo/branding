import os
import re

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
    ACTION_DEEP,
    BRAND_PURPLE,
    CHROME_BASE,
    CHROME_DEEP,
    DARK_BUNDLE,
    WCAG_AA_NORMAL_TEXT,
    _composite_over,
    _contrast_ratio,
    _normalize_colour,
    _winning_declaration,
)
from .test_theme_dark_widgets import (
    BACKEND_BUNDLE,
    HOME_MENU_ROOT_ANCESTORS,
    HOME_MENU_ROOT_CLASSES,
    HOME_SECTION_LABEL_ANCESTORS,
    HOME_SECTION_LABEL_CLASSES,
    _resolve_to_hex,
)

# An app tile and its label, from home_menu.xml: `.o_viin_home_grid` > `a.o_app.o_viin_home_app`
# > `span.o_viin_home_app_name`. The cascade resolver keys on classes.
HOME_TILE_CLASSES = frozenset({"o_app", "o_viin_home_app", "d-flex", "flex-column", "align-items-center"})
HOME_TILE_ANCESTORS = HOME_SECTION_LABEL_ANCESTORS | {"o_viin_home_grid"}
HOME_TILE_LABEL_CLASSES = frozenset({"o_viin_home_app_name"})
HOME_TILE_LABEL_ANCESTORS = HOME_TILE_ANCESTORS | HOME_TILE_CLASSES

# One translucent backdrop layer as the compiled bundle spells it, e.g.
# `color-mix(in srgb, #00BBCE 7%, transparent)`. Mixing toward `transparent` makes it an alpha layer
# over the page band.
_COLOR_MIX_LAYER_RE = re.compile(
    r"color-mix\(\s*in\s+srgb\s*,\s*(#[0-9A-Fa-f]{3,8})\s+([\d.]+)%\s*,\s*transparent\s*\)",
    re.IGNORECASE,
)


@tagged("post_install", "-at_install")
class TestHomeMenuBackground(TransactionCase):
    """The app dashboard has a brand-token gradient backdrop that keeps the page readable.

    The backdrop is drawn from the brand tokens as layered CSS gradients, with no image asset. Its
    tints stay low because the greeting, the date subtitle and the section label are painted
    directly on it. The worst-case composite is computed from the layers the bundle declares, so
    the contrast checks follow any re-tuned percentage.
    """

    def _compiled_css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build." % bundle_name,
        )
        self.assertNotIn(
            "a css error occured", css.lower(),
            "%s carries Odoo's CSS-error banner: Odoo re-serves the PREVIOUS stylesheet on a Sass "
            "failure, so these assertions would read stale styles. Fix the compile first."
            % bundle_name,
        )
        return css

    def _menu_root(self):
        return {
            "classes": HOME_MENU_ROOT_CLASSES,
            "ancestors": HOME_MENU_ROOT_ANCESTORS,
            "prev_sibling": frozenset(),
        }

    def _backdrop(self, css):
        """Return the menu root's backdrop.

        :return: ``(background_image_value, composited_worst_case_surface_hex)``; the surface is
            every declared alpha layer stacked on the page band, i.e. the darkest pixel the header
            text can land on.
        """
        image = _winning_declaration(css, self._menu_root(), ("background-image",))
        band = _resolve_to_hex(
            css, _winning_declaration(css, self._menu_root(), ("background-color", "background"))
        )
        self.assertIsNotNone(
            band,
            "could not resolve the home-menu page band (its background-color) from the compiled "
            "bundle - the surface every header assertion below is measured against.",
        )
        surface = band
        for hex_colour, percent in _COLOR_MIX_LAYER_RE.findall(image or ""):
            surface = _composite_over(
                _normalize_colour(hex_colour), surface, float(percent) / 100.0
            )
        return image, surface

    def test_the_app_dashboard_has_a_brand_backdrop_in_both_schemes(self):
        """`.o_viin_home_menu` paints a brand-derived gradient backdrop in light AND dark.

        The assertion is structural (gradient layers built from a `color-mix` of a brand token), not
        a hardcoded colour list: re-tuning a percentage or an angle is a design decision, losing the
        backdrop or hardcoding a non-token hex into it is the regression.
        """
        gradient_re = re.compile(r"(linear|radial|conic)-gradient\(", re.IGNORECASE)
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            image = _winning_declaration(css, self._menu_root(), ("background-image",))
            self.assertTrue(
                image and image.strip() not in ("none", "initial"),
                "[%s] .o_viin_home_menu declares no background-image (%r) - the app-dashboard "
                "backdrop is gone." % (arm, image),
            )
            self.assertTrue(
                gradient_re.search(image),
                "[%s] the home-menu background-image %r contains no gradient layer." % (arm, image),
            )
            layers = _COLOR_MIX_LAYER_RE.findall(image)
            self.assertTrue(
                layers,
                "[%s] the backdrop declares no `color-mix(... , transparent)` layer (%r). The "
                "backdrop must be derived from a brand token so it tracks the palette; a literal "
                "hex or an image URL here means it does not." % (arm, image),
            )

    def test_the_backdrop_is_tinted_with_the_chrome_ladder_not_the_brand_purple(self):
        """The backdrop is application chrome: its tints are the chrome teal, never the brand purple.

        Light mixes the chrome base, dark the deep chrome rung; the secondary cyan is the other
        facet in both. The purple of the content (buttons, links, the section label) never tints
        the page behind them.
        """
        for arm, bundle_name, chrome_rung in (
            ("light", BACKEND_BUNDLE, CHROME_BASE), ("dark", DARK_BUNDLE, CHROME_DEEP),
        ):
            css = self._compiled_css(bundle_name)
            image = _winning_declaration(css, self._menu_root(), ("background-image",))
            hexes = [hex_colour.lower() for hex_colour, _percent in _COLOR_MIX_LAYER_RE.findall(image)]
            self.assertIn(
                chrome_rung, hexes,
                "[%s] the home-menu backdrop layers %r do not mix the chrome rung %s."
                % (arm, hexes, chrome_rung),
            )
            for content_purple in (BRAND_PURPLE, ACTION_DEEP):
                self.assertNotIn(
                    content_purple, hexes,
                    "[%s] the home-menu backdrop is tinted with the content purple %s (layers %r): "
                    "the frame reads the chrome ladder." % (arm, content_purple, hexes),
                )

    def test_the_backdrop_keeps_the_header_text_wcag_aa(self):
        """The purple "APPLICATIONS" label clears WCAG AA over the composited backdrop.

        The label is the tightest of the texts painted directly on the backdrop, so it sets the tint
        percentages. Raising a tint until this fails is the signal to stop, not to relax the test.
        """
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            _image, surface = self._backdrop(css)
            label = _resolve_to_hex(
                css,
                _winning_declaration(
                    css,
                    {
                        "classes": HOME_SECTION_LABEL_CLASSES,
                        "ancestors": HOME_SECTION_LABEL_ANCESTORS,
                        "prev_sibling": frozenset(),
                    },
                    ("color",),
                ),
            )
            self.assertIsNotNone(
                label,
                "[%s] no compiled `color` resolves for .o_viin_home_section_label." % arm,
            )
            ratio = _contrast_ratio(label, surface)
            self.assertGreaterEqual(
                round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                "[%s] the home-menu section label %s measures only %.2f:1 over the composited "
                "backdrop %s - the app-dashboard background pushed it below WCAG AA normal text "
                "(%.1f:1). Lower the gradient tint percentages in home_menu.scss."
                % (arm, label, ratio, surface, WCAG_AA_NORMAL_TEXT),
            )

    def test_the_backdrop_keeps_the_app_tile_labels_wcag_aa(self):
        """App-tile labels stay AA because the tiles are opaque cards the backdrop never reaches.

        If the tiles turn translucent, their resolved background stops being an opaque token and the
        labels are measured against the gradient.
        """
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            tile = {
                "classes": HOME_TILE_CLASSES,
                "ancestors": HOME_TILE_ANCESTORS,
                "prev_sibling": frozenset(),
            }
            tile_bg = _resolve_to_hex(
                css, _winning_declaration(css, tile, ("background-color", "background"))
            )
            self.assertIsNotNone(
                tile_bg,
                "[%s] the app tile declares no resolvable background - if the tiles went "
                "translucent, the labels now read against the backdrop." % arm,
            )
            label = _resolve_to_hex(
                css,
                _winning_declaration(
                    css,
                    {
                        "classes": HOME_TILE_LABEL_CLASSES,
                        "ancestors": HOME_TILE_LABEL_ANCESTORS,
                        "prev_sibling": frozenset(),
                    },
                    ("color",),
                ),
            )
            self.assertIsNotNone(
                label, "[%s] no compiled `color` resolves for .o_viin_home_app_name." % arm
            )
            ratio = _contrast_ratio(label, tile_bg)
            self.assertGreaterEqual(
                round(ratio, 2), WCAG_AA_NORMAL_TEXT,
                "[%s] the app-tile label %s measures only %.2f:1 on the tile surface %s - below "
                "WCAG AA normal text (%.1f:1)."
                % (arm, label, ratio, tile_bg, WCAG_AA_NORMAL_TEXT),
            )

    def test_the_backdrop_adds_no_image_asset(self):
        """The backdrop stays payload-free: no `url()` into an image and no inlined `data:` URI.

        The backdrop is drawn from brand tokens, which keeps it scheme-aware and free of image
        licences.
        """
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            image = _winning_declaration(css, self._menu_root(), ("background-image",)) or ""
            self.assertNotIn(
                "url(", image.lower(),
                "[%s] the home-menu backdrop references an image asset (%r). It is drawn from brand "
                "tokens on purpose: core ships no such image and a third-party overlay "
                "cannot enter this OPL-1 module." % (arm, image),
            )

    def test_home_menu_scss_declares_no_new_border_radius(self):
        """home_menu.scss declares no `border-radius`: the cluster ships no radius overrides.

        Targeted repeat of the cluster-wide guard in test_theme_radius_is_core, so a radius slipped
        in beside the gradient is attributed to this file.
        """
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        home_menu_scss = os.path.join(module_dir, "static", "src", "home_menu", "home_menu.scss")
        with open(home_menu_scss, "r", encoding="utf-8") as handle:
            source = handle.read()
        source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
        source = re.sub(r"//[^\n]*", "", source)
        radii = re.findall(r"^\s*border-radius\s*:", source, re.MULTILINE)
        self.assertFalse(
            radii,
            "home_menu.scss declares %d border-radius rule(s) - the cluster owns none." % len(radii),
        )
