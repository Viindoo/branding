# Three core widget surfaces the theme is NOT allowed to restyle (owner reverts, 2026-08-03).
#
# WHAT THIS FILE PROTECTS, AND WHY IT IS PHRASED AS AN ABSENCE.
# -----------------------------------------------------------------------------------------------
# The theme's job is to add what Odoo CE lacks, not to re-shape widgets the owner is happy with. On
# 2026-08-03 three of its restyles were reverted because each one had turned a working core widget
# into a broken one. A "the new look is correct" test cannot express that outcome - the requirement
# is that OUR code stops participating - so every guard here asserts an ABSENCE plus the core
# behaviour that absence restores:
#
#   1. STATUSBAR STAYS AN ARROW. "Cho state tren form view tao van muon giu cai mui ten nhu mac
#      dinh. Hien tai thi `.o_viin_stepper` bien chung thanh cac o chu nhat." The D6 stepper set
#      `clip-path: none` on `.o_arrow_button`, which is exactly what turns core's chevron chain into
#      rectangles - so the guard is "a compiled `clip-path: none` never reaches an arrow button, and
#      core's polygon geometry is still there". The brand-teal CURRENT arrow the owner does want is
#      NOT ours and is not touched: viin_brand_web paints it through core's own
#      --o-statusbar-border-active token (see that module's
#      test_statusbar_current_arrow_outline_is_chrome_base_over_a_light_fill).
#
#   2. THE NAVBAR APPS ICON IS PAINTED BY CORE, SO IT IS WHITE. "App icon hien co mau den. Tao muon
#      cho nay khong override gi de no trang nhu cu." The repurposed button (apps_menu_home.xml)
#      lost core's Dropdown-injected `dropdown-toggle`, so it matched no navbar-entry rule, and the
#      `text-reset` we added forced `color: inherit` all the way up to the body colour - black on the
#      teal navbar. The guard is two-sided: no colour is authored by us anywhere for that button,
#      AND the colour it actually COMPUTES equals core's navbar-entry token.
#
#   3. THE STAT BUTTON IS CORE'S LAYOUT. The D7 reskin boxed the icon in a teal swatch, uppercased
#      the label, removed the border and added a hairline rule - which pushed the label outside the
#      button. The guard names each of those four defects as a property that must NOT be declared,
#      so a partial re-introduction still fails. The Viindoo purple TEXT is deliberately NOT guarded
#      here: it is viin_brand_web's (--o-stat-text-color, light-only), asserted in that module's
#      test_brand_secondary_text_clears_wcag_aa_on_light_and_dark_surfaces.
#
# WHY COMPILED CSS AND A SOURCE SCAN, NOT ONE OR THE OTHER. The compiled assertions describe what a
# user SEES, and survive a re-introduction that arrives under a different class name or through a
# token. But a rule the resolver cannot model (an @media-only override, an exotic selector) would
# slip past them, and the previous passes proved this cluster re-grows restyles file by file - so
# the source scan holds the other side: the theme's OWN sources must not mention those core hooks at
# all. Neither half is redundant; both are cheap.
#
# THE CASCADE MACHINERY IS REUSED, NOT FORKED (ODOO-AI-ETHOS #11). viin_brand_web already owns a
# compiled-CSS cascade resolver, the WCAG helpers and the element ancestor pools for exactly these
# surfaces; viin_backend_theme depends on that module, so it is always importable at test time.
import os
import re

from odoo.tests.common import BaseCase, TransactionCase, tagged

