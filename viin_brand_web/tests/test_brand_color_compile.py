# Compiled-render behaviour guard (DESIGN 2.2 / 2.3 / 5, ODOO-AI-ETHOS #8): with the Viindoo
# branding installed, the backend brand surfaces must RENDER in the Viindoo brand teal - NEVER Odoo
# community purple (#71639e) nor enterprise aubergine (#714B67). Core web derives those surfaces
# from the $o-brand-odoo colour FAMILY at SASS COMPILE time, not from a single literal:
#   web/static/src/webclient/navbar/navbar.scss          .o_main_navbar { background: $o-navbar-background; }
#   web/static/src/webclient/navbar/navbar.variables.scss $o-navbar-background: $o-brand-odoo;
#   web/static/src/scss/primary_variables.scss            $o-brand-odoo: $o-community-color;  $o-community-color: #71639e;
# tests/test_brand_ssot.py only compares the SCSS *literal* $o-brand-primary to VIINDOO_THEME_COLOR;
# but $o-brand-primary is a DIFFERENT variable from $o-brand-odoo, so that test stays GREEN even
# when the compiled navbar leaks purple because the module dropped the $o-brand-odoo family. This
# test closes that gap by asserting the OBSERVABLE compiled colour of the .o_main_navbar surface -
# not a source literal. No extra dependency is required: viin_brand_web depends only on
# viin_brand + web, and .o_main_navbar ships inside web.assets_backend.
#
# Per the 2026-07-24 approved design decision, the navbar background must NOT compile to the flat
# brand teal VIINDOO_THEME_COLOR (#00bbce - 2.33:1 contrast with white text, fails WCAG AA
# normal-text). It must instead compile to the darker, WCAG-AA-compliant teal
# VIINDOO_NAVBAR_BACKGROUND_COLOR (#007f8e - 4.74:1 with white text), restoring the
# navbar-background darkening lost in the v19 SSOT rewrite, this time as a native-variable TOKEN
# rather than a cascade rule.
import re

from odoo.tests.common import TransactionCase, tagged

try:
    # Expected teal read from the module's single Python SSOT (never hardcoded-and-compared-to
    # itself). Imported defensively so a missing constant yields a crisp per-test failure rather
    # than breaking collection of the whole tests package.
    from ..controllers.webmanifest import VIINDOO_THEME_COLOR
except ImportError:
    VIINDOO_THEME_COLOR = None

# The two Odoo brand-family hexes that must NEVER surface once Viindoo branding is installed.
ODOO_COMMUNITY_PURPLE = "#71639e"
ODOO_ENTERPRISE_AUBERGINE = "#714b67"

# The darker, WCAG-AA-compliant teal the .o_main_navbar background must compile to (2026-07-24
# design decision). Same hue-family value already established as the "AA text/links" token in the
# approved P3 theme design doc (.odoo-ai/designs/viin-backend-theme-2026-07-17.md) - white-on-bg
# contrast 4.74:1, clearing the WCAG AA normal-text threshold (4.5:1) with comfortable margin.
# Reused here for SSOT/consistency rather than inventing a second, nearly-identical dark-teal
# shade. A fixed, hand-chosen design constant asserted as a literal - NOT derived by computing a
# Sass darken() formula inside this test, which would re-implement production logic and compare
# it against itself.
VIINDOO_NAVBAR_BACKGROUND_COLOR = "#007f8e"

# The primary-INTERACTIVE surfaces (primary button background/border, the root --primary token, and
# the interactive link colour) must clear WCAG AA against their white/on-surface text just like the
# navbar. That is the SAME darker AA teal shade as the navbar background - so it is reused here as an
# alias rather than re-declaring a second nearly-identical #007f8e literal (SSOT, ODOO-AI-ETHOS #11).
# Brand-IDENTITY decorative teal stays the flat VIINDOO_THEME_COLOR (#00bbce); only interactive
# tokens darken.
VIINDOO_AA_INTERACTIVE_COLOR = VIINDOO_NAVBAR_BACKGROUND_COLOR

