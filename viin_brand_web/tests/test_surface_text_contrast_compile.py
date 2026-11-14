# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# WHAT IS PROTECTED (behaviour, not code): the text a core screen renders on a core surface stays
# readable (WCAG 2.1 AA, 4.5:1 for normal text) once the theme is installed, in the scheme a user
# reads it in. Core tunes its contextual text colours (`text-info`, `text-danger`, `text-warning`,
# `text-success`, the muted tier) for the VIEW surface - white in light, the panel tier of the
# recompiled dark bundle - so the surfaces that host decorated rows and contextual text (a list
# cell, a kanban card, a dialog, a popover) must be that surface, never the app-shell grey; and the
# label of a brand semantic fill (a state pill, a danger or info button) must clear AA against the
# fill itself, in both schemes. In dark, the faded label of a read-only radio or checkbox must stay
# readable on the muted label tier of the mobile form.
#
# Every expected value is a literal transcribed from core or from the brand palette, and every
# contrast is the W3C WCAG 2.x formula owned by test_brand_cascade_compile.py; nothing is re-derived
# through a Sass mix() in Python. Compiled CSS, not source: the colours reach the pixel through
# bundle-specific compiles (the dark bundle recompiles the whole light bundle).
from odoo.tests.common import TransactionCase, tagged

from .test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    BLACK,
    DARK_BODY_BG,
    DARK_BUNDLE,
    DARK_MUTED_TIER,
    DARK_READABLE_TEXT,
    LIST_SURFACE_DARK,
    LIST_SURFACE_LIGHT,
    UTILITY_ANCESTORS,
    WCAG_AA_NORMAL_TEXT,
    WHITE,
    _COMMENT_RE,
    _composite_over,
    _computed_value,
    _contrast_ratio,
    _declarations,
    _iter_rules,
    _normalize_colour,
    _winning_declaration,
)
from .test_dark_gray_ramp_compile import _last_value, _root_value

# The contextual text utilities core tunes for a white page ($o-theme-text-colors). The colour each
# one renders is read from the compiled bundle, so a change of that map shows up here.
CONTEXTUAL_TEXT_CLASSES = ("text-info", "text-danger", "text-warning", "text-success")
# The theme semantic fills a state pill or a button can carry (the live `--<name>-rgb` triplets of
# the compiled :root decide the actual fill; the names are what core's templates put in the class).
SEMANTIC_FILLS = ("primary", "success", "info", "warning", "danger")
# Fills whose white label core's color-contrast() accepts at its lowered 3:1 floor but which sit
# under AA: the label is re-chosen for exactly these.
FILLS_WITH_RE_CHOSEN_LABEL = ("info", "danger")

LIST_TABLE = ".o_list_renderer .o_list_table"
KANBAN_CARD = ".o_kanban_record:not(.o_kanban_ghost)"
POPOVER = ".o_popover"
MODAL = ".o_dialog .modal-content"


def _surface(value):
    """The #rrggbb a compiled surface value resolves to (core spells white as the keyword)."""
    if value is None:
        return None
    if value.strip().lower() == "white":
        return WHITE
    return _normalize_colour(value)


def _rgb_triplet_to_hex(triplet):
    channels = [int(part) for part in triplet.replace(",", " ").split()]
    return "#%02x%02x%02x" % tuple(channels)


