import os
import re

from odoo.tests.common import BaseCase, TransactionCase, tagged

from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
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
from odoo.addons.viin_brand.tests.test_brand_ssot import (
    BRAND_VARIABLES_SCSS,
    _resolve_scss_hex,
)

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_SRC = os.path.join(MODULE_DIR, "static", "src")
APPS_MENU_SCSS = os.path.join(STATIC_SRC, "webclient", "apps_menu_home.scss")
APPS_MENU_XML = os.path.join(STATIC_SRC, "webclient", "apps_menu_home.xml")

BUNDLES = (BACKEND_BUNDLE, DARK_BUNDLE)

# Element models, transcribed from the templates: the navbar is
# `<header class="o_navbar"> > <nav class="o_main_navbar d-print-none"> > <div class="o_navbar_apps_menu">`
# > the repurposed apps button (apps_menu_home.xml).
NAVBAR_ANCESTORS = frozenset({"o_web_client", "o_navbar", "o_main_navbar", "o_navbar_apps_menu"})
APPS_BUTTON_HOOK = "o_viin_apps_home"
NAVBAR = {
    "classes": frozenset({"o_main_navbar", "d-print-none"}),
    "ancestors": frozenset({"o_web_client", "o_navbar"}),
    "prev_sibling": frozenset(),
}
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
# (button_box renders text then value, so the label is the value's previous sibling).
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

# The core hooks the theme must not mention in its own production assets. `clip-path` is listed with
# the statusbar because that property IS the arrow geometry and the theme has no other use for it.
FORBIDDEN_SOURCE_TOKENS = {
    "core's arrow statusbar": (
        "o_statusbar_status", "o_arrow_button", "o_viin_stepper", "o_viin_step",
        "StatusBarField", "StatusBarDurationField", "statusbar_duration", "clip-path",
    ),
    "core's stat button layout": (
        "oe_stat_button", "o-form-buttonbox", "o_button_icon", "o_stat_text", "o_stat_value",
        "o-stat-text-color", "o-stat-button-color",
    ),
}

_SCSS_LINE_COMMENT_RE = re.compile(r"//[^\n]*")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_XML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _strip_comments(text, filename):
    """Drop comments so a rule is never matched inside prose."""
    text = _BLOCK_COMMENT_RE.sub("", text)
    if filename.endswith(".xml"):
        return _XML_COMMENT_RE.sub("", text)
    return _SCSS_LINE_COMMENT_RE.sub("", text)