BACKEND_BUNDLE = "web.assets_backend"

# Markers odoo/addons/base/models/assetsbundle.py appends to the SERVED payload when a Sass compile
# fails (`preprocess_css`, ~:492-511): it does NOT raise - it re-serves the PREVIOUS stylesheet with
# an error banner. Grounded verbatim from that source. Full reasoning for why BOTH halves (the
# freshly-populated `css_errors` list AND these cached-payload markers) are needed lives in
# tests/test_brand_cascade_compile.py::test_backend_bundle_compiles_without_css_errors - the SSOT
# for this guard; not restated here.
_CSS_ERROR_MARKERS = ("## CSS error message ##", "css_error_message", "A css error occured")

# A single "selector { body }" rule in the (minified) compiled CSS. [^{}] keeps each match to one
# non-nested rule, so rules nested inside @media wrappers are still captured individually.
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
# Selector token that targets the navbar bar ELEMENT itself - plain, a pseudo ':...' or a compound
# '.foo' - but NOT a descendant such as ".o_main_navbar .o_menu_brand" (those carry their own
# backgrounds and are not the brand surface under test).
_NAVBAR_SELF_RE = re.compile(r"^\.o_main_navbar([:.]|$)")
# A background / background-color declaration value (excludes background-image, -position, etc.).
_BG_RE = re.compile(r"background(?:-color)?\s*:\s*([^;]+)", re.IGNORECASE)
# A hex colour literal inside a declaration value.
_HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}")
# A CSS comment block. Odoo's asset pipeline (odoo/addons/base/models/assetsbundle.py,
# preprocess_css()'s final `'\n'.join(asset.minify() for asset in self.stylesheets)`)
# unconditionally prepends a "/* <source-file-path> */" banner immediately before each
# per-source-file compiled CSS fragment, in both debug and minified mode. When a source file's
# FIRST rule targets .o_main_navbar (as navbar.scss's does), _RULE_RE below has no comment
# awareness and captures the banner glued to the selectors group, e.g.
# "\n\n/* /web/static/src/webclient/navbar/navbar.scss */\n .o_main_navbar". Stripped out before
# selector matching (see _navbar_background_hexes) so that real selector is still recognized.
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


