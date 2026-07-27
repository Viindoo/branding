# Compile-cascade behaviour guards for viin_backend_theme's OWN widget surfaces (PR #658 review-fix
# T-3; ODOO-AI-ETHOS #8: protect the BEHAVIOR, not the code).
#
# WHY THIS FILE REPLACES test_w1_substrate.py (RETIRED).
# -----------------------------------------------------------------------------------------------
# test_w1_substrate.py asserted the CONTENT of static/src/scss/dark_surfaces.scss and scheme.scss -
# ~40 source-text assertions protecting the RETIRED no-reload `[data-bs-theme]` allow-list dark
# engine. PR #658 C-2 DELETED both files and re-based dark mode on the RECOMPILED web.assets_web_dark
# bundle owned by viin_brand_common (dark_palette.scss, Option A Layer 1), so those assertions now
# (a) read files that no longer exist and (b) snapshot an architecture that was deliberately removed.
# Keeping them would red every correct step of the re-architecture, so they are gone. What survived
# as genuine BEHAVIOUR is folded here, plus the NEW Option-A contract the theme now owns:
#   * KEPT  - the backend bundle still compiles to a healthy stylesheet (an aborted compile = an
#             unstyled webclient), and the two compile-abort landmines stay out (a var()-ified
#             surface var feeding a Sass colour function; a '--' inside an XML comment).
# (The T-4 always-dark rail focus-ring guard was removed with the vertical rail itself in PR #658
# item 1 - the flat home menu is now the sole app switcher, so there is no rail surface to assert.
# The T-3 stepper done-marker AA guard went the same way on 2026-08-03: the owner reverted the D6
# stepper entirely and the theme no longer owns ANY statusbar surface, so there is no theme-owned
# marker left to measure. What replaced it is the opposite assertion - "we do not touch core's
# arrow statusbar at all" - in tests/test_theme_core_chrome_untouched.py.)
# DROPPED as an architecture-preference snapshot (not a behaviour): the old "zero --viin-* custom
# properties" rule - the review-fix design (C-7 focus tokens) legitimately introduces --o-viin-*
# levers, so that guard would now red a correct implementation. See the design doc §C-2 / §T-3.
#
# WHY COMPILED-CSS, NOT SOURCE SUBSTRINGS.
# -----------------------------------------------------------------------------------------------
# The dark widget colour is produced by SASS at compile time and, for T-3, lives in a SEPARATE bundle
# (web.assets_web_dark = `('include','web.assets_web')` + a trailing `*.dark.scss` glob) that
# recompiles every backend rule. Only the compiled bundle shows whether the done-marker actually
# renders a readable colour on the dark panel; a source-substring check ("#4FD4E2 appears somewhere")
# is not a behaviour assertion. So the contrast tests resolve the value a real element COMPUTES
# through the real cascade, REUSING viin_brand_common's cascade + WCAG SSOT
# (tests/test_brand_cascade_compile.py, whose dark arm landed with C-6) instead of re-implementing it
# (ODOO-AI-ETHOS #11 SSOT). viin_backend_theme depends on viin_brand_common, so that module is always
# installed and importable at test time; if it is ever restructured this import is the signal to
# re-ground, not to fork a second copy of the resolver.
import os
import re

from odoo.tests.common import BaseCase, TransactionCase, tagged

