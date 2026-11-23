# SSOT guard: each brand hex is declared ONCE.
# The Python constant of the content colour (VIINDOO_BRAND_COLOR) and the SCSS brand variable
# ($o-brand-primary in brand_variables.scss) must carry the SAME colour; so must the Python constant
# of the chrome colour (VIINDOO_THEME_COLOR) and the SCSS chrome base ($o-viin-chrome-base). This
# test asserts the SOURCES agree - it never hardcodes the literal on both sides.
import os
import re

from odoo.tests.common import TransactionCase, tagged

try:
    # Imported defensively so a missing constant fails each test crisply instead of breaking
    # collection of the whole tests package.
    from ..controllers.webmanifest import VIINDOO_BRAND_COLOR, VIINDOO_THEME_COLOR
except ImportError:
    VIINDOO_BRAND_COLOR = VIINDOO_THEME_COLOR = None

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
BRAND_VARIABLES_SCSS = os.path.join(MODULE_DIR, "static", "src", "scss", "brand_variables.scss")
BRAND_CASCADE_SCSS = os.path.join(MODULE_DIR, "static", "src", "scss", "brand_cascade.scss")


def _strip_scss_comments(scss):
    """Drop `/* */` block and `//` line comments so only code is counted: a brand hex quoted in a
    comment is not a live literal."""
    scss = re.sub(r"/\*.*?\*/", "", scss, flags=re.DOTALL)
    scss = re.sub(r"//[^\n]*", "", scss)
    return scss


def _resolve_scss_hex(scss, var_name, _seen=None):
    """Return the concrete hex ``var_name`` resolves to in ``scss`` (following $var
    indirection), or None if no hex literal is reachable."""
    if _seen is None:
        _seen = set()
    if var_name in _seen:
        return None
    _seen.add(var_name)
    # Anchored to start-of-line so a `//` comment containing "$var: ...;" text (brand_variables.scss
    # quotes `$o-brand-odoo: $o-enterprise-color;` in a comment) can never stand in for a dropped
    # real declaration.
    match = re.search(r"^\s*%s\s*:\s*([^;]+);" % re.escape(var_name), scss, re.MULTILINE)
    if not match:
        return None
    rhs = match.group(1).replace("!default", "").strip()
    hex_match = re.match(r"^(#[0-9A-Fa-f]{3,8})$", rhs)
    if hex_match:
        return hex_match.group(1)
    var_match = re.match(r"^(\$[\w-]+)$", rhs)
    if var_match:
        return _resolve_scss_hex(scss, var_match.group(1), _seen)
    return None