from odoo.addons.viin_brand_web.tests.test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    BUTTONBOX_ANCESTORS,
    CHROME_BASE,
    DARK_BUNDLE,
    STAT_BUTTON_ANCESTORS,
    WCAG_NON_TEXT_MIN,
    _computed_value,
    _contrast_ratio,
    _declarations,
    _iter_rules,
    _normalize_colour,
    _winning_declaration,
)
from odoo.addons.viin_brand_web.tests.test_brand_ssot import (
    BRAND_VARIABLES_SCSS,
    _resolve_scss_hex,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
STATIC_SRC = os.path.join(MODULE_DIR, "static", "src")
APPS_MENU_SCSS = os.path.join(STATIC_SRC, "webclient", "apps_menu_home.scss")
APPS_MENU_XML = os.path.join(STATIC_SRC, "webclient", "apps_menu_home.xml")

BUNDLES = (BACKEND_BUNDLE, DARK_BUNDLE)

# --- element models -------------------------------------------------------------------------
# navbar.xml:4-8 - <header class="o_navbar"> > <nav class="o_main_navbar d-print-none"> >
# <div class="o_navbar_apps_menu"> > our repurposed button (apps_menu_home.xml).
NAVBAR_ANCESTORS = frozenset({"o_web_client", "o_navbar", "o_main_navbar", "o_navbar_apps_menu"})
APPS_BUTTON_HOOK = "o_viin_apps_home"
NAVBAR = {
    "classes": frozenset({"o_main_navbar", "d-print-none"}),
    "ancestors": frozenset({"o_web_client", "o_navbar"}),
    "prev_sibling": frozenset(),
}
# button_box.xml:5 + form_compiler.js:157-164, transcribed the same way viin_brand_web does.
BUTTONBOX = {
    "classes": frozenset({
        "o-form-buttonbox", "d-print-none", "position-relative", "d-flex", "w-md-auto",
        "o_not_full",
    }),
    "ancestors": BUTTONBOX_ANCESTORS,
    "prev_sibling": frozenset(),
}
STAT_BUTTON = {
    "classes": frozenset({
        "oe_stat_button", "btn", "btn-outline-secondary", "flex-grow-1", "flex-lg-grow-0",
    }),
    "ancestors": BUTTONBOX_ANCESTORS | {"o-form-buttonbox"},
    "prev_sibling": frozenset(),
}
# The icon is the first child of the stat button; the label is the first child of .o_stat_info
# (button_box renders text then value - which is why viin_brand_web models .o_stat_text as the
# VALUE's previous sibling).
STAT_ICON = {
    "classes": frozenset({"o_button_icon"}),
    "ancestors": STAT_BUTTON_ANCESTORS,
    "prev_sibling": frozenset(),
}
STAT_LABEL = {
    "classes": frozenset({"o_stat_text"}),
    "ancestors": STAT_BUTTON_ANCESTORS,
    "prev_sibling": frozenset(),
}

# --- source-scan vocabulary -----------------------------------------------------------------
# The core hooks the theme must not mention in its OWN production assets, grouped by the owner
# decision each group belongs to so a failure explains itself. `clip-path` is in the statusbar group
# because that property IS the arrow geometry - the stepper's `clip-path: none` is what squared the
# steps - and the theme has no other legitimate use for it.
FORBIDDEN_SOURCE_TOKENS = {
    "core's ARROW statusbar (owner 2026-08-03: keep Odoo CE's chevrons on the form header)": (
        "o_statusbar_status", "o_arrow_button", "o_viin_stepper", "o_viin_step",
        "StatusBarField", "StatusBarDurationField", "statusbar_duration", "clip-path",
    ),
    "core's STAT BUTTON layout (owner 2026-08-03: keep Odoo CE's button box)": (
        "oe_stat_button", "o-form-buttonbox", "o_button_icon", "o_stat_text", "o_stat_value",
        "o-stat-text-color", "o-stat-button-color",
    ),
}
SCANNED_SUFFIXES = (".scss", ".css", ".js", ".xml")

# A `color:` declaration, but never `background-color:` / `border-color:` / `--o-...-color:`: the
# character before "color" must not be part of a longer property name.
_COLOUR_DECLARATION_RE = re.compile(r"(?:^|[;{\s])color\s*:", re.MULTILINE)
# Bootstrap/Odoo text-colour utilities. `text-reset` (color: inherit !important) is the one that
# actually turned the icon black, but every member of the family is a colour override.
_TEXT_COLOUR_UTILITY_RE = re.compile(
    r"\btext-(reset|body|muted|black|white|dark|light|primary|secondary|success|info|warning|"
    r"danger|\d{2,3})\b"
)
_SCSS_LINE_COMMENT_RE = re.compile(r"//[^\n]*")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _strip_comments(text, filename):
    """Drop comments so a rule is never matched inside prose (these files document heavily)."""
    text = _BLOCK_COMMENT_RE.sub("", text)
    if filename.endswith(".xml"):
        return _XML_COMMENT_RE.sub("", text)
    return _SCSS_LINE_COMMENT_RE.sub("", text)


def _apps_button_classes():
    """The class set the apps-menu button ACTUALLY carries, read from apps_menu_home.xml.

    Deliberately NOT hardcoded. An element model written by hand describes the markup the author
    BELIEVED was there, and the cascade resolver happily answers for it whether or not the template
    agrees - which makes the compiled colour guard vacuous exactly when it matters. (Proven, not
    hypothetical: with a hardcoded {o_nav_entry, o_viin_apps_home} the guard stayed GREEN against a
    deliberately re-broken template carrying `btn ... text-reset` and no o_nav_entry at all, because
    it kept resolving core's .o_nav_entry rule for an element that no longer had the class.) Reading
    the real class list means the resolution follows the template: drop `o_nav_entry` and the button
    matches no navbar-entry rule; add `text-reset` back and `color: inherit !important` wins. Either
    way the guard goes red.

    Returns None when the button cannot be located, so the caller can fail with a clear message
    instead of silently asserting about an empty element.

    Read with a regex rather than an XML parser: the class attribute is all that is needed, the rest
    of this file already scans these sources textually, and it keeps the test free of both a
    defusedxml dependency and stdlib-parser exposure."""
    markup = _read(APPS_MENU_XML)
    for tag in re.finditer(r"<button\b[^>]*>", markup):
        class_attr = re.search(r'\bclass\s*=\s*"([^"]*)"', tag.group(0))
        classes = frozenset((class_attr.group(1) if class_attr else "").split())
        if APPS_BUTTON_HOOK in classes:
            return classes
    return None


def _is_zero_border(value):
    """Whether a compiled `border` / `border-width` value paints nothing."""
    if value is None:
        return True
    normalised = re.sub(r"\s+", " ", value.strip().lower()).rstrip(";")
    return normalised in {"0", "0px", "none", "0 none", "medium none", "0 solid transparent"}


@tagged("post_install", "-at_install")
class TestCoreChromeIsUntouched(TransactionCase):
    """Core's statusbar, navbar apps icon and stat button render as Odoo CE ships them."""

    def _compiled_css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so none of these surfaces can be "
            "verified." % bundle_name,
        )
        return css

    # --- 1. the arrow statusbar ---------------------------------------------------------------

    def test_statusbar_steps_keep_cores_arrow_geometry(self):
        """A statusbar step must still be clipped into core's chevron - never squared off.

        Core builds the arrow purely with `clip-path: polygon(...)` on
        `.o_field_statusbar > .o_statusbar_status > .o_arrow_button:not(.d-none)`
        (web/static/src/views/fields/statusbar/statusbar_field.scss:35-48) plus a matching ::before
        notch. The D6 stepper's very first declaration was `clip-path: none`, which is precisely and
        only how a chevron becomes the rectangle the owner reported - so the two halves of this test
        are the complete behaviour: the polygon is still compiled, and nothing anywhere unsets it.

        Asserted on the RAW compiled rules rather than through the cascade resolver on purpose: a
        `clip-path: none` reaching an arrow button by ANY selector shape (an @media arm, a widget
        wrapper this file does not model, a future class of ours) is a regression, and a raw scan
        cannot miss one by failing to model its selector.

        WOULD FAIL IF REVERTED: restoring statusbar_field.scss re-adds
        `.o_statusbar_status.o_viin_stepper > .o_arrow_button:not(.d-none) { clip-path: none }`,
        which this reports by selector, in whichever bundle it lands."""
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)
            polygons, unset = [], []
            for _order, selector, body in _iter_rules(css):
                if "o_arrow_button" not in selector:
                    continue
                for value, _important in _declarations(body, {"clip-path"}):
                    if value.strip().lower() == "none":
                        unset.append("%s { clip-path: %s }" % (selector, value.strip()))
                    elif "polygon(" in value.lower():
                        polygons.append(selector)
            self.assertFalse(
                unset,
                "A statusbar step is having core's arrow clip-path UNSET in %s, which renders it as "
                "a rectangle instead of a chevron - the exact regression the owner reverted on "
                "2026-08-03:\n  %s" % (bundle_name, "\n  ".join(unset)),
            )
            self.assertTrue(
                polygons,
                "No compiled rule in %s clips `.o_arrow_button` into a polygon, so the form-header "
                "statusbar no longer renders Odoo CE's chevron steps at all. Core builds the arrow "
                "with clip-path (web/static/src/views/fields/statusbar/statusbar_field.scss) - if "
                "core changed lever, re-ground this guard rather than deleting it." % bundle_name,
            )

    # --- 2. the navbar apps icon --------------------------------------------------------------

    def test_navbar_apps_icon_computes_cores_navbar_entry_colour(self):
        """The repurposed apps button must compute core's navbar-entry colour - i.e. white.

        ROOT CAUSE OF THE BLACK ICON, restated as the thing this measures. Core paints every navbar
        entry from `%-main-navbar-entry-base`, whose `o-hover-text-color()` emits
        `color: var(--NavBar-entry-color, #{$o-navbar-entry-color})`
        (web/static/src/webclient/navbar/navbar.variables.scss:34-50). Nothing in the addons path
        declares --NavBar-entry-color, so the Sass fallback wins - and viin_brand_web pins
        `$o-navbar-entry-color: #FFFFFF`. Replacing core's <Dropdown> dropped the `dropdown-toggle`
        class that selects that rule, and the `text-reset` we substituted resolved `inherit` up to
        the body colour. Giving the button core's own `o_nav_entry` class puts it back on that rule.

        THE EXPECTED VALUE IS READ FROM THE TOKEN SSOT, not literalised: if the brand ever re-tints
        the navbar entry, this guard follows it instead of going stale. Both bundles are checked -
        the navbar chrome is scheme-invariant teal, so 'white in light only' would be a bug.

        THE ELEMENT IS READ FROM THE TEMPLATE, not hardcoded - see _apps_button_classes() for why
        that distinction is load-bearing here (a hardcoded model kept this guard green against a
        deliberately re-broken template).

        RED BEFORE GREEN: with `text-reset` back on the button the winning declaration is
        `color: inherit !important`, which carries no colour - the resolution below returns None and
        this fails on the 'nothing resolvable' assertion before it ever reaches the comparison."""
        button_classes = _apps_button_classes()
        self.assertIsNotNone(
            button_classes,
            "No <button> carrying `%s` was found in apps_menu_home.xml, so this guard has no "
            "element to resolve and would pass vacuously. The apps-menu repurpose changed shape - "
            "re-ground the guard on the new markup." % APPS_BUTTON_HOOK,
        )
        apps_button = {
            "classes": button_classes,
            "ancestors": NAVBAR_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        expected = _resolve_scss_hex(_read(BRAND_VARIABLES_SCSS), "$o-navbar-entry-color")
        self.assertIsNotNone(
            expected,
            "$o-navbar-entry-color must be declared in viin_brand_web's brand_variables.scss - "
            "it is the SSOT this guard reads the expected navbar-entry colour from.",
        )
        expected = expected.lower()

        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)
            raw = _computed_value(css, [apps_button, NAVBAR], ("color",))
            self.assertIsNotNone(
                raw,
                "No compiled `color` applies to the navbar apps button (.o_viin_apps_home) in %s. "
                "It carries none of core's navbar-entry classes, so nothing paints it and it falls "
                "back to the inherited body colour - BLACK on the teal navbar." % bundle_name,
            )
            colour = _normalize_colour(raw)
            self.assertIsNotNone(
                colour,
                "The navbar apps button resolves `color` to %r in %s, which carries no colour. "
                "`inherit` here is the signature of a `text-reset` (or any `color: inherit`) "
                "override of ours: it walks past .o_navbar_apps_menu and .o_main_navbar, neither of "
                "which declares a colour, and lands on the body colour." % (raw, bundle_name),
            )
            self.assertEqual(
                colour, expected,
                "The navbar apps icon compiles %s in %s instead of core's navbar-entry colour %s. "
                "The button must carry core's `o_nav_entry` class and NO colour of ours - see "
                "apps_menu_home.xml." % (colour, bundle_name, expected),
            )
            # The icon is a graphic, so WCAG SC 1.4.11 (3:1) is the applicable floor; white on the
            # #007F8E navbar measures 4.74:1 and clears it comfortably.
            ratio = _contrast_ratio(colour, CHROME_BASE)
            self.assertGreaterEqual(
                ratio, WCAG_NON_TEXT_MIN,
                "The navbar apps icon renders %s on the teal navbar %s in %s - %.2f:1, below the "
                "WCAG non-text threshold of %.1f:1."
                % (colour, CHROME_BASE, bundle_name, ratio, WCAG_NON_TEXT_MIN),
            )

    # --- 3. the stat button -------------------------------------------------------------------

    def test_stat_button_renders_cores_default_layout(self):
        """A stat button must be core's: bordered box, icon left, normal-case label above the value.

        Each assertion is ONE defect from the owner's 'current (broken)' screenshot, expressed as a
        property the theme must not declare, so a partial re-introduction still fails:
          * the icon has no background and no fixed box -> no teal swatch around the glyph;
          * the label declares no text-transform -> 'Invoices', not 'INVOICES';
          * the button box declares no border-bottom -> no stray hairline rule under the strip;
          * the button's own border is not zeroed -> the bordered box the owner wants is back.
        Together with the absence of the gap/flex reflow (the source scan below), that is the whole
        difference between the two screenshots.

        WHAT IS DELIBERATELY NOT ASSERTED HERE: the Viindoo purple stat TEXT. It survives the revert
        and belongs to viin_brand_web (--o-stat-text-color, light-only), which guards it in
        test_brand_secondary_text_clears_wcag_aa_on_light_and_dark_surfaces. Duplicating it here
        would fork the SSOT."""
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)

            for element, props, description in (
                (STAT_ICON, ("background-color", "background"),
                 "the stat-button ICON is given a background - the teal swatch that boxed the glyph"),
                (STAT_ICON, ("width", "height"),
                 "the stat-button ICON is given a fixed box size - core sizes it by font-size alone"),
                (STAT_LABEL, ("text-transform",),
                 "the stat-button LABEL is case-transformed - the owner wants 'Invoices', not "
                 "'INVOICES'"),
                (BUTTONBOX, ("border-bottom", "border-bottom-width"),
                 "the stat strip declares a bottom border - the stray horizontal rule the owner "
                 "flagged"),
                (BUTTONBOX, ("gap",),
                 "the stat strip declares a gap - core overlaps the chips by a negative border "
                 "width instead, and the gap is part of what pushed the label out of the button"),
            ):
                value = _winning_declaration(css, element, props)
                self.assertIsNone(
                    value,
                    "In %s, %s (`%s: %s`). Odoo CE declares none of these on this element - delete "
                    "the rule that does rather than re-tuning it (owner revert 2026-08-03)."
                    % (bundle_name, description, "/".join(props), value),
                )

            border = _winning_declaration(css, STAT_BUTTON, ("border", "border-width"))
            self.assertFalse(
                _is_zero_border(border),
                "In %s the stat button's border compiles to %r, i.e. no border at all. Core renders "
                "a stat button as `btn btn-outline-secondary` inside a bordered box, which is the "
                "layout the owner asked to have back; the reverted D7 reskin zeroed it."
                % (bundle_name, border),
            )


