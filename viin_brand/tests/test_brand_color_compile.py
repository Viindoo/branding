# Compiled-render guard: with the Viindoo branding installed, the backend frame (the navbar) must
# RENDER in the Viindoo chrome teal and the content (the primary button, --primary) in the Viindoo
# brand purple - never Odoo community purple (#71639e) nor enterprise aubergine (#714B67). Core web
# derives the navbar from the $o-brand-odoo colour FAMILY at Sass compile time unless a chrome
# token is set, and the content surfaces from it always:
#   web/static/src/webclient/navbar/navbar.scss           .o_main_navbar { background: $o-navbar-background; }
#   web/static/src/webclient/navbar/navbar.variables.scss $o-navbar-background: $o-brand-odoo;
#   web/static/src/scss/primary_variables.scss            $o-brand-odoo: $o-community-color;
#                                                         $o-community-color: #71639e;
# tests/test_brand_ssot.py only compares the SCSS literals to the Python constants, a different
# variable from $o-brand-odoo, so it stays green even when the compiled navbar leaks core's purple.
# This test asserts the observable compiled colour of the .o_main_navbar surface, which ships inside
# web.assets_backend, and of the primary button and the root --primary token.
#
# The navbar compiles to the chrome teal #007F8E (white text on it is 4.74:1); the primary button and
# --primary compile to the brand purple #7F4282 (6.99:1). The foot of the navbar carries no stripe.
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

# The chrome teal the .o_main_navbar background must compile to: white-on-bg contrast 4.74:1,
# clearing the WCAG AA normal-text threshold (4.5:1). A fixed literal, not derived from a Sass
# formula, which would compare production logic against itself.
VIINDOO_NAVBAR_BACKGROUND_COLOR = "#007f8e"

# The primary-interactive surfaces (primary button background/border and the root --primary token)
# carry white text and use the brand purple, which is the content colour, not the chrome one.
VIINDOO_AA_INTERACTIVE_COLOR = "#7f4282"