@tagged("post_install", "-at_install")
class BrandColorCompileTest(TransactionCase):

    def _compiled_backend_css(self):
        """Compile the backend asset bundle and return its CSS payload as decoded text.

        Grounded 19.0 API (OSM): ``ir.qweb._get_asset_bundle(bundle_name, css=True, js=False)``
        returns an AssetsBundle; ``.css()`` returns the compiled ``ir.attachment`` record(s) and
        ``attachment.raw`` is the binary content. Join across the recordset so a split bundle is
        handled, and decode leniently so the assertion (not a decode error) reports any problem.

        The payload is gated by `_assert_bundle_compiled_clean` before it is handed back: EVERY
        assertion in this file reads this text, so a silent Sass failure - which Odoo answers by
        re-serving the PREVIOUS stylesheet instead of raising - would make all of them happily
        confirm the old, correct colours while the backend renders stale styles."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(BACKEND_BUNDLE, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self._assert_bundle_compiled_clean(bundle, css)
        return css

    def _assert_bundle_compiled_clean(self, bundle, css):
        """Fail loudly when the backend bundle did not compile, or served a cached error payload.

        Both halves are required: ``css_errors`` reports the compile that just happened, but
        ``css()`` returns early when a compiled attachment is already cached - in which case the
        list stays empty even though the served payload IS an error payload. See
        tests/test_brand_cascade_compile.py::test_backend_bundle_compiles_without_css_errors for
        the full rationale (SSOT)."""
        self.assertFalse(
            bundle.css_errors,
            "%s reported SCSS compile errors: %s. On an error Odoo silently serves the previous "
            "stylesheet, so every colour assertion below would read stale - not current - brand "
            "tokens." % (BACKEND_BUNDLE, "; ".join(bundle.css_errors)),
        )
        for marker in _CSS_ERROR_MARKERS:
            self.assertNotIn(
                marker, css,
                "The compiled %s payload carries the error marker %r that assetsbundle.py appends "
                "when a Sass compile fails. A previously cached error payload is being served, so "
                "the backend is rendering stale styles." % (BACKEND_BUNDLE, marker),
            )

    def _navbar_background_hexes(self, css):
        """Return the lower-cased hex colours set as ``background`` on the .o_main_navbar element."""
        hexes = []
        for selectors, body in _RULE_RE.findall(css):
            # Strip any per-source-file comment banner (see _COMMENT_RE) before splitting, so a
            # rule whose real selector is glued to a leading "/* ... */" file-header comment is
            # still recognized as targeting the navbar element.
            uncommented_selectors = _COMMENT_RE.sub("", selectors)
            targets_navbar_element = any(
                _NAVBAR_SELF_RE.match(selector.strip())
                for selector in uncommented_selectors.split(",")
            )
            if not targets_navbar_element:
                continue
            for declared_value in _BG_RE.findall(body):
                hexes.extend(
                    hex_literal.lower() for hex_literal in _HEX_RE.findall(declared_value)
                )
        return hexes

    def test_backend_navbar_renders_brand_teal_not_odoo_purple_or_aubergine(self):
        """Backend navbar surface must compile to the Viindoo brand teal, never Odoo purple/aubergine.

        The .o_main_navbar background is derived by core web from the $o-brand-odoo colour family.
        If viin_brand_web drops that family, $o-brand-odoo falls back to core $o-community-color
        (#71639e) and the compiled navbar renders community purple. This asserts the OBSERVABLE
        compiled colour, so it fails whenever the brand family leaks a non-Viindoo colour."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand_web/controllers/webmanifest.py (the single Python brand-hex SSOT).",
        )
        expected_teal = VIINDOO_THEME_COLOR.lower()

        css = self._compiled_backend_css()
        self.assertTrue(
            css.strip(),
            "web.assets_backend compiled to empty CSS - the bundle did not build, so the navbar "
            "brand colour cannot be verified.",
        )

        navbar_hexes = self._navbar_background_hexes(css)
        self.assertTrue(
            navbar_hexes,
            "No background colour was found on the .o_main_navbar element in the compiled "
            "web.assets_backend bundle. Core web sets `.o_main_navbar { background: $o-brand-odoo }`, "
            "so a compiled navbar must carry a background hex to brand-check.",
        )

        # The Odoo brand-family colours must NOT surface on the navbar.
        self.assertNotIn(
            ODOO_COMMUNITY_PURPLE, navbar_hexes,
            "Backend navbar compiled to Odoo COMMUNITY PURPLE %s (navbar backgrounds: %r). The "
            "$o-brand-odoo colour family was dropped, so $o-brand-odoo fell back to core "
            "$o-community-color. viin_brand_web must set the family to the Viindoo brand teal."
            % (ODOO_COMMUNITY_PURPLE, navbar_hexes),
        )
        self.assertNotIn(
            ODOO_ENTERPRISE_AUBERGINE, navbar_hexes,
            "Backend navbar compiled to Odoo ENTERPRISE AUBERGINE %s (navbar backgrounds: %r). "
            "viin_brand_web must set the $o-brand-odoo colour family to the Viindoo brand teal."
            % (ODOO_ENTERPRISE_AUBERGINE, navbar_hexes),
        )

        # Regression guard (2026-07-24 design decision): the flat, un-darkened brand teal must
        # NEVER be the .o_main_navbar element's own background again - it may still legitimately
        # appear elsewhere in the compiled CSS (e.g. the raw $o-brand-odoo/$o-community-color
        # family literal used by OTHER selectors), but not here, where white nav text needs an
        # AA-compliant surface.
        self.assertNotIn(
            expected_teal, navbar_hexes,
            "Backend navbar regressed back to the flat, WCAG-AA-FAILING brand teal %s (navbar "
            "backgrounds: %r) - the navbar-background darkening token was dropped or reverted. "
            "The .o_main_navbar background must be the darker %s (VIINDOO_NAVBAR_BACKGROUND_COLOR), "
            "not the flat brand teal used elsewhere for brand identity."
            % (expected_teal, navbar_hexes, VIINDOO_NAVBAR_BACKGROUND_COLOR),
        )

        # The navbar surface must render the darker, WCAG-AA-compliant Viindoo teal - white nav
        # text needs >= 4.5:1 contrast (WCAG AA normal text); the flat brand teal only reaches
        # 2.33:1, while this darker teal reaches 4.74:1.
        self.assertIn(
            VIINDOO_NAVBAR_BACKGROUND_COLOR, navbar_hexes,
            "Backend navbar did not compile to the darker, WCAG-AA-compliant Viindoo teal %s "
            "(navbar backgrounds: %r). White nav text needs >= 4.5:1 contrast (WCAG AA normal "
            "text); %s reaches 4.74:1 while the flat brand teal %s only reaches 2.33:1. The "
            "$o-navbar-background token must resolve to the darker teal, not the flat brand teal."
            % (
                VIINDOO_NAVBAR_BACKGROUND_COLOR,
                navbar_hexes,
                VIINDOO_NAVBAR_BACKGROUND_COLOR,
                expected_teal,
            ),
        )

    def _rule_bodies_for(self, css, selector_matches):
        """Return the bodies of compiled rules with a selector token satisfying ``selector_matches``.

        Mirrors _navbar_background_hexes' comment-banner stripping so a selector glued to a leading
        per-source-file "/* ... */" banner is still recognised."""
        bodies = []
        for selectors, body in _RULE_RE.findall(css):
            uncommented_selectors = _COMMENT_RE.sub("", selectors)
            if any(
                selector_matches(selector.strip())
                for selector in uncommented_selectors.split(",")
            ):
                bodies.append(body)
        return bodies

    def _declared_values(self, bodies, prop):
        """Return every value declared for the CSS custom property ``--<prop>`` across ``bodies``.

        Values are stripped and lower-cased. The ``\\s*:`` guard means ``--link-color`` never
        accidentally matches ``--link-color-rgb`` (and vice versa)."""
        pattern = re.compile(r"--%s\s*:\s*([^;}]+)" % re.escape(prop))
        values = []
        for body in bodies:
            for match in pattern.finditer(body):
                values.append(match.group(1).strip().lower())
        return values

    def test_primary_interactive_tokens_render_wcag_aa_teal(self):
        """Primary-interactive tokens must compile to the darker AA teal, never the flat brand teal.

        The primary button background (.btn-primary --btn-bg / --btn-border-color) and the root
        --primary token carry white or near-white text, so they must clear WCAG AA (>= 4.5:1). The
        flat brand teal VIINDOO_THEME_COLOR (#00bbce) is only 2.33:1 against white; the AA teal
        VIINDOO_AA_INTERACTIVE_COLOR (#007f8e) reaches 4.74:1. These assert the OBSERVABLE compiled
        token values, so each fails on an un-darkened build and passes once the interactive tokens
        are darkened. Brand-IDENTITY uses of the flat teal elsewhere are NOT touched (see the
        closing invariant).

        --link-color used to be asserted here too; it moved to tests/test_link_tier_compile.py when
        the owner made the text link the brand SECONDARY purple (2026-08-03) - see the inline note
        where that block used to be."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand_web/controllers/webmanifest.py (the single Python brand-hex SSOT).",
        )
        flat_brand_teal = VIINDOO_THEME_COLOR.lower()
        expected_teal = VIINDOO_AA_INTERACTIVE_COLOR

        css = self._compiled_backend_css()
        self.assertTrue(
            css.strip(),
            "web.assets_backend compiled to empty CSS - the bundle did not build, so the "
            "interactive-token colours cannot be verified.",
        )

        root_bodies = self._rule_bodies_for(css, lambda selector: selector == ":root")
        btn_primary_bodies = self._rule_bodies_for(css, lambda selector: selector == ".btn-primary")
        self.assertTrue(
            root_bodies, "compiled web.assets_backend must declare a :root custom-property block."
        )
        self.assertTrue(
            btn_primary_bodies, "compiled web.assets_backend must declare a .btn-primary rule."
        )

        # --- Root --primary token ---------------------------------------------------------------
        primary_values = self._declared_values(root_bodies, "primary")
        self.assertTrue(primary_values, "no --primary custom property found on :root.")
        self.assertNotIn(
            flat_brand_teal, primary_values,
            "root --primary compiled to the flat, WCAG-AA-FAILING brand teal %s (%r). It must be "
            "the darker AA teal %s." % (flat_brand_teal, primary_values, expected_teal),
        )
        self.assertIn(
            expected_teal, primary_values,
            "root --primary must compile to the darker, WCAG-AA-compliant teal %s (%r)."
            % (expected_teal, primary_values),
        )

        # --- Primary button background + border (.btn-primary) ----------------------------------
        btn_bg_values = self._declared_values(btn_primary_bodies, "btn-bg")
        self.assertTrue(btn_bg_values, "no --btn-bg custom property found on .btn-primary.")
        self.assertNotIn(
            flat_brand_teal, btn_bg_values,
            "primary button background --btn-bg compiled to the flat, WCAG-AA-FAILING brand teal "
            "%s (%r) - white button text needs >= 4.5:1. It must be the darker AA teal %s."
            % (flat_brand_teal, btn_bg_values, expected_teal),
        )
        self.assertIn(
            expected_teal, btn_bg_values,
            "primary button background --btn-bg must compile to the darker AA teal %s (%r)."
            % (expected_teal, btn_bg_values),
        )

        btn_border_values = self._declared_values(btn_primary_bodies, "btn-border-color")
        self.assertTrue(
            btn_border_values, "no --btn-border-color custom property found on .btn-primary."
        )
        self.assertNotIn(
            flat_brand_teal, btn_border_values,
            "primary button border --btn-border-color compiled to the flat brand teal %s (%r); "
            "it must match the darker AA background %s." % (flat_brand_teal, btn_border_values, expected_teal),
        )
        self.assertIn(
            expected_teal, btn_border_values,
            "primary button border --btn-border-color must compile to the darker AA teal %s (%r)."
            % (expected_teal, btn_border_values),
        )

        # --- The interactive-teal tier no longer includes --link-color -------------------------
        # OWNER REVISION 2026-08-03: the HYPERLINK left this tier. This test used to assert that
        # :root --link-color / --link-color-rgb compiled to the AA teal, because $link-color was
        # simply an alias of $o-main-link-color (core bootstrap_overridden.scss:76). The owner then
        # asked for the text link to carry the Viindoo SECONDARY purple
        # ("tao muốn override nó thành màu secondary của Viindoo"), so
        # static/src/scss/link_tier.scss splits the token: --link-color is now the hyperlink colour
        # (purple in light, unchanged teal in dark) while Bootstrap's `.nav-link` / `.btn-link` /
        # `.pagination` BORROWERS are re-anchored back onto the AA teal asserted above.
        #
        # The link tier's own guard is tests/test_link_tier_compile.py - the SSOT for it, asserting
        # the light purple, the unchanged dark teal, and that no button/tab/pager picks up purple.
        # The assertions are NOT duplicated here (ODOO-AI-ETHOS #11); what remains in this test is
        # the surface set that genuinely still is the AA teal: .btn-primary and root --primary.
        # A future edit that "restores" a teal --link-color assertion here would contradict the
        # owner decision AND the sibling file - read both before changing this.

        # Invariant (NOT a global purge): the flat brand-identity teal may - and should - still
        # appear elsewhere in the compiled CSS (brand-decorative surfaces). Darkening the
        # interactive tokens must not nuke the brand identity.
        self.assertIn(
            flat_brand_teal, css.lower(),
            "the flat brand-identity teal %s must still appear in the compiled CSS for brand "
            "decorative surfaces - only the primary-interactive tokens darken to %s."
            % (flat_brand_teal, expected_teal),
        )
