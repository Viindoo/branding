# SSOT guard (DESIGN 2.2 / 2.3 / 5, ODOO-AI-ETHOS #11): the brand hex is declared ONCE.
# The single Python brand constant (VIINDOO_THEME_COLOR) and the single SCSS brand variable
# ($o-brand-primary in brand_variables.scss) must carry the SAME colour. This test asserts the
# two SOURCES agree - it never hardcodes the literal on both sides.
import os
import re

from odoo.tests.common import TransactionCase, tagged

try:
    # RED now: the backend coder has not yet added the SSOT constant. Imported defensively so a
    # missing constant yields a crisp per-test failure instead of breaking collection of the
    # whole tests package.
    from ..controllers.webmanifest import VIINDOO_THEME_COLOR
except ImportError:
    VIINDOO_THEME_COLOR = None

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
BRAND_VARIABLES_SCSS = os.path.join(MODULE_DIR, "static", "src", "scss", "brand_variables.scss")
BRAND_CASCADE_SCSS = os.path.join(MODULE_DIR, "static", "src", "scss", "brand_cascade.scss")


def _strip_scss_comments(scss):
    """Drop `/* */` block and `//` line comments so only CODE is counted (a brand hex quoted in an
    explanatory comment is not a live literal and must not be miscounted as one)."""
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
    # Anchor to true start-of-line (only leading whitespace allowed) so a `//`-prefixed
    # explanatory comment that happens to contain "$var: ...;" text (e.g. brand_variables.scss
    # documents the portal clobber `$o-brand-odoo: $o-enterprise-color;` inside a comment) can
    # NEVER shadow the real declaration. Without the anchor, an unanchored re.search matched the
    # comment occurrence first and made a dropped real $o-brand-odoo line resolve via the comment
    # (a false pass on the exact regression this guard exists to catch).
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

    def test_brand_hex_ssot_python_and_scss_agree(self):
        """Brand hex is a single SSOT: Python VIINDOO_THEME_COLOR == SCSS $o-brand-primary."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand_web/controllers/webmanifest.py (the single Python brand-hex SSOT).",
        )
        self.assertTrue(
            os.path.exists(BRAND_VARIABLES_SCSS),
            "brand_variables.scss (the SCSS brand-hex SSOT) must exist at %s" % BRAND_VARIABLES_SCSS,
        )
        with open(BRAND_VARIABLES_SCSS, "r", encoding="utf-8") as scss_file:
            scss = scss_file.read()
        scss_hex = _resolve_scss_hex(scss, "$o-brand-primary")
        self.assertIsNotNone(
            scss_hex,
            "brand_variables.scss must assign a hex to $o-brand-primary "
            "(directly or via a $var), so the Python side can be compared against it.",
        )
        self.assertEqual(
            scss_hex.lower(),
            VIINDOO_THEME_COLOR.lower(),
            "Brand-hex SSOT mismatch: SCSS $o-brand-primary=%s but Python "
            "VIINDOO_THEME_COLOR=%s - both must be the same brand colour."
            % (scss_hex, VIINDOO_THEME_COLOR),
        )

    def test_brand_odoo_color_family_matches_ssot(self):
        """The Odoo brand-colour FAMILY ($o-community-color, $o-enterprise-color, $o-brand-odoo)
        must ALL resolve to the same hex as the Python SSOT VIINDOO_THEME_COLOR.

        This is a DIFFERENT invariant than test_brand_hex_ssot_python_and_scss_agree above (which
        only checks $o-brand-primary, a variable core never reads). Core web/portal derive the
        BACKEND BRAND SURFACES from this three-member family at SASS compile time:
          web/.../webclient/navbar/navbar.variables.scss  $o-navbar-background: $o-brand-odoo;
          web/.../scss/primary_variables.scss             $o-brand-odoo: $o-community-color;
          portal/.../chatter/scss/primary_variables.scss  $o-brand-odoo: $o-enterprise-color;
                                                           (unconditional reassignment)
        viin_brand_web does NOT depend on portal, so tests/test_brand_color_compile.py's
        compiled-CSS assertion can only ever exercise the COMMUNITY resolution path
        (web.assets_backend) - it can never observe the portal chatter bundle. Concrete blind
        spot this closes: if $o-enterprise-color's teal override were removed while
        $o-community-color and $o-brand-odoo stayed teal, the compile test would stay GREEN (the
        navbar still renders teal via the community path) while the portal chatter bundle
        silently regressed to Odoo ENTERPRISE AUBERGINE #714B67 - the original CRITICAL leak this
        module exists to prevent. Asserting the SOURCE-LITERAL hex of all three family members
        directly needs no compile step and no portal dependency, so it protects the surface the
        compile test structurally cannot reach."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand_web/controllers/webmanifest.py (the single Python brand-hex SSOT).",
        )
        self.assertTrue(
            os.path.exists(BRAND_VARIABLES_SCSS),
            "brand_variables.scss (the SCSS brand-hex SSOT) must exist at %s" % BRAND_VARIABLES_SCSS,
        )
        with open(BRAND_VARIABLES_SCSS, "r", encoding="utf-8") as scss_file:
            scss = scss_file.read()

        expected_hex = VIINDOO_THEME_COLOR.lower()
        # Each family member and WHY its own resolution path matters, so a failure message
        # identifies exactly which member broke and which real surface it would leak.
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
                "viin_brand_web does not depend on portal, so NO compiled-CSS test can ever "
                "observe this surface; only this source-literal assertion protects it.",
            ),
            (
                "$o-brand-odoo",
                "the family head directly consumed by the navbar background and other direct "
                "core uses (loading_indicator, html_editor table_menu, web_responsive).",
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
                "Brand-colour FAMILY mismatch: SCSS %s=%s but Python VIINDOO_THEME_COLOR=%s - "
                "%s If %s stops resolving to the Viindoo teal, this surface leaks back to an Odoo "
                "brand colour, undetected by the compiled-CSS test."
                % (var_name, scss_hex, VIINDOO_THEME_COLOR, why, var_name),
            )

    def test_brand_hex_literal_is_declared_exactly_once(self):
        """No bare brand-hex literal drifts out of the ONE declaration (PR #658 review-fix C-8 SSOT).

        The decorative brand teal #00BBCE and the AA interactive teal #007F8E must each appear as a
        CODE literal EXACTLY once - #00BBCE at `$o-brand-primary`, #007F8E at `$o-navbar-background`.
        Every other use (the Odoo brand-colour family, $primary, $o-main-link-color, the
        $o-btns-bs-override AA-base entries, the chrome ladder) aliases the declared Sass var, so a
        single edit re-tints all of them and no second literal can silently disagree. Comments are
        stripped first: a brand hex quoted in an explanatory comment is documentation, not a live
        literal. The pre-computed button SHADES (#00515B / #002428 / #E6F2F4) are NOT the brand hex
        and are deliberately not counted (Sass colour helpers are banned in brand_variables.scss)."""
        code = ""
        for path in (BRAND_VARIABLES_SCSS, BRAND_CASCADE_SCSS):
            self.assertTrue(os.path.exists(path), "%s must exist for the SSOT literal count" % path)
            with open(path, "r", encoding="utf-8") as scss_file:
                code += "\n" + _strip_scss_comments(scss_file.read())
        for brand_hex in ("#00BBCE", "#007F8E"):
            count = len(re.findall(re.escape(brand_hex), code, re.IGNORECASE))
            self.assertEqual(
                count, 1,
                "Brand hex %s must appear EXACTLY once as a CODE literal (its single SSOT "
                "declaration); every other use must alias the declared Sass var. Found %d "
                "occurrences across brand_variables.scss + brand_cascade.scss."
                % (brand_hex, count),
            )