BACKEND_BUNDLE = "web.assets_backend"
DARK_BUNDLE = "web.assets_web_dark"

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

    def test_backend_navbar_renders_chrome_teal_not_odoo_purple_or_aubergine(self):
        """Backend navbar surface must compile to the Viindoo chrome teal, never Odoo purple/aubergine.

        The .o_main_navbar background is derived by core web from `$o-navbar-background`, which
        defaults to the $o-brand-odoo colour family. If viin_brand drops the chrome token, the
        navbar falls back to the family (the content purple, or core's #71639e when the family is
        dropped too). This asserts the OBSERVABLE compiled colour, so it fails whenever the frame
        leaks the content colour or a non-Viindoo colour."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand/controllers/webmanifest.py (the single Python brand-hex SSOT).",
        )
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
        self.assertNotIn(
            ODOO_COMMUNITY_PURPLE, navbar_hexes,
            "Backend navbar compiled to Odoo COMMUNITY PURPLE %s (navbar backgrounds: %r). The "
            "$o-brand-odoo colour family was dropped, so $o-brand-odoo fell back to core "
            "$o-community-color." % (ODOO_COMMUNITY_PURPLE, navbar_hexes),
        )
        self.assertNotIn(
            ODOO_ENTERPRISE_AUBERGINE, navbar_hexes,
            "Backend navbar compiled to Odoo ENTERPRISE AUBERGINE %s (navbar backgrounds: %r)."
            % (ODOO_ENTERPRISE_AUBERGINE, navbar_hexes),
        )
        self.assertIn(
            VIINDOO_NAVBAR_BACKGROUND_COLOR, navbar_hexes,
            "Backend navbar did not compile to the Viindoo chrome teal %s (navbar backgrounds: %r)."
            % (VIINDOO_NAVBAR_BACKGROUND_COLOR, navbar_hexes),
        )
        self.assertNotIn(
            VIINDOO_AA_INTERACTIVE_COLOR, navbar_hexes,
            "Backend navbar compiled to the content purple %s (navbar backgrounds: %r): the frame "
            "reads the chrome ladder, not the brand purple."
            % (VIINDOO_AA_INTERACTIVE_COLOR, navbar_hexes),
        )
        self.assertEqual(
            VIINDOO_THEME_COLOR.lower(), VIINDOO_NAVBAR_BACKGROUND_COLOR,
            "the PWA colour and the navbar must be the same chrome colour",
        )

    def test_navbar_foot_carries_no_stripe(self):
        """The foot of the navbar is plain in both schemes: no inset shadow, no stripe.

        The navbar is the chrome teal bar and nothing else; the cyan has no role in it. Every compiled
        rule that targets the navbar element itself is read, and none declares an inset shadow."""
        for bundle_name in (BACKEND_BUNDLE, DARK_BUNDLE):
            bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
            css = "".join(
                (attachment.raw or b"").decode("utf-8", "replace")
                for attachment in (bundle.css() or self.env["ir.attachment"])
            )
            self.assertTrue(css.strip(), "%s compiled to empty CSS" % bundle_name)
            navbar_rules = 0
            for selectors, body in _RULE_RE.findall(css):
                if not any(
                    _NAVBAR_SELF_RE.match(selector.strip())
                    for selector in _COMMENT_RE.sub("", selectors).split(",")
                ):
                    continue
                navbar_rules += 1
                for shadow in re.findall(r"box-shadow\s*:\s*([^;]+)", body):
                    with self.subTest(bundle=bundle_name, selectors=selectors.strip()[:60]):
                        self.assertNotIn(
                            "inset", shadow.lower(),
                            "the navbar element declares the inset shadow %r in %s: the foot of the "
                            "navbar carries no stripe." % (shadow, bundle_name),
                        )
            self.assertTrue(navbar_rules, "no compiled rule targets the navbar element in %s" % bundle_name)

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

    def test_primary_interactive_tokens_render_the_brand_purple(self):
        """The primary button and the root --primary token compile to the brand purple.

        The primary button background (.btn-primary --btn-bg / --btn-border-color) and the root
        --primary token carry white text: #7F4282 reaches 6.99:1 on it. The hover and pressed rungs
        are the Bootstrap shades of the same purple. --link-color is covered by
        tests/test_link_tier_compile.py."""
        css = self._compiled_backend_css()
        root_bodies = self._rule_bodies_for(css, lambda selector: selector == ":root")
        btn_primary_bodies = self._rule_bodies_for(css, lambda selector: selector == ".btn-primary")
        self.assertTrue(
            root_bodies, "compiled web.assets_backend must declare a :root custom-property block."
        )
        self.assertTrue(
            btn_primary_bodies, "compiled web.assets_backend must declare a .btn-primary rule."
        )

        self.assertIn(
            VIINDOO_AA_INTERACTIVE_COLOR, self._declared_values(root_bodies, "primary"),
            "root --primary must compile to the brand purple %s." % VIINDOO_AA_INTERACTIVE_COLOR,
        )
        expected_button = {
            "btn-bg": VIINDOO_AA_INTERACTIVE_COLOR,
            "btn-border-color": VIINDOO_AA_INTERACTIVE_COLOR,
            "btn-color": "#ffffff",
            "btn-hover-bg": "#663568",
            "btn-hover-border-color": "#592e5b",
            "btn-hover-color": "#ffffff",
            "btn-active-bg": "#f2ecf2",
            "btn-active-border-color": VIINDOO_AA_INTERACTIVE_COLOR,
            "btn-active-color": "#4c284e",
            "btn-disabled-bg": VIINDOO_AA_INTERACTIVE_COLOR,
            "btn-disabled-border-color": VIINDOO_AA_INTERACTIVE_COLOR,
            "btn-disabled-color": "#ffffff",
        }
        for prop, expected in expected_button.items():
            with self.subTest(prop=prop):
                self.assertIn(
                    expected, self._declared_values(btn_primary_bodies, prop),
                    "`.btn-primary` --%s must compile to %s." % (prop, expected),
                )