@tagged("post_install", "-at_install")
class TestSurfaceTextContrastCompile(TransactionCase):
    """Surfaces that host core text are the view surface; semantic fills carry an AA label; the
    dark faded label stays readable."""

    def _css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(css.strip(), "%s compiled to empty CSS." % bundle_name)
        return _COMMENT_RE.sub("", css)

    # ------------------------------------------------------------------------------------------
    # Surfaces that host core text
    # ------------------------------------------------------------------------------------------
    def _assert_contextual_text_clears_aa(self, css, surface, label):
        """Every contextual text utility, as the bundle compiles it, clears AA on ``surface``."""
        for text_class in CONTEXTUAL_TEXT_CLASSES:
            raw = _computed_value(css, [self._element(text_class)], ("color",))
            colour = _normalize_colour(raw or "")
            self.assertIsNotNone(colour, "`.%s` compiles no colour (%r)." % (text_class, raw))
            ratio = _contrast_ratio(colour, surface)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "`.%s` (%s) on %s %s is %.2f:1, below WCAG AA %.1f:1."
                % (text_class, colour, label, surface, ratio, WCAG_AA_NORMAL_TEXT),
            )

    def test_list_cell_surface_is_the_view_surface_in_both_schemes(self):
        """The cell surface of a list is the view surface (white in light, the panel tier in dark),
        never the app-shell grey: the decoration colours of a row (text-info, text-danger,
        text-warning, text-success) are tuned for white and fall under 4.5:1 on #F8F9FA.

        WOULD FAIL IF REVERTED: re-pointing `--table-bg` at `var(--body-bg)` on `.o_list_renderer
        .o_list_table` replaces core's `white` with a var() that resolves to #F8F9FA in light."""
        for arm, bundle_name, expected in (
            ("light", BACKEND_BUNDLE, LIST_SURFACE_LIGHT),
            ("dark", DARK_BUNDLE, LIST_SURFACE_DARK),
        ):
            with self.subTest(arm=arm):
                css = self._css(bundle_name)
                value = _last_value(css, LIST_TABLE, "--table-bg")
                self.assertEqual(
                    _surface(value), expected,
                    "The %s list cell surface (--table-bg on %s) is %r, expected the view surface "
                    "%s." % (arm, LIST_TABLE, value, expected),
                )
                self._assert_contextual_text_clears_aa(css, _surface(value), "the %s list cell" % arm)

    def test_kanban_card_surface_is_the_view_surface_in_both_schemes(self):
        """The surface of a kanban card is the view surface, so the deadline (text-danger), the
        muted footer and every contextual colour on it are read on white in light.

        WOULD FAIL IF REVERTED: a `background-color: var(--body-bg)` on the card hands the light
        card the app-shell grey #F8F9FA (and the same tier as the kanban canvas)."""
        for arm, bundle_name, expected in (
            ("light", BACKEND_BUNDLE, LIST_SURFACE_LIGHT),
            ("dark", DARK_BUNDLE, LIST_SURFACE_DARK),
        ):
            with self.subTest(arm=arm):
                css = self._css(bundle_name)
                value = _last_value(css, KANBAN_CARD, "background-color")
                self.assertEqual(
                    _surface(value), expected,
                    "The %s kanban card surface is %r, expected the view surface %s."
                    % (arm, value, expected),
                )
                self._assert_contextual_text_clears_aa(css, _surface(value), "the %s kanban card" % arm)

    def test_dialog_and_popover_surfaces_are_the_view_surface_in_both_schemes(self):
        """A dialog body and a popover body carry the same decorated and muted text as a list, so
        their surface is the view surface too: the modal keeps core's own `--modal-bg` (declared on
        `.modal`, not re-pointed on `.o_dialog .modal-content`), the popover is pointed at the view
        surface because core's `$popover-bg` is a literal white the dark bundle does not recompile.

        WOULD FAIL IF REVERTED: `--modal-bg: var(--body-bg)` on the modal content, or
        `--popover-bg: var(--body-bg)` on `.o_popover`, paints them #F8F9FA in light."""
        for arm, bundle_name, expected in (
            ("light", BACKEND_BUNDLE, LIST_SURFACE_LIGHT),
            ("dark", DARK_BUNDLE, LIST_SURFACE_DARK),
        ):
            css = self._css(bundle_name)
            with self.subTest(arm=arm, surface="modal"):
                value = _last_value(css, MODAL, "--modal-bg")
                self.assertIsNone(
                    value,
                    "The %s dialog declares --modal-bg %r on %s; the modal surface is core's own "
                    "($modal-content-bg = the view surface)." % (arm, value, MODAL),
                )
                core_surface = _last_value(css, ".modal", "--modal-bg")
                self.assertEqual(
                    _surface(core_surface), expected,
                    "The %s modal surface (--modal-bg on .modal) is %r, expected the view surface %s."
                    % (arm, core_surface, expected),
                )
                self._assert_contextual_text_clears_aa(css, expected, "the %s dialog" % arm)
            with self.subTest(arm=arm, surface="popover"):
                value = _last_value(css, POPOVER, "--popover-bg")
                self.assertEqual(
                    _surface(value), expected,
                    "The %s popover surface is %r, expected the view surface %s."
                    % (arm, value, expected),
                )
                self._assert_contextual_text_clears_aa(css, expected, "the %s popover" % arm)

    # ------------------------------------------------------------------------------------------
    # Label of a semantic fill
    # ------------------------------------------------------------------------------------------
    def _fill(self, css, name):
        triplet = _root_value(css, "%s-rgb" % name)
        self.assertIsNotNone(triplet, "No :root --%s-rgb is compiled." % name)
        return _rgb_triplet_to_hex(triplet)

    def _element(self, *classes):
        return {
            "classes": frozenset(classes), "ancestors": UTILITY_ANCESTORS,
            "prev_sibling": frozenset(),
        }

    def test_semantic_fill_badge_labels_clear_wcag_aa_in_both_schemes(self):
        """The label of every `.text-bg-<semantic colour>` pill clears 4.5:1 against its fill - the
        brand info blue and danger red included, where core's color-contrast() (lowered to a 3:1
        floor) picks a white label at 3.13:1 and 4.29:1.

        WOULD FAIL IF REVERTED: dropping the label rule from brand_cascade.scss hands `.text-bg-info`
        and `.text-bg-danger` core's #FFFFFF label."""
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._css(bundle_name)
            for name in SEMANTIC_FILLS:
                with self.subTest(arm=arm, fill=name):
                    fill = self._fill(css, name)
                    raw = _winning_declaration(
                        css, self._element("badge", "text-bg-%s" % name), ("color",),
                    )
                    label = _normalize_colour(raw or "")
                    self.assertIsNotNone(
                        label, "`.text-bg-%s` compiles no label colour in the %s bundle." % (name, arm),
                    )
                    ratio = _contrast_ratio(label, fill)
                    self.assertGreaterEqual(
                        ratio, WCAG_AA_NORMAL_TEXT,
                        "`.text-bg-%s` renders %s on %s = %.2f:1 in the %s bundle, below WCAG AA "
                        "%.1f:1." % (name, label, fill, ratio, arm, WCAG_AA_NORMAL_TEXT),
                    )
                    if name in FILLS_WITH_RE_CHOSEN_LABEL:
                        self.assertEqual(
                            label, BLACK,
                            "`.text-bg-%s` label is %s; white on %s is under AA, so the AA pair is "
                            "the black label." % (name, label, fill),
                        )

    def test_semantic_fill_button_labels_clear_wcag_aa_at_rest_hover_and_active(self):
        """A `.btn-<semantic colour>` label clears 4.5:1 against its fill at rest, on hover and
        when pressed; its hover and active fills derive from the re-chosen label, so a black label
        never lands on a shaded-darker fill.

        The re-emit is scoped to `:not(.btn-link)`: the bare `.btn-<colour>` rule keeps core's white
        label, so a link-styled button that carries the colour class is left to core.

        WOULD FAIL IF REVERTED: dropping the `button-variant()` re-emit leaves `.btn-danger` and
        `.btn-info` core's white label; dropping the hover or active label argument brings white back
        on the tinted fill (3.41:1 and 3.15:1 for the danger red); dropping `:not(.btn-link)` moves
        the black label onto the bare `.btn-<colour>` rule."""
        pairs = (
            ("rest", "--btn-color", "--btn-bg"),
            ("hover", "--btn-hover-color", "--btn-hover-bg"),
            ("active", "--btn-active-color", "--btn-active-bg"),
        )
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._css(bundle_name)
            for name in FILLS_WITH_RE_CHOSEN_LABEL:
                for state, colour_prop, fill_prop in pairs:
                    with self.subTest(arm=arm, button=name, state=state):
                        selector = ".btn-%s:not(.btn-link)" % name
                        label = _normalize_colour(_last_value(css, selector, colour_prop) or "")
                        fill = _normalize_colour(_last_value(css, selector, fill_prop) or "")
                        self.assertIsNotNone(
                            label, "%s declares no %s in the %s bundle." % (selector, colour_prop, arm),
                        )
                        self.assertIsNotNone(
                            fill, "%s declares no %s in the %s bundle." % (selector, fill_prop, arm),
                        )
                        ratio = _contrast_ratio(label, fill)
                        self.assertGreaterEqual(
                            ratio, WCAG_AA_NORMAL_TEXT,
                            "%s %s renders %s on %s = %.2f:1 in the %s bundle, below WCAG AA %.1f:1."
                            % (selector, state, label, fill, ratio, arm, WCAG_AA_NORMAL_TEXT),
                        )
            for name in FILLS_WITH_RE_CHOSEN_LABEL:
                with self.subTest(arm=arm, button=name, state="link-styled"):
                    bare = _last_value(css, ".btn-%s" % name, "--btn-color")
                    self.assertEqual(
                        _normalize_colour(bare or ""), WHITE,
                        "The bare `.btn-%s` rule declares --btn-color %r in the %s bundle: the "
                        "label re-emit must stay scoped to `:not(.btn-link)`, leaving what core "
                        "resolves for a link-styled button untouched." % (name, bare, arm),
                    )

    # ------------------------------------------------------------------------------------------
    # Dark: bare badge and faded labels
    # ------------------------------------------------------------------------------------------
    def test_default_badge_label_is_readable_on_the_dark_panel(self):
        """A `.badge.text-bg-default` pill (a label-selection value mapped to `default`) has no fill
        rule anywhere, so in dark it sits straight on the panel and its label is the body text tier,
        not core's real black (1.20:1 on the panel). The arm exists in the dark bundle only; the
        light page keeps core's black on white.

        The rule is read by its exact selector: `:where()` is outside the cascade model of
        _winning_declaration, which would skip it and report core's black.

        WOULD FAIL IF REVERTED: without the `text-bg-default` arm of dark_badge_label.scss the
        generic bare-badge selector skips the class (it excludes every `text-*`) and no rule
        re-points the label."""
        selector = ".badge:where(.text-bg-default)"
        dark_label = _normalize_colour(_last_value(self._css(DARK_BUNDLE), selector, "color") or "")
        self.assertEqual(
            dark_label, DARK_READABLE_TEXT,
            "`%s` compiles %r in the dark bundle, expected the body text tier %s."
            % (selector, dark_label, DARK_READABLE_TEXT),
        )
        self.assertGreaterEqual(_contrast_ratio(dark_label, DARK_BODY_BG), WCAG_AA_NORMAL_TEXT)
        self.assertIsNone(
            _last_value(self._css(BACKEND_BUNDLE), selector, "color"),
            "`%s` is compiled in the light bundle; the arm is dark-only." % selector,
        )

    def _disabled_label_opacity(self, css):
        found = None
        for _order, selector, body in _iter_rules(css):
            if ".form-check-input:disabled ~ .form-check-label" not in " ".join(selector.split()):
                continue
            for value, _important in _declarations(body, ("opacity",)):
                found = float(value)
        return found

    def test_faded_form_check_label_is_readable_on_the_dark_panel(self):
        """The label of a read-only (disabled) radio or checkbox is faded by Bootstrap's
        `.form-check-input:disabled ~ .form-check-label` opacity. In dark that fade, composited over
        the panel, keeps both label tiers (the muted tier the mobile form paints its labels with, and
        the body tier) at 4.5:1.

        WOULD FAIL IF REVERTED: dropping `$form-check-label-disabled-opacity` from dark_palette.scss
        returns Bootstrap's .5 default, which puts the muted tier at 2.66:1."""
        dark_opacity = self._disabled_label_opacity(self._css(DARK_BUNDLE))
        self.assertIsNotNone(dark_opacity, "No disabled form-check label opacity in the dark bundle.")
        for tier_name, tier in (("muted", DARK_MUTED_TIER), ("body", DARK_READABLE_TEXT)):
            with self.subTest(tier=tier_name):
                faded = _composite_over(tier, DARK_BODY_BG, dark_opacity)
                ratio = _contrast_ratio(faded, DARK_BODY_BG)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "A faded read-only label on the %s tier %s at opacity %.2f is %s = %.2f:1 on the "
                    "dark panel, below WCAG AA %.1f:1."
                    % (tier_name, tier, dark_opacity, faded, ratio, WCAG_AA_NORMAL_TEXT),
                )