def _apps_button_classes():
    """Read the class set the apps-menu button carries from apps_menu_home.xml.

    The element model follows the template instead of a hardcoded class list: a hand-written model
    keeps resolving core's navbar-entry rule for a button without the class, which makes
    the compiled colour guard vacuous.

    :return: the button's classes, or ``None`` when the button cannot be located
    """
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
    """Core's statusbar, navbar apps icon and stat button render as Odoo CE ships them.

    The theme adds what Odoo CE lacks and does not restyle these widgets, so each guard asserts an
    absence plus the core behaviour that absence preserves. The cascade helpers are reused from
    viin_brand.
    """

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

    def test_statusbar_steps_keep_cores_arrow_geometry(self):
        """A statusbar step is still clipped into core's chevron, never squared off.

        Core builds the arrow with ``clip-path: polygon(...)`` on
        ``.o_field_statusbar > .o_statusbar_status > .o_arrow_button:not(.d-none)``, so the polygon
        must still be compiled and nothing may unset it. The colour of the current arrow belongs to
        viin_brand.

        The raw compiled rules are scanned instead of resolving the cascade: a ``clip-path: none``
        reaching an arrow button by any selector shape is a regression, and a raw scan cannot miss
        one by failing to model its selector.
        """
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
                "a rectangle instead of a chevron:\n  %s" % (bundle_name, "\n  ".join(unset)),
            )
            self.assertTrue(
                polygons,
                "No compiled rule in %s clips `.o_arrow_button` into a polygon, so the form-header "
                "statusbar does not render Odoo CE's chevron steps at all. Core builds the arrow "
                "with clip-path (web/static/src/views/fields/statusbar/statusbar_field.scss) - if "
                "core changed lever, re-ground this guard rather than deleting it." % bundle_name,
            )

    def test_navbar_apps_icon_computes_cores_navbar_entry_colour(self):
        """The repurposed apps button computes core's navbar-entry colour, i.e. white.

        Core paints every navbar entry from ``%-main-navbar-entry-base``, whose
        ``o-hover-text-color()`` emits ``color: var(--NavBar-entry-color, #{$o-navbar-entry-color})``
        (web/static/src/webclient/navbar/navbar.variables.scss). No rule that reaches the regular
        navbar declares ``--NavBar-entry-color``, so the Sass fallback wins, and viin_brand pins
        ``$o-navbar-entry-color: #FFFFFF``. The button carries core's ``o_nav_entry`` class to stay
        on that rule; a ``text-reset`` (``color: inherit !important``) would resolve up to the body
        colour and render black on the navbar.

        The expected value is read from the token SSOT and both bundles are checked, because the
        navbar chrome is scheme-invariant. The element is read from the template, see
        ``_apps_button_classes``.
        """
        button_classes = _apps_button_classes()
        self.assertIsNotNone(
            button_classes,
            "No <button> carrying `%s` was found in apps_menu_home.xml, so this guard has no "
            "element to resolve and would pass vacuously. The apps-menu markup changed shape - "
            "re-ground the guard on it." % APPS_BUTTON_HOOK,
        )
        apps_button = {
            "classes": button_classes,
            "ancestors": NAVBAR_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        expected = _resolve_scss_hex(_read(BRAND_VARIABLES_SCSS), "$o-navbar-entry-color")
        self.assertIsNotNone(
            expected,
            "$o-navbar-entry-color must be declared in viin_brand's brand_variables.scss - "
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
                "back to the inherited body colour - BLACK on the navbar." % bundle_name,
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
            # The icon is a graphic, so WCAG SC 1.4.11 (3:1) is the applicable floor.
            ratio = _contrast_ratio(colour, CHROME_BASE)
            self.assertGreaterEqual(
                ratio, WCAG_NON_TEXT_MIN,
                "The navbar apps icon renders %s on the navbar %s in %s - %.2f:1, below the "
                "WCAG non-text threshold of %.1f:1."
                % (colour, CHROME_BASE, bundle_name, ratio, WCAG_NON_TEXT_MIN),
            )

    def test_stat_button_renders_cores_default_layout(self):
        """A stat button is core's: bordered box, icon left, normal-case label above the value.

        Each assertion is one property the theme must not declare, so a partial re-introduction
        still fails:
          * the icon has no background and no fixed box - no swatch around the glyph;
          * the label declares no text-transform - 'Invoices', not 'INVOICES';
          * the button box declares no border-bottom and no gap - no stray rule, no reflow that
            pushes the label out of the button;
          * the button's own border is not zeroed - the bordered box stays.
        The purple stat text is not asserted here: it belongs to viin_brand (``--o-stat-text-color``,
        light-only), which guards it.
        """
        for bundle_name in BUNDLES:
            css = self._compiled_css(bundle_name)

            for element, props, description in (
                (STAT_ICON, ("background-color", "background"),
                 "the stat-button ICON is given a background - a swatch that boxes the glyph"),
                (STAT_ICON, ("width", "height"),
                 "the stat-button ICON is given a fixed box size - core sizes it by font-size alone"),
                (STAT_LABEL, ("text-transform",),
                 "the stat-button LABEL is case-transformed - it must read 'Invoices', not "
                 "'INVOICES'"),
                (BUTTONBOX, ("border-bottom", "border-bottom-width"),
                 "the stat strip declares a bottom border - a stray horizontal rule"),
                (BUTTONBOX, ("gap",),
                 "the stat strip declares a gap - core overlaps the chips by a negative border "
                 "width instead, and a gap pushes the label out of the button"),
            ):
                value = _winning_declaration(css, element, props)
                self.assertIsNone(
                    value,
                    "In %s, %s (`%s: %s`). Odoo CE declares none of these on this element - delete "
                    "the rule that does rather than re-tuning it."
                    % (bundle_name, description, "/".join(props), value),
                )

            border = _winning_declaration(css, STAT_BUTTON, ("border", "border-width"))
            self.assertFalse(
                _is_zero_border(border),
                "In %s the stat button's border compiles to %r, i.e. no border at all. Core renders "
                "a stat button as `btn btn-outline-secondary` inside a bordered box."
                % (bundle_name, border),
            )


class TestThemeAuthorsNoCoreChromeOverride(BaseCase):
    """Static source guards - the theme's own assets do not reach for these core hooks at all.

    No database is needed. They catch an override whose selector the cascade resolver cannot model
    (an ``@media``-only arm, an exotic selector) and fail with a file and line rather than a colour.
    """

    def _authored_sources(self):
        for root, _dirs, files in os.walk(STATIC_SRC):
            for filename in sorted(files):
                if filename.endswith((".scss", ".css", ".js", ".xml")):
                    yield os.path.join(root, filename), filename

    def test_the_theme_mentions_no_reverted_core_widget_hook(self):
        """No production asset of the theme references core's statusbar or stat-button internals.

        Any ``.o_arrow_button`` rule, ``StatusBarField`` patch or ``.o_button_icon`` /
        ``.o_stat_text`` declaration is an attempt to restyle those widgets again. Comments are
        stripped first. The scope is ``static/src`` only: a tour may use ``.oe_stat_button`` as a
        trigger without restyling anything.
        """
        offenders = []
        for path, filename in self._authored_sources():
            stripped = _strip_comments(_read(path), filename)
            for decision, tokens in FORBIDDEN_SOURCE_TOKENS.items():
                for token in tokens:
                    for match in re.finditer(re.escape(token), stripped):
                        line = stripped.count("\n", 0, match.start()) + 1
                        offenders.append(
                            "%s (near line %d of the comment-stripped file): %r - a hook of %s"
                            % (os.path.relpath(path, MODULE_DIR), line, token, decision)
                        )
        self.assertFalse(
            offenders,
            "The theme is reaching back into core widget internals it must leave alone; %d "
            "reference(s):\n  %s\n\nDelete the rule - do not re-tune it. If Odoo core genuinely "
            "moves one of these hooks and the theme must follow, change the token list here in the "
            "same commit and say why." % (len(offenders), "\n  ".join(offenders)),
        )

    def test_the_theme_declares_no_colour_for_the_navbar_apps_icon(self):
        """The apps-menu button carries no colour of ours - core's navbar cascade paints it white.

        Two authored surfaces could turn it black and both are checked: a ``color`` declaration in
        apps_menu_home.scss, and a Bootstrap text-colour utility on the button markup (``text-reset``
        forces ``color: inherit``, which lands on the body colour because no navbar ancestor declares
        one). The compiled companion test proves the icon ends up white; this one proves it is so
        because nothing overrides it.
        """
        # A `color:` declaration, never `background-color:` / `border-color:` / `--o-...-color:`:
        # the character before "color" must not be part of a longer property name.
        colour_declaration_re = re.compile(r"(?:^|[;{\s])color\s*:", re.MULTILINE)
        text_colour_utility_re = re.compile(
            r"\btext-(reset|body|muted|black|white|dark|light|primary|secondary|success|info|warning|"
            r"danger|\d{2,3})\b"
        )
        scss = _strip_comments(_read(APPS_MENU_SCSS), "apps_menu_home.scss")
        declarations = colour_declaration_re.findall(scss)
        self.assertFalse(
            declarations,
            "apps_menu_home.scss declares a `color` (%d occurrence(s)). This file must stay "
            "colour-free: the apps icon is painted by core's `.o_main_navbar .o_nav_entry` rule "
            "(navbar.variables.scss %%-main-navbar-entry-base), and a colour authored here "
            "overrides that with the body colour - black on the navbar." % len(declarations),
        )

        markup = _strip_comments(_read(APPS_MENU_XML), "apps_menu_home.xml")
        utilities = sorted(set(text_colour_utility_re.findall(markup)))
        self.assertFalse(
            utilities,
            "apps_menu_home.xml puts the text-colour utilit(y/ies) %s on the apps-menu markup. "
            "`text-reset` makes the icon BLACK (it forces `color: inherit`, and no navbar "
            "ancestor declares a colour, so it lands on the body colour). Let core's navbar entry "
            "rule paint it instead - the button carries `o_nav_entry` for exactly that."
            % ", ".join("text-%s" % name for name in utilities),
        )