class TestThemeAuthorsNoCoreChromeOverride(BaseCase):
    """Static source guards - the theme's OWN assets must not reach for these core hooks at all.

    No DB needed. These are the other half of the compiled guards above: they catch a re-introduced
    override whose selector the cascade resolver cannot model (an @media-only arm, an exotic
    selector), and they fail with a file and line rather than with a colour.
    """

    def _authored_sources(self):
        for root, _dirs, files in os.walk(STATIC_SRC):
            for filename in sorted(files):
                if filename.endswith(SCANNED_SUFFIXES):
                    yield os.path.join(root, filename), filename

    def test_the_theme_mentions_no_reverted_core_widget_hook(self):
        """No production asset of the theme references core's statusbar or stat-button internals.

        Both restyles were deleted whole on 2026-08-03 rather than re-tuned, so the honest guard is
        that the hooks are simply not spoken of again: any `.o_arrow_button` rule, any
        `StatusBarField` patch, any `.o_button_icon` / `.o_stat_text` declaration is a new attempt at
        the same thing. Comments are stripped first - this cluster documents its decisions in prose
        that legitimately names the removed hooks (this file included).

        SCOPE IS static/src ONLY - production assets. A future tour may legitimately use
        `.oe_stat_button` as a trigger without restyling anything, so static/tests is out of scope.

        RED BEFORE GREEN: re-adding views/form/button_box/button_box.scss or
        views/fields/statusbar/statusbar_field.scss names the file, the line and the token."""
        offenders = []
        for path, filename in self._authored_sources():
            stripped = _strip_comments(_read(path), filename)
            for decision, tokens in FORBIDDEN_SOURCE_TOKENS.items():
                for token in tokens:
                    for match in re.finditer(re.escape(token), stripped):
                        line = stripped.count("\n", 0, match.start()) + 1
                        offenders.append(
                            "%s (near line %d of the comment-stripped file): %r - reverted with %s"
                            % (os.path.relpath(path, MODULE_DIR), line, token, decision)
                        )
        self.assertFalse(
            offenders,
            "The theme is reaching back into core widget internals it was told to leave alone; %d "
            "reference(s):\n  %s\n\nDelete the rule - do not re-tune it. If Odoo core genuinely "
            "moves one of these hooks and the theme must follow, change the token list here in the "
            "same commit and say why." % (len(offenders), "\n  ".join(offenders)),
        )

    def test_the_theme_declares_no_colour_for_the_navbar_apps_icon(self):
        """The apps-menu button carries no colour of ours - core's navbar cascade paints it white.

        Two authored surfaces could re-blacken it and both are checked: a `color` declaration in
        apps_menu_home.scss, and a Bootstrap text-colour utility on the button markup. `text-reset`
        is the specific one that caused the bug (`color: inherit !important`, which resolves to the
        body colour because no navbar ancestor declares a colour), but the whole `text-*` family is
        an override and none of them belongs here.

        The compiled companion (test_navbar_apps_icon_computes_cores_navbar_entry_colour) proves the
        icon ends up white; this proves it does so for the right REASON - by not being overridden -
        which is literally what the owner asked for ('khong override gi de no trang nhu cu')."""
        scss = _strip_comments(_read(APPS_MENU_SCSS), "apps_menu_home.scss")
        declarations = _COLOUR_DECLARATION_RE.findall(scss)
        self.assertFalse(
            declarations,
            "apps_menu_home.scss declares a `color` (%d occurrence(s)). This file must stay "
            "colour-free: the apps icon is painted by core's `.o_main_navbar .o_nav_entry` rule "
            "(navbar.variables.scss %%-main-navbar-entry-base), and every colour authored here has "
            "so far ended up overriding that with the body colour - black on the teal navbar."
            % len(declarations),
        )

        markup = _strip_comments(_read(APPS_MENU_XML), "apps_menu_home.xml")
        utilities = sorted(set(_TEXT_COLOUR_UTILITY_RE.findall(markup)))
        self.assertFalse(
            utilities,
            "apps_menu_home.xml puts the text-colour utilit(y/ies) %s on the apps-menu markup. "
            "`text-reset` is what made the icon BLACK (it forces `color: inherit`, and no navbar "
            "ancestor declares a colour, so it lands on the body colour). Let core's navbar entry "
            "rule paint it instead - the button carries `o_nav_entry` for exactly that."
            % ", ".join("text-%s" % name for name in utilities),
        )
