# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# The five semantic fills (primary, success, info, warning, danger) and the labels that sit on them
# are the same in the light and the dark backend bundle, clear WCAG AA (4.5:1) with their label,
# and come from the one rule core already has: color-contrast() with the brand dark label. Bootstrap's
# `$purple` is the Viindoo purple in the backend only. Every expected value is a literal of the
# design (fill, label), and every ratio is the W3C formula of test_brand_cascade_compile.py; the
# compiled CSS is read, because the colours reach the pixel through bundle-specific compiles.
import re

from odoo.tests.common import TransactionCase, tagged

from .test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BODY_BG,
    DARK_BUNDLE,
    UTILITY_ANCESTORS,
    WCAG_AA_NORMAL_TEXT,
    WHITE,
    _COMMENT_RE,
    _contrast_ratio,
    _iter_rules,
    _declarations,
    _normalize_colour,
    _winning_declaration,
)
from .test_dark_gray_ramp_compile import _last_value, _root_value

FRONTEND_BUNDLE = "web.assets_frontend"

# colour name -> (fill, label on that fill)
SEMANTIC_PAIRS = {
    "primary": ("#007f8e", "#ffffff"),
    "success": ("#00884d", "#ffffff"),
    "info": ("#007dbc", "#ffffff"),
    "warning": ("#ffcc32", "#21272b"),
    "danger": ("#ca4c4c", "#ffffff"),
}
OUTLINE_COLOURS = ("primary", "success", "info", "warning", "danger")
LIGHT_PURPLE = "#7f4282"
DARK_PURPLE = "#bd83c0"
CORE_FRONTEND_PURPLE = "#6f42c1"


def _rgb_triplet_to_hex(triplet):
    channels = [int(part) for part in triplet.replace(",", " ").split()]
    return "#%02x%02x%02x" % tuple(channels)