from odoo.addons.viin_brand_common.tests.test_brand_cascade_compile import (
    CHROME_BASE,
    CHROME_DEEP,
    DARK_BUNDLE,
    DARK_MUTED_TIER,
    RETIRED_DARK_PURPLE,
    WCAG_AA_NORMAL_TEXT,
    _VAR_RE,
    _contrast_ratio,
    _iter_rules,
    _normalize_colour,
    _winning_declaration,
)
# The brand-secondary purple is declared ONLY in SCSS (there is no Python constant for it, unlike
# the brand primary), so the expected value is READ from viin_brand_common's token SSOT with that
# module's own resolver rather than re-literalised here (ODOO-AI-ETHOS #11).
from odoo.addons.viin_brand_common.tests.test_brand_ssot import (
    BRAND_VARIABLES_SCSS,
    _resolve_scss_hex,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
SCSS_DIR = os.path.join(MODULE_DIR, "static", "src", "scss")
STATIC_SRC = os.path.join(MODULE_DIR, "static", "src")

BACKEND_BUNDLE = "web.assets_backend"

# Element ancestor pools (class-only), transcribed from the theme's own templates.
# home_menu.xml:10-32 - `.o_viin_home_menu` > `.o_viin_home_content` > `.o_viin_home_body` >
# `<div class="o_viin_home_section_label">Applications</div>`. The menu ROOT is modelled separately
# because it is the element that declares the page band the label renders on
# (`background-color: var(--secondary-bg)`, home_menu.scss:15).
HOME_MENU_ROOT_CLASSES = frozenset({"o_viin_home_menu"})
HOME_MENU_ROOT_ANCESTORS = frozenset({"o_web_client", "o_action_manager"})
HOME_SECTION_LABEL_CLASSES = frozenset({"o_viin_home_section_label"})
HOME_SECTION_LABEL_ANCESTORS = HOME_MENU_ROOT_ANCESTORS | HOME_MENU_ROOT_CLASSES | {
    "o_viin_home_content", "o_viin_home_body", "d-flex", "flex-column", "flex-grow-1",
}
# The muted-grey tier the label carried before the semantic accent landed (home_menu.scss used
# `var(--secondary-color)`). Named only so the failure message can say what a revert looks like; the
# load-bearing assertions are "equals the $o-brand-secondary SSOT" and the measured contrast.
PRE_ACCENT_LABEL_TOKEN = "--secondary-color"


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _strip_scss_comments(text):
    """Drop // line and /* */ block comments so a rule is never matched inside a comment."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _root_prop(css, name):
    """Last value declared for the custom property ``name`` on a ``:root`` rule, or None.

    The dark palette declares the dark ``--link-color`` on ``:root``; the class-based cascade
    resolver deliberately does not model ``:root`` (it needs a positive class), so a ``color`` that
    resolves through a ``:root`` custom property is read here. Last declaration wins (source order)."""
    values = []
    for _order, selector, body in _iter_rules(css):
        if selector.strip() != ":root":
            continue
        for declaration in body.split(";"):
            key, separator, value = declaration.partition(":")
            if separator and key.strip() == name:
                values.append(value.strip())
    return values[-1] if values else None


def _resolve_to_hex(css, value):
    """Normalise ``value`` to a ``#rrggbb`` colour, following ONE ``var()`` hop through ``:root``.

    Robust to both spellings the T-3 fix may use for the dark teal foreground: a literal
    (``color: #4fd4e2``) or the runtime prop (``color: var(--link-color)``)."""
    if value is None:
        return None
    match = _VAR_RE.match(value.strip())
    if match:
        resolved = _root_prop(css, match.group(1))
        value = resolved if resolved is not None else match.group(2)
    return _normalize_colour(value) if value else None


@tagged("post_install", "-at_install")
class TestThemeDarkWidgetContrast(TransactionCase):
    """The theme's own widget surfaces must be readable/visible in both compiled bundles."""

    def _compiled_css(self, bundle_name):
        """Compile ``bundle_name`` and return its CSS payload as decoded text (19.0 API:
        ``ir.qweb._get_asset_bundle(name, css=True, js=False).css()`` - same contract as
        viin_brand_common/tests/test_brand_cascade_compile.py)."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so its surfaces cannot be "
            "verified." % bundle_name,
        )
        return css

    def test_backend_bundle_compiles_to_a_healthy_stylesheet(self):
        """web.assets_backend must compile to a large, error-free stylesheet.

        The compile-abort landmine (a var()-ified surface var feeding color-contrast()/mix(), or a
        Sass error) collapses the whole bundle to a ~23KB stub carrying the "A css error occured"
        banner and renders the webclient unstyled. A healthy compile is far larger and carries none
        of that banner. End-to-end proof the theme's SCSS contributions stay compile-safe."""
        css = self._compiled_css(BACKEND_BUNDLE)
        self.assertGreater(
            len(css), 100_000,
            "web.assets_backend compiled to only %d bytes - the SCSS build aborted (a var()-ified "
            "surface var / color-contrast() landmine, or another Sass error). The webclient would "
            "render unstyled." % len(css),
        )
        self.assertNotIn(
            "a css error occured", css.lower(),
            "web.assets_backend carries the Odoo CSS-error banner - the bundle did not compile clean.",
        )

    def test_home_menu_section_label_is_the_structure_purple_on_its_own_band(self):
        """The home-menu section label must be the STRUCTURE purple, readable on its band, both schemes.

        OWNER DECISION 2026-08-03. viin_brand_common's COLOUR LAW (brand_variables.scss) reads
        TEAL = ACT / PURPLE = META-STRUCTURE. "Applications" is a section label - it organises the
        app grid, it is not something the user can do - so it joins the group-by search facet and
        the list group header as a purple STRUCTURE accent. It previously read
        `var(--secondary-color)`, the muted-grey tier: readable, but semantically silent.

        >>> OWNER REVISION 2026-08-03 (same day): THE PURPLE IS LIGHT-MODE ONLY. <<<
        The owner then ruled purple wrong on a dark canvas, so the two arms of this test assert
        OPPOSITE things on purpose:
          light  the label IS $o-brand-secondary #7F4282 (and is not a teal);
          dark   the label is NOT purple - it returns to exactly what it was before the accent
                 landed, `var(--secondary-color)`, i.e. "the default look / core colours". That token
                 flips dark-correct on its own: dark_palette.scss re-points $body-secondary-color to
                 #8EA5A8, which Bootstrap emits as --secondary-color, giving 7.24:1 on the dark band.

        THE SURFACE IS RESOLVED, NOT ASSUMED. The label sits on the menu root's own band, which
        home_menu.scss paints `background-color: var(--secondary-bg)` - a runtime prop that flips
        between the schemes ($gray-200 #E9ECEF light / #0B1315 dark, the latter from
        viin_brand_common's dark_palette.scss $body-secondary-bg). So the contrast is measured
        against the band the compiled bundle ACTUALLY declares for that element, in each bundle,
        rather than against a hardcoded page colour that could silently go stale.

        STILL NO DARK COMPANION FILE, AND THAT IS PART OF THE CONTRACT: the choice is made at COMPILE
        time by viin_brand_common's $o-viin-dark-bundle flag, so each bundle carries exactly one
        `color` declaration and there is no cascade fight and no *.dark.scss to keep in sync.

        This is the lowest-risk purple in the cluster: `.o_viin_home_section_label` is theme-owned
        markup that no core rule targets, so the fix needs no `!important` and no token re-point -
        which the assertions rely on only in that they expect a plain resolvable colour.

        WOULD FAIL IF REVERTED: restoring `var(--secondary-color)` unconditionally fails the "equals
        $o-brand-secondary" assertion in the light arm; dropping the `@if` guard (purple in both)
        fails the dark refusal."""
        expected_purple = _resolve_scss_hex(_read(BRAND_VARIABLES_SCSS), "$o-brand-secondary")
        self.assertIsNotNone(
            expected_purple,
            "$o-brand-secondary must be declared in viin_brand_common's brand_variables.scss - it "
            "is the SSOT for every META/STRUCTURE purple surface in this cluster.",
        )
        expected_purple = expected_purple.lower()

        label = {
            "classes": HOME_SECTION_LABEL_CLASSES,
            "ancestors": HOME_SECTION_LABEL_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        menu_root = {
            "classes": HOME_MENU_ROOT_CLASSES,
            "ancestors": HOME_MENU_ROOT_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)

            raw_label = _winning_declaration(css, label, ("color",))
            self.assertIsNotNone(
                raw_label,
                "No compiled `color` applies to .o_viin_home_section_label in %s - the home-menu "
                "SCSS is not reaching that bundle." % bundle_name,
            )
            colour = _resolve_to_hex(css, raw_label)
            self.assertIsNotNone(
                colour,
                "The %s home-menu section label `color` %r carries no resolvable colour."
                % (arm, raw_label),
            )
            self.assertNotIn(
                colour, (CHROME_BASE, CHROME_DEEP),
                "The %s home-menu section label compiled the teal %s. A section label is "
                "STRUCTURE, not an ACT - see the colour law in viin_brand_common's "
                "brand_variables.scss." % (arm, colour),
            )
            if arm == "light":
                self.assertEqual(
                    colour, expected_purple,
                    "The home-menu section label compiled %s instead of the brand secondary %s "
                    "($o-brand-secondary). A revert to the muted `var(%s)` grey looks like this."
                    % (colour, expected_purple, PRE_ACCENT_LABEL_TOKEN),
                )
            else:
                self.assertNotEqual(
                    colour, expected_purple,
                    "The home-menu section label compiled the light brand purple %s in the DARK "
                    "bundle - 2.24:1 on the dark band. The purple accent is light-only from "
                    "2026-08-03; wrap the declaration in `@if not $o-viin-dark-bundle`."
                    % expected_purple,
                )
                self.assertNotEqual(
                    colour, RETIRED_DARK_PURPLE,
                    "The home-menu section label compiled the RETIRED dark purple %s. The owner "
                    "rejected a darker purple as the answer to the dark canvas - the answer is no "
                    "purple." % RETIRED_DARK_PURPLE,
                )
                self.assertEqual(
                    colour, DARK_MUTED_TIER,
                    "The home-menu section label compiled %s in the dark bundle instead of the "
                    "muted tier %s that `var(%s)` resolves to there. That token IS the pre-accent "
                    "default the owner asked the label to fall back to; anything else means a dark "
                    "accent of ours is still being emitted."
                    % (colour, DARK_MUTED_TIER, PRE_ACCENT_LABEL_TOKEN),
                )

            raw_band = _winning_declaration(css, menu_root, ("background-color", "background"))
            self.assertIsNotNone(
                raw_band,
                "The .o_viin_home_menu root declares no background in %s, so the band the label "
                "renders on cannot be resolved." % bundle_name,
            )
            band = _resolve_to_hex(css, raw_band)
            self.assertIsNotNone(
                band,
                "The %s home-menu band %r carries no resolvable colour." % (arm, raw_band),
            )
            ratio = _contrast_ratio(colour, band)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "The home-menu section label renders %s on the %s band %s - %.2f:1, below the WCAG "
                "AA normal-text threshold of %.1f:1. In the dark bundle this is the signature of a "
                "$o-brand-secondary that lost its dark arm (the light #7F4282 is 2.50:1 there)."
                % (colour, arm, band, ratio, WCAG_AA_NORMAL_TEXT),
            )


class TestThemeCompileSafetyInvariants(BaseCase):
    """Static source guards for the two compile-abort landmines - no DB needed. These protect real
    catastrophic BEHAVIOURS (unstyled / blank webclient), not deleted-file text, so they survive the
    C-2 re-architecture and stay."""

    def test_surface_vars_are_never_var_ified(self):
        """primary_variables.scss must NOT var()-ify a surface var that feeds a Sass colour function.

        `$o-view-background-color` / `$o-webclient-background-color` feed core's `$body-bg` ->
        `color-contrast()` -> `mix()`, which cannot evaluate a var() at compile time; a var()-ified
        surface var aborts the WHOLE web.assets_web bundle (unstyled webclient). They MUST stay real
        hexes - dark is delivered by the recompiled web.assets_web_dark bundle, not a runtime var
        flip. This is the exact regression guard for that proven abort."""
        source = _strip_scss_comments(_read(os.path.join(SCSS_DIR, "primary_variables.scss")))
        for var_name in ("$o-view-background-color", "$o-webclient-background-color"):
            offenders = re.findall(re.escape(var_name) + r"\s*:\s*[^;]*var\(", source)
            self.assertFalse(
                offenders,
                "%s is var()-ified in primary_variables.scss (%r). That poisons core's "
                "$body-bg -> color-contrast() -> mix() and aborts the whole web.assets_web bundle "
                "(unstyled webclient). Keep it a real hex." % (var_name, offenders),
            )

    def test_no_double_hyphen_in_xml_comments(self):
        """No XML comment under static/src may contain '--' (double hyphen).

        '--' is illegal inside `<!-- ... -->` and makes the QWeb parser reject the WHOLE web.assets
        template bundle -> `OwlError: Missing template "web.WebClient"` -> the entire backend renders
        BLANK. A single such slip in a comment took down 100% of the webclient during W2, so this
        cheap static guard scans every OWL/QWeb .xml under static/src."""
        offenders = []
        for root, _dirs, files in os.walk(STATIC_SRC):
            for name in files:
                if not name.endswith(".xml"):
                    continue
                path = os.path.join(root, name)
                for match in re.finditer(r"<!--(.*?)-->", _read(path), re.DOTALL):
                    if "--" in match.group(1):
                        offenders.append(
                            "%s: %r" % (os.path.relpath(path, MODULE_DIR), match.group(1).strip()[:70])
                        )
        self.assertFalse(
            offenders,
            "XML comment(s) contain an illegal '--' (double hyphen), which breaks the entire "
            "web.assets template bundle and blanks the webclient:\n%s" % "\n".join(offenders),
        )
