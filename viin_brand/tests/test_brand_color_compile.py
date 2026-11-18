# Compiled-render guard: with the Viindoo branding installed, the backend brand surfaces must
# RENDER in the Viindoo brand teal - never Odoo community purple (#71639e) nor enterprise
# aubergine (#714B67). Core web derives those surfaces from the $o-brand-odoo colour FAMILY at Sass
# compile time, not from a single literal:
#   web/static/src/webclient/navbar/navbar.scss           .o_main_navbar { background: $o-navbar-background; }
#   web/static/src/webclient/navbar/navbar.variables.scss $o-navbar-background: $o-brand-odoo;
#   web/static/src/scss/primary_variables.scss            $o-brand-odoo: $o-community-color;
#                                                         $o-community-color: #71639e;
# tests/test_brand_ssot.py only compares the SCSS literal $o-brand-primary to VIINDOO_THEME_COLOR,
# a different variable from $o-brand-odoo, so it stays green even when the compiled navbar leaks
# purple. This test asserts the observable compiled colour of the .o_main_navbar surface, which
# ships inside web.assets_backend.
#
# The navbar background must NOT compile to the flat brand teal VIINDOO_THEME_COLOR (#00bbce -
# 2.33:1 contrast with white text, fails WCAG AA normal-text). It compiles to the darker,
# WCAG-AA-compliant teal VIINDOO_NAVBAR_BACKGROUND_COLOR (#007f8e - 4.74:1 with white text).
import re

from odoo.tests.common import TransactionCase, tagged

try:
    # Imported defensively so a missing constant fails each test crisply instead of breaking
    # collection of the whole tests package.
    from ..controllers.webmanifest import VIINDOO_THEME_COLOR
except ImportError:
    VIINDOO_THEME_COLOR = None

# The two Odoo brand-family hexes that must NEVER surface once Viindoo branding is installed.
ODOO_COMMUNITY_PURPLE = "#71639e"
ODOO_ENTERPRISE_AUBERGINE = "#714b67"

# The darker, WCAG-AA-compliant teal the .o_main_navbar background must compile to: white-on-bg
# contrast 4.74:1, clearing the WCAG AA normal-text threshold (4.5:1). A fixed literal, not derived
# from a Sass darken() formula, which would compare production logic against itself.
VIINDOO_NAVBAR_BACKGROUND_COLOR = "#007f8e"

# The primary-interactive surfaces (primary button background/border and the root --primary token)
# must clear WCAG AA against their white text just like the navbar, so they use the same AA teal.
# The decorative brand teal stays the flat VIINDOO_THEME_COLOR (#00bbce).
VIINDOO_AA_INTERACTIVE_COLOR = VIINDOO_NAVBAR_BACKGROUND_COLOR

BACKEND_BUNDLE = "web.assets_backend"

# Markers odoo/addons/base/models/assetsbundle.py appends to the served payload when a Sass compile
# fails: it does not raise, it re-serves the previous stylesheet with an error banner. Why both the
# `css_errors` list and these markers are needed: see
# tests/test_brand_cascade_compile.py::test_backend_bundle_compiles_without_css_errors.
_CSS_ERROR_MARKERS = ("## CSS error message ##", "css_error_message", "A css error occured")

# A single "selector { body }" rule in the compiled CSS; [^{}] keeps each match to one non-nested
# rule, so rules inside @media wrappers are still captured individually.
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
# The navbar element itself - plain, a pseudo ':...' or a compound '.foo' - but not a descendant
# such as ".o_main_navbar .o_menu_brand", which carries its own background.
_NAVBAR_SELF_RE = re.compile(r"^\.o_main_navbar([:.]|$)")
_BG_RE = re.compile(r"background(?:-color)?\s*:\s*([^;]+)", re.IGNORECASE)
_HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}")
# Odoo's asset pipeline prepends a "/* <source-file-path> */" banner before each per-source-file
# compiled CSS fragment. When a file's first rule targets .o_main_navbar, _RULE_RE captures the
# banner glued to the selectors group, so it is stripped before selector matching.
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