@tagged("post_install", "-at_install")
class TestSemanticColourCompile(TransactionCase):

    def _css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(css.strip(), "%s compiled to empty CSS." % bundle_name)
        return _COMMENT_RE.sub("", css)

    def _element(self, *classes):
        return {
            "classes": frozenset(classes), "ancestors": UTILITY_ANCESTORS,
            "prev_sibling": frozenset(),
        }

    def _fill(self, css, name):
        triplet = _root_value(css, "%s-rgb" % name)
        self.assertIsNotNone(triplet, "No :root --%s-rgb is compiled." % name)
        return _rgb_triplet_to_hex(triplet)

    def test_semantic_fills_and_labels_follow_the_palette_in_both_schemes(self):
        """`.text-bg-<colour>` and `.btn-<colour>` render the palette fill with the palette label,
        in the light and in the dark bundle alike.

        WOULD FAIL IF REVERTED: any fill other than the palette's, or a black label on the warning
        fill, changes the pair."""
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._css(bundle_name)
            for name, (fill, label) in SEMANTIC_PAIRS.items():
                with self.subTest(arm=arm, colour=name):
                    self.assertEqual(self._fill(css, name), fill)
                    badge_label = _normalize_colour(
                        _winning_declaration(
                            css, self._element("badge", "text-bg-%s" % name), ("color",),
                        ) or ""
                    )
                    self.assertEqual(badge_label, label, ".text-bg-%s label" % name)
                    button_label = _normalize_colour(_last_value(css, ".btn-%s" % name, "--btn-color") or "")
                    button_fill = _normalize_colour(_last_value(css, ".btn-%s" % name, "--btn-bg") or "")
                    self.assertEqual((button_fill, button_label), (fill, label), ".btn-%s" % name)

    def test_buttons_clear_wcag_aa_at_rest_hover_and_active(self):
        """The label of a `.btn-<colour>` clears 4.5:1 against its fill in every state.

        WOULD FAIL IF REVERTED: a fill or a label of the palette that falls under AA, or a hover or
        active fill that is shaded against a fixed label, fails here."""
        pairs = (
            ("rest", "--btn-color", "--btn-bg"),
            ("hover", "--btn-hover-color", "--btn-hover-bg"),
            ("active", "--btn-active-color", "--btn-active-bg"),
        )
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._css(bundle_name)
            for name in SEMANTIC_PAIRS:
                for state, colour_prop, fill_prop in pairs:
                    with self.subTest(arm=arm, button=name, state=state):
                        label = _normalize_colour(_last_value(css, ".btn-%s" % name, colour_prop) or "")
                        fill = _normalize_colour(_last_value(css, ".btn-%s" % name, fill_prop) or "")
                        self.assertTrue(label and fill, ".btn-%s declares no %s pair" % (name, state))
                        ratio = _contrast_ratio(label, fill)
                        self.assertGreaterEqual(
                            ratio, WCAG_AA_NORMAL_TEXT,
                            ".btn-%s %s renders %s on %s = %.2f:1 in the %s bundle."
                            % (name, state, label, fill, ratio, arm),
                        )

    def test_no_semantic_label_is_pure_black(self):
        """No rule of the compiled bundles paints a `.text-bg-<colour>` label pure black: the dark
        label is the brand tone core's color-contrast() picks.

        WOULD FAIL IF REVERTED: dropping `$color-contrast-dark` from brand_variables.scss brings
        core's black back on the warning fill."""
        for bundle_name in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._css(bundle_name)
            for _order, selector, body in _iter_rules(css):
                if not any(selector == ".text-bg-%s" % name for name in SEMANTIC_PAIRS):
                    continue
                for value, _important in _declarations(body, ("color",)):
                    with self.subTest(bundle=bundle_name, selector=selector):
                        self.assertNotIn(
                            _normalize_colour(value), ("#000000", None),
                            "%s paints %r in %s." % (selector, value, bundle_name),
                        )

    def test_text_inside_a_semantic_fill_takes_the_label_of_the_fill(self):
        """Text in a `.bg-<colour>` element has the label of that fill, except when a
        `bg-opacity-*` class makes the fill translucent.

        WOULD FAIL IF REVERTED: without the rule in brand_cascade.scss the text keeps the colour it
        inherits; without the exception a translucent fill gets a white label on the page."""
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._css(bundle_name)
            for name, (_fill, label) in SEMANTIC_PAIRS.items():
                with self.subTest(arm=arm, colour=name):
                    solid = _normalize_colour(
                        _last_value(css, '.bg-%s:not([class*="bg-opacity-"])' % name, "color") or ""
                    )
                    self.assertEqual(solid, label)
                    unguarded = [
                        selector for _order, selector, body in _iter_rules(css)
                        if re.match(r"\.bg-%s(?![\w-])" % name, selector) and _declarations(body, ("color",))
                        and 'bg-opacity-' not in selector
                    ]
                    self.assertEqual(unguarded, [], ".bg-%s sets a text colour on a translucent fill" % name)

    def test_outline_buttons_clear_wcag_aa_on_the_dark_page(self):
        """The resting label and border of `.btn-outline-<colour>` read on the dark page at 4.5:1.

        WOULD FAIL IF REVERTED: without the entries of dark_buttons.scss the outline takes the
        palette fill as its label, 3.86:1 for success, 3.89:1 for info, 3.88:1 for danger."""
        css = self._css(DARK_BUNDLE)
        for name in OUTLINE_COLOURS:
            for prop in ("--btn-color", "--btn-border-color"):
                with self.subTest(colour=name, prop=prop):
                    colour = _normalize_colour(_last_value(css, ".btn-outline-%s" % name, prop) or "")
                    self.assertIsNotNone(colour, ".btn-outline-%s declares no %s" % (name, prop))
                    ratio = _contrast_ratio(colour, DARK_BODY_BG)
                    self.assertGreaterEqual(
                        ratio, WCAG_AA_NORMAL_TEXT,
                        ".btn-outline-%s %s is %s = %.2f:1 on %s." % (name, prop, colour, ratio, DARK_BODY_BG),
                    )
        for name, (fill, label) in SEMANTIC_PAIRS.items():
            if name == "primary":
                continue
            with self.subTest(colour=name, state="hover"):
                self.assertEqual(
                    (
                        _normalize_colour(_last_value(css, ".btn-outline-%s" % name, "--btn-hover-bg") or ""),
                        _normalize_colour(_last_value(css, ".btn-outline-%s" % name, "--btn-hover-color") or ""),
                    ),
                    (fill, label),
                )

    def test_purple_is_the_viindoo_purple_in_the_backend_only(self):
        """`--purple` is the Viindoo purple in the light backend, the lightened purple in the dark
        backend and Bootstrap's own in the frontend.

        WOULD FAIL IF REVERTED: dropping backend_variables.scss leaves Bootstrap's #6f42c1 in the
        backend; dropping the `$purple` of dark_palette.scss leaves the light purple, 2.5:1 on the
        dark page, in the dark bundle; assigning `$purple` in a frontend bundle changes the
        website of a customer."""
        expectations = (
            ("light", BACKEND_BUNDLE, LIGHT_PURPLE),
            ("dark", DARK_BUNDLE, DARK_PURPLE),
        )
        for arm, bundle_name, expected in expectations:
            with self.subTest(arm=arm):
                self.assertEqual(_normalize_colour(_root_value(self._css(bundle_name), "purple") or ""), expected)
        frontend = _normalize_colour(_root_value(self._css(FRONTEND_BUNDLE), "purple") or "")
        self.assertIn(frontend, (None, CORE_FRONTEND_PURPLE))
        self.assertGreaterEqual(_contrast_ratio(DARK_PURPLE, DARK_BODY_BG), WCAG_AA_NORMAL_TEXT)
        self.assertGreaterEqual(_contrast_ratio(LIGHT_PURPLE, WHITE), WCAG_AA_NORMAL_TEXT)
