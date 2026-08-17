# Compiled-cascade guard for THE APP-DASHBOARD BACKGROUND (owner request 2026-08-03: "Ở trên app
# dashboard, tao muốn có cái background như ở các phiên bản trước đã từng có").
#
# WHAT SHIPPED, AND WHY THERE IS NO IMAGE FILE TO ASSERT ON
# =================================================================================================
# The investigation behind the implementation is recorded in full at the top of
# static/src/home_menu/home_menu.scss. In short: Odoo 19 CE core ships NO home/app-drawer background
# asset (web/static/img/ has only graph_background.png and form_sheetbg.png, and CE has no app
# drawer at all), and the image the PREVIOUS Viindoo versions used -
# web_responsive/static/src/img/home-menu-bg-overlay.svg, referenced by
# to_backend_theme/.../apps_menu/apps_menu.scss:3 on origin/19.0 - is an OCA LGPL-3 asset belonging
# to a module this very PR deletes, so it cannot be re-added to an OPL-1 module. The backdrop is
# therefore re-DRAWN from the cluster's own brand tokens as layered CSS gradients: original work,
# zero image payload, and scheme-aware for free.
#
# WHAT THIS FILE PROTECTS - THE TWO WAYS THIS FEATURE CAN GO WRONG
# =================================================================================================
#  1. IT SILENTLY DISAPPEARS. A refactor of home_menu.scss, or a `background:` shorthand added later
#     in the cascade, drops the layers and the dashboard is a flat grey page again with nobody
#     noticing. Guarded by resolving the winning `background-image` on the menu root in BOTH
#     compiled bundles and requiring real gradient layers built from the brand token.
#  2. IT MAKES THE PAGE UNREADABLE. This is the real risk and the reason the tints are low single
#     digits: the app-tile labels are safe by construction (they sit on OPAQUE cards), but the
#     greeting, the date subtitle and the purple "APPLICATIONS" label are painted DIRECTLY on this
#     backdrop, so every gradient layer eats into their contrast. Guarded by compositing the layers
#     the bundle ACTUALLY declares - worst case, all of them overlapping - and re-measuring the
#     section label and the tile label against WCAG AA on the result.
#
# WHY THE COMPOSITE IS COMPUTED HERE RATHER THAN HARDCODED
# =================================================================================================
# Hardcoding "the backdrop is #c8e5ea" would go stale the moment a percentage is re-tuned, and would
# assert a colour instead of the property that matters (readability). Instead the test PARSES the
# compiled `color-mix(in srgb, <hex> <pct>%, transparent)` layers out of the bundle and alpha-
# composites them with the standard source-over formula the cluster already owns
# (viin_brand_web _composite_over). That formula is EXTERNAL (W3C), not production logic, so this
# is not the test re-implementing the feature and comparing it against itself - it reads what
# shipped and applies the spec to it.
import os
import re

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand_web.tests.test_brand_cascade_compile import (
    DARK_BUNDLE,
    WCAG_AA_NORMAL_TEXT,
    _composite_over,
    _contrast_ratio,
    _normalize_colour,
    _winning_declaration,
)
# Reuse this module's own :root reader and var() resolver rather than forking a second copy
# (ODOO-AI-ETHOS #11) - they already model exactly the "colour that resolves through a :root custom
# property" case every surface below hits.
from .test_theme_dark_widgets import (
    BACKEND_BUNDLE,
    HOME_MENU_ROOT_ANCESTORS,
    HOME_MENU_ROOT_CLASSES,
    HOME_SECTION_LABEL_ANCESTORS,
    HOME_SECTION_LABEL_CLASSES,
    _resolve_to_hex,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
HOME_MENU_SCSS = os.path.join(MODULE_DIR, "static", "src", "home_menu", "home_menu.scss")

# An app TILE and its label, transcribed from home_menu.xml -
# `.o_viin_home_grid` > `<a class="o_app o_viin_home_app ..." href="...">` > `<span class="o_viin_home_app_name">`.
# (The tile became an anchor on 2026-08-17 so core's app-switch tours can resolve
# `a[data-menu-xmlid="<app>"]`, exactly as core renders its own apps menu. The CLASS list is
# byte-for-byte what the previous <button> carried, which is why this contrast model is unaffected -
# the cascade resolver keys on classes, and none of them changed.)
HOME_TILE_CLASSES = frozenset({"o_app", "o_viin_home_app", "d-flex", "flex-column", "align-items-center"})
HOME_TILE_ANCESTORS = HOME_SECTION_LABEL_ANCESTORS | {"o_viin_home_grid"}
HOME_TILE_LABEL_CLASSES = frozenset({"o_viin_home_app_name"})
HOME_TILE_LABEL_ANCESTORS = HOME_TILE_ANCESTORS | HOME_TILE_CLASSES

# One translucent backdrop layer as the compiled bundle spells it, e.g.
# `color-mix(in srgb, #00BBCE 7%, transparent)`. Anything mixed toward `transparent` is an alpha
# layer over the page band; a layer mixed toward an opaque colour would not be, hence the explicit
# `transparent` in the pattern.
_COLOR_MIX_LAYER_RE = re.compile(
    r"color-mix\(\s*in\s+srgb\s*,\s*(#[0-9A-Fa-f]{3,8})\s+([\d.]+)%\s*,\s*transparent\s*\)",
    re.IGNORECASE,
)
# A gradient function of any kind - what proves the backdrop is DRAWN rather than absent.
_GRADIENT_RE = re.compile(r"(linear|radial|conic)-gradient\(", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestHomeMenuBackground(TransactionCase):
    """The app dashboard has a brand backdrop, and it did not cost the page its readability."""

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
        """Return ``(background_image_value, composited_worst_case_surface_hex)`` for the menu root.

        The worst case is every declared alpha layer stacked on the page band, which is what the
        header text sits on where the facets overlap. Compositing in declaration order is the
        conservative reading: order does not change the final alpha, and all layers share one hue
        family here, so the result is the darkest/most saturated pixel the header can land on."""
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
        """`.o_viin_home_menu` must paint a brand-derived gradient backdrop in light AND dark.

        RED before this feature: home_menu.scss declared only `background-color: var(--secondary-bg)`
        and no `background-image` at all, so the dashboard was a flat grey page - which is exactly
        what the owner asked to change.

        The assertion is deliberately structural (gradient layers, built from a `color-mix` of a
        brand token) rather than a hardcoded colour list: re-tuning a percentage or an angle is a
        design decision, whereas LOSING the backdrop, or hardcoding a non-token hex into it, are
        the regressions worth failing on."""
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            image = _winning_declaration(css, self._menu_root(), ("background-image",))
            self.assertTrue(
                image and image.strip() not in ("none", "initial"),
                "[%s] .o_viin_home_menu declares no background-image (%r) - the app-dashboard "
                "backdrop is gone." % (arm, image),
            )
            self.assertTrue(
                _GRADIENT_RE.search(image),
                "[%s] the home-menu background-image %r contains no gradient layer." % (arm, image),
            )
            layers = _COLOR_MIX_LAYER_RE.findall(image)
            self.assertTrue(
                layers,
                "[%s] the backdrop declares no `color-mix(... , transparent)` layer (%r). The "
                "backdrop must be derived from a brand token so it tracks the palette; a literal "
                "hex or an image URL here means it no longer does." % (arm, image),
            )

    def test_the_backdrop_keeps_the_header_text_wcag_aa(self):
        """The purple "APPLICATIONS" label must still clear WCAG AA over the new backdrop.

        This is the constraint that sets the tint percentages. The section label is the WORST case
        of the three texts painted directly on the backdrop: the greeting is near-black body text
        with an enormous margin, whereas the label is a mid-tone purple that started at 5.90:1 on
        the bare #E9ECEF band - so it is the one that runs out of room first. Measured against the
        fully-composited worst-case surface, not the bare band.

        Raising a tint percentage until this reds is the signal to stop, not to relax the test."""
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
        """App-tile labels must stay AA - the tiles are opaque cards, and must remain so.

        The tile carries its own `background-color: var(--body-bg)`, so the backdrop never reaches
        the label. That is a DESIGN GUARANTEE rather than a happy accident, and this test is what
        makes it one: if a later change makes the tiles translucent (to "let the background show
        through"), the resolved tile background stops being an opaque token and the labels start
        reading against the gradient - which this measures."""
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
        """The backdrop must stay payload-free - no url() into an image, no inlined data: URI.

        Recorded as a behaviour because the tempting "fix" for a future fidelity complaint is to
        drop the recovered OCA SVG back in (licence conflict - see the file header of
        home_menu.scss) or to inline a data: URI (bundle bloat, and it defeats the scheme-awareness
        the gradient layers get for free). Either shows up here."""
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            image = _winning_declaration(css, self._menu_root(), ("background-image",)) or ""
            self.assertNotIn(
                "url(", image.lower(),
                "[%s] the home-menu backdrop references an image asset (%r). It is drawn from brand "
                "tokens on purpose: core 19.0 ships no such image and the previous theme's overlay "
                "is OCA LGPL-3, which cannot enter this OPL-1 module." % (arm, image),
            )

    def test_home_menu_scss_declares_no_new_border_radius(self):
        """The cluster ships ZERO radius overrides (owner 2026-08-03 "bo hết") - adding a backdrop
        must not have smuggled one in.

        tests/test_theme_radius_is_core.py owns the cluster-wide guard; this is a targeted repeat on
        the one file this change touched, so a radius slipped in beside the gradient is attributed
        to the right edit."""
        with open(HOME_MENU_SCSS, "r", encoding="utf-8") as handle:
            source = handle.read()
        source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
        source = re.sub(r"//[^\n]*", "", source)
        radii = re.findall(r"^\s*border-radius\s*:", source, re.MULTILINE)
        self.assertFalse(
            radii,
            "home_menu.scss declares %d border-radius rule(s) - the cluster owns none." % len(radii),
        )