@tagged("post_install", "-at_install")
class BrandColorCompileTest(TransactionCase):

    def _compiled_backend_css(self):
        """Compile the backend asset bundle and return its CSS payload as decoded text.

        The payload is gated by `_assert_bundle_compiled_clean`: a silent Sass failure, which Odoo
        answers by re-serving the previous stylesheet, would make every assertion confirm stale
        colours."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(BACKEND_BUNDLE, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self._assert_bundle_compiled_clean(bundle, css)
        return css

    def _assert_bundle_compiled_clean(self, bundle, css):
        """Fail loudly when the backend bundle did not compile, or served a cached error payload.

        ``css_errors`` reports the compile that just happened, but ``css()`` returns early when a
        compiled attachment is already cached, leaving the list empty even though the served payload
        is an error payload; hence both checks."""
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
                "when a Sass compile fails. A cached error payload is being served, so "
                "the backend is rendering stale styles." % (BACKEND_BUNDLE, marker),
            )

    def _navbar_background_hexes(self, css):
        """Return the lower-cased hex colours set as ``background`` on the .o_main_navbar element."""
        hexes = []
        for selectors, body in _RULE_RE.findall(css):
            # Strip the per-source-file banner (see _COMMENT_RE) before splitting.
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
        If viin_brand drops that family, $o-brand-odoo falls back to core $o-community-color
        (#71639e) and the compiled navbar renders community purple. This asserts the OBSERVABLE
        compiled colour, so it fails whenever the brand family leaks a non-Viindoo colour."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand/controllers/webmanifest.py (the single Python brand-hex SSOT).",
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
            "$o-community-color. viin_brand must set the family to the Viindoo brand teal."
            % (ODOO_COMMUNITY_PURPLE, navbar_hexes),
        )
        self.assertNotIn(
            ODOO_ENTERPRISE_AUBERGINE, navbar_hexes,
            "Backend navbar compiled to Odoo ENTERPRISE AUBERGINE %s (navbar backgrounds: %r). "
            "viin_brand must set the $o-brand-odoo colour family to the Viindoo brand teal."
            % (ODOO_ENTERPRISE_AUBERGINE, navbar_hexes),
        )

        # The flat brand teal may appear elsewhere in the compiled CSS but never as the navbar's
        # own background, where white nav text needs an AA-compliant surface.
        self.assertNotIn(
            expected_teal, navbar_hexes,
            "Backend navbar regressed back to the flat, WCAG-AA-FAILING brand teal %s (navbar "
            "backgrounds: %r) - the navbar-background darkening token was dropped or reverted. "
            "The .o_main_navbar background must be the darker %s (VIINDOO_NAVBAR_BACKGROUND_COLOR), "
            "not the flat brand teal used elsewhere for brand identity."
            % (expected_teal, navbar_hexes, VIINDOO_NAVBAR_BACKGROUND_COLOR),
        )

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

        Strips the per-source-file comment banner like _navbar_background_hexes."""
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
        VIINDOO_AA_INTERACTIVE_COLOR (#007f8e) reaches 4.74:1. Brand-identity uses of the flat teal
        elsewhere are untouched (see the closing invariant). --link-color is covered by
        tests/test_link_tier_compile.py."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand/controllers/webmanifest.py (the single Python brand-hex SSOT).",
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

        # --link-color is not in this tier: link_tier.scss makes it the hyperlink colour (purple
        # in light) and re-anchors the Bootstrap borrowers onto the AA teal. Its guard is
        # tests/test_link_tier_compile.py.

        # The flat brand-identity teal must still appear elsewhere in the compiled CSS (decorative
        # surfaces); only the primary-interactive tokens darken.
        self.assertIn(
            flat_brand_teal, css.lower(),
            "the flat brand-identity teal %s must still appear in the compiled CSS for brand "
            "decorative surfaces - only the primary-interactive tokens darken to %s."
            % (flat_brand_teal, expected_teal),
        )