@tagged("post_install", "-at_install")
class BrandHexSsotTest(TransactionCase):

    def _scss(self):
        self.assertTrue(
            os.path.exists(BRAND_VARIABLES_SCSS),
            "brand_variables.scss (the SCSS brand-hex SSOT) must exist at %s" % BRAND_VARIABLES_SCSS,
        )
        with open(BRAND_VARIABLES_SCSS, "r", encoding="utf-8") as scss_file:
            return scss_file.read()

    def test_brand_hex_ssot_python_and_scss_agree(self):
        """Brand hex is a single SSOT: Python VIINDOO_BRAND_COLOR == SCSS $o-brand-primary."""
        self.assertIsNotNone(
            VIINDOO_BRAND_COLOR,
            "VIINDOO_BRAND_COLOR must be defined in "
            "viin_brand/controllers/webmanifest.py (the single Python content-colour SSOT).",
        )
        scss_hex = _resolve_scss_hex(self._scss(), "$o-brand-primary")
        self.assertIsNotNone(
            scss_hex,
            "brand_variables.scss must assign a hex to $o-brand-primary "
            "(directly or via a $var), so the Python side can be compared against it.",
        )
        self.assertEqual(
            scss_hex.lower(),
            VIINDOO_BRAND_COLOR.lower(),
            "Brand-hex SSOT mismatch: SCSS $o-brand-primary=%s but Python "
            "VIINDOO_BRAND_COLOR=%s - both must be the same brand colour."
            % (scss_hex, VIINDOO_BRAND_COLOR),
        )

    def test_chrome_hex_ssot_python_and_scss_agree(self):
        """The chrome hex is a single SSOT: Python VIINDOO_THEME_COLOR == SCSS $o-viin-chrome-base,
        which is also what the navbar background resolves to."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand/controllers/webmanifest.py (the single Python chrome-colour SSOT).",
        )
        scss = self._scss()
        for var_name in ("$o-viin-chrome-base", "$o-navbar-background"):
            scss_hex = _resolve_scss_hex(scss, var_name)
            self.assertIsNotNone(
                scss_hex,
                "brand_variables.scss must assign a hex to %s (directly or via a $var)." % var_name,
            )
            self.assertEqual(
                scss_hex.lower(),
                VIINDOO_THEME_COLOR.lower(),
                "Chrome-hex SSOT mismatch: SCSS %s=%s but Python VIINDOO_THEME_COLOR=%s - the "
                "browser theme colour must be the colour of the navbar."
                % (var_name, scss_hex, VIINDOO_THEME_COLOR),
            )

    def test_the_brand_primary_is_the_viindoo_purple_and_the_chrome_is_the_teal(self):
        """The content colour (buttons, links, the emails and livechat defaults) is the Viindoo
        purple #7F4282; the colour of the frame (the navbar, the PWA) is the chrome teal #007F8E."""
        self.assertIsNotNone(VIINDOO_BRAND_COLOR)
        self.assertEqual(VIINDOO_BRAND_COLOR.upper(), "#7F4282")
        self.assertIsNotNone(VIINDOO_THEME_COLOR)
        self.assertEqual(VIINDOO_THEME_COLOR.upper(), "#007F8E")

    def test_the_dark_content_colour_is_the_cyan_alias_not_a_new_literal(self):
        """dark_palette.scss re-points the one content token at the cyan it already declares: no new
        hex enters the module, and the dark rungs are derived from the token."""
        dark_scss = os.path.join(os.path.dirname(BRAND_VARIABLES_SCSS), "dark_palette.scss")
        with open(dark_scss, "r", encoding="utf-8") as scss_file:
            scss = scss_file.read()
        self.assertEqual((_resolve_scss_hex(scss, "$o-brand-primary") or "").lower(), "#00bbce")
        self.assertEqual((_resolve_scss_hex(scss, "$primary") or "").lower(), "#00bbce")
        brand_scss = self._scss()
        self.assertEqual(
            (_resolve_scss_hex(brand_scss, "$o-navbar-badge-bg") or "").lower(),
            VIINDOO_BRAND_COLOR.lower(),
            "the navbar counters read the scheme-invariant identity purple, not $o-brand-primary",
        )

    def test_brand_odoo_color_family_matches_ssot(self):
        """The Odoo brand-colour FAMILY ($o-community-color, $o-enterprise-color, $o-brand-odoo)
        must ALL resolve to the same hex as the Python SSOT VIINDOO_BRAND_COLOR.

        Core web/portal derive the content brand surfaces from this family at Sass compile time
        (the navbar reads `$o-navbar-background`, which viin_brand points at the chrome base):
          web/.../webclient/navbar/navbar.variables.scss  $o-navbar-background: $o-brand-odoo;
          web/.../scss/primary_variables.scss             $o-brand-odoo: $o-community-color;
          portal/.../chatter/scss/primary_variables.scss  $o-brand-odoo: $o-enterprise-color;
                                                           (unconditional reassignment)
        viin_brand does not depend on portal, so tests/test_brand_color_compile.py can only
        exercise the community path (web.assets_backend). If $o-enterprise-color's purple override
        were removed, the portal chatter bundle would regress to Odoo enterprise aubergine
        #714B67 while that compile test stayed green. Asserting the source-literal hex of all
        three members needs no compile step and no portal dependency."""
        self.assertIsNotNone(
            VIINDOO_BRAND_COLOR,
            "VIINDOO_BRAND_COLOR must be defined in "
            "viin_brand/controllers/webmanifest.py (the single Python content-colour SSOT).",
        )
        scss = self._scss()

        expected_hex = VIINDOO_BRAND_COLOR.lower()
        # Each family member with the surface it feeds, so a failure names what would leak.
        family_members = [
            (
                "$o-community-color",
                "feeds $o-brand-odoo on the COMMUNITY path (core web/static/src/scss/"
                "primary_variables.scss: $o-brand-odoo: $o-community-color) - core default "
                "#71639e (Odoo community purple).",
            ),
            (
                "$o-enterprise-color",
                "feeds $o-brand-odoo on the PORTAL CHATTER path (portal/static/src/chatter/scss/"
                "primary_variables.scss unconditionally reassigns $o-brand-odoo: "
                "$o-enterprise-color) - core default #714B67 (Odoo enterprise aubergine). "
                "viin_brand does not depend on portal, so NO compiled-CSS test can ever "
                "observe this surface; only this source-literal assertion protects it.",
            ),
            (
                "$o-brand-odoo",
                "the family head directly consumed by the content surfaces of core (html_editor "
                "table_menu, web_tour pointer, website).",
            ),
        ]
        for var_name, why in family_members:
            scss_hex = _resolve_scss_hex(scss, var_name)
            self.assertIsNotNone(
                scss_hex,
                "brand_variables.scss must assign a hex to %s (directly or via a $var) - %s"
                % (var_name, why),
            )
            self.assertEqual(
                scss_hex.lower(),
                expected_hex,
                "Brand-colour FAMILY mismatch: SCSS %s=%s but Python VIINDOO_BRAND_COLOR=%s - "
                "%s If %s stops resolving to the Viindoo purple, this surface leaks back to an Odoo "
                "brand colour, undetected by the compiled-CSS test."
                % (var_name, scss_hex, VIINDOO_BRAND_COLOR, why, var_name),
            )

    def test_brand_hex_literal_is_declared_exactly_once(self):
        """No bare brand-hex literal drifts out of the ONE declaration.

        The brand purple #7F4282, the secondary cyan #00BBCE, the chrome teal #007F8E and the two deep
        rungs (#005E68 chrome, #592E5B content) must each appear as a CODE literal EXACTLY once -
        at `$o-brand-primary`, `$o-brand-secondary`, `$o-viin-chrome-base`, `$o-viin-chrome-deep` and
        `$o-viin-action-deep`. Every other use (the Odoo brand-colour family, $primary,
        $o-main-link-color, the $o-btns-bs-override entries, `$o-navbar-background`, the structural
        accent) aliases the declared Sass var, so a single edit re-tints all of them.
        Comments are stripped first. The other pre-computed button shades (#663568 / #F2ECF2 /
        #4C284E) are not a brand hex and are not counted (Sass colour helpers are banned in
        brand_variables.scss)."""
        code = ""
        for path in (BRAND_VARIABLES_SCSS, BRAND_CASCADE_SCSS):
            self.assertTrue(os.path.exists(path), "%s must exist for the SSOT literal count" % path)
            with open(path, "r", encoding="utf-8") as scss_file:
                code += "\n" + _strip_scss_comments(scss_file.read())
        for brand_hex in ("#7F4282", "#00BBCE", "#007F8E", "#005E68", "#592E5B"):
            count = len(re.findall(re.escape(brand_hex), code, re.IGNORECASE))
            self.assertEqual(
                count, 1,
                "Brand hex %s must appear EXACTLY once as a CODE literal (its single SSOT "
                "declaration); every other use must alias the declared Sass var. Found %d "
                "occurrences across brand_variables.scss + brand_cascade.scss."
                % (brand_hex, count),
            )
