# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# WHAT IS PROTECTED (behaviour, not code): a user on the dark scheme reads every backend screen with
# no light band under light text and no dark text on a dark surface, and a user on the light scheme
# sees what the light bundles always compiled. Core's `*.dark.scss` files (survey section rows, file
# viewer toolbar, tooltips, settings sidebar, ...) are written against a DARK gray ramp, so the
# dark bundles must carry one: `$o-gray-100..900` run from the raised surface up to the body text,
# while `$white`, `$black`, `$light` and `$dark` keep their light-scheme meaning because core and
# Bootstrap use them for media chrome and `color-contrast()` labels in both schemes.
#
# Every expected value below is a literal, never re-derived through a Sass mix() in
# Python, and every contrast is the W3C WCAG 2.x formula owned by test_brand_cascade_compile.py.
# Modules outside viin_brand_web's closure (survey, mail) are read only when installed.
from odoo.tests.common import TransactionCase, tagged

from .test_brand_cascade_compile import (
    BACKEND_BUNDLE,
    DARK_BODY_BG,
    DARK_BUNDLE,
    DARK_READABLE_TEXT,
    WCAG_AA_NORMAL_TEXT,
    _COMMENT_RE,
    _contrast_ratio,
    _declarations,
    _iter_rules,
    _normalize_colour,
    _relative_luminance,
)

LAZY_BUNDLE = "web.assets_backend_lazy"
LAZY_DARK_BUNDLE = "web.assets_backend_lazy_dark"

# The dark gray ramp (every rung an alias of the palette ladder) and the light rungs core declares.
DARK_RAMP = {
    100: "#152225",
    200: "#1d2d31",
    300: "#25383c",
    400: "#31474c",
    500: "#60767a",
    600: "#8ea5a8",
    700: "#acbec0",
    800: "#c9d6d8",
    900: "#edf4f5",
}
LIGHT_RAMP = {
    100: "#f8f9fa",
    200: "#e9ecef",
    300: "#dee2e6",
    400: "#ced4da",
    500: "#adb5bd",
    600: "#6c757d",
    700: "#495057",
    800: "#343a40",
    900: "#212529",
}

DARK_PLACEHOLDER = "#8ea5a8"
LIGHT_PLACEHOLDER = "#bec5cc"

# Teal text on the dark panel: the notebook active tab, the selection-box active item and the
# empty-state link in the dark bundle; their light values.
DARK_TEAL_TEXT = "#4fd4e2"
DARK_TEAL_TEXT_HOVER = "#7fe0ea"
LIGHT_TEAL_TEXT = "#007f8e"
LIGHT_TEAL_TEXT_HOVER = "#005e68"

# Large bold text (WCAG SC 1.4.3 relaxed threshold).
WCAG_AA_LARGE_TEXT = 3.0

NOTEBOOK_ACTIVE = ".o_notebook:not(.vertical) .nav-link.active"
SELECTION_ACTIVE = (
    ".o_control_panel_actions .o_selection_container:has(.o_viin_selection_bar) "
    ".o_selection_box .list-group-item.active"
)
NOCONTENT_LINK = ".o_view_nocontent .o_nocontent_help a"
NOCONTENT_CTA = ".o_view_nocontent .o_nocontent_help .o_nocontent_create"


def _last_value(css, selector, prop):
    """The value of ``prop`` in the LAST rule whose selector list holds exactly ``selector``.

    Exact-selector match on purpose: every selector asked for here is one the dark bundle is expected to carry, and the
    last declaration of an exact selector is the cascade winner for it (same specificity, later
    source order). Returns None when no rule declares it."""
    wanted = " ".join(selector.split()).replace('"', "")
    found = None
    for _order, rule_selector, body in _iter_rules(css):
        if " ".join(rule_selector.split()).replace('"', "") != wanted:
            continue
        for value, _important in _declarations(body, (prop,)):
            found = value
    return found


def _root_value(css, prop):
    """The value of the custom property ``--<prop>`` declared on ``:root`` (last one wins)."""
    return _last_value(css, ":root", "--" + prop)


@tagged("post_install", "-at_install")
class TestDarkGrayRampCompile(TransactionCase):
    """The dark bundles carry the gray ramp and the scheme-invariant pins; the light bundles keep
    their light rungs."""

    def _css(self, bundle_name):
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        self.assertTrue(css.strip(), "%s compiled to empty CSS." % bundle_name)
        return _COMMENT_RE.sub("", css)

    def _installed(self, module_name):
        return bool(
            self.env["ir.module.module"].search_count(
                [("name", "=", module_name), ("state", "=", "installed")]
            )
        )

    def _colour(self, css, selector, prop, label):
        value = _last_value(css, selector, prop)
        self.assertIsNotNone(value, "no %s declared on %s (%s)" % (prop, selector, label))
        colour = _normalize_colour(value)
        self.assertIsNotNone(colour, "%s on %s is not a colour: %r" % (prop, selector, value))
        return colour

    # ------------------------------------------------------------------------------------------
    # The ramp and the scheme-invariant pins
    # ------------------------------------------------------------------------------------------
    def test_dark_bundles_carry_the_dark_gray_ramp_and_light_bundles_keep_core_rungs(self):
        """Rungs 100-900 compile to the dark ramp in the dark backend bundle and to core's light
        rungs in the light backend bundle, so a core dark file that reads `$o-gray-N` lands on a
        dark surface or light text in dark and is untouched in light. (The lazy dark bundle carries
        no :root block; its pivot hover band is guarded by test_pivot_dark_compile.)"""
        for bundle_name, expected in (
            (DARK_BUNDLE, DARK_RAMP),
            (BACKEND_BUNDLE, LIGHT_RAMP),
        ):
            css = self._css(bundle_name)
            for rung, hex_value in expected.items():
                with self.subTest(bundle=bundle_name, rung=rung):
                    value = _root_value(css, "gray-%d" % rung)
                    self.assertIsNotNone(
                        value, "%s declares no gray rung %d." % (bundle_name, rung)
                    )
                    self.assertEqual(
                        _normalize_colour(value), hex_value,
                        "gray rung %d in %s is %s, expected %s."
                        % (rung, bundle_name, value, hex_value),
                    )

    def test_white_black_light_and_dark_keep_their_light_scheme_meaning_in_dark(self):
        """`$white` / `$black` stay real white and black (the label of every teal fill is chosen by
        `color-contrast()` against them) and `$light` / `$dark` keep their light-scheme meaning
        (core media chrome such as the file viewer arrows uses `bg-dark text-white` in both
        schemes), so the dark ramp must not invert them."""
        css = self._css(DARK_BUNDLE)
        for name, expected in (
            ("white", "#ffffff"),
            ("black", "#000000"),
            ("light", "#ffffff"),
            ("dark", "#0b1315"),
            ("light-bg-subtle", "#152225"),
        ):
            with self.subTest(token=name):
                value = _root_value(css, name)
                self.assertIsNotNone(value, "the dark bundle declares no :root --%s." % name)
                self.assertEqual(
                    _normalize_colour(value), expected,
                    ":root --%s is %s in the dark bundle, expected %s." % (name, value, expected),
                )

    def test_link_button_in_dark_style_is_muted_at_rest_and_body_text_on_hover(self):
        """`btn btn-link btn-dark` (the mail activity list button) rests on the muted tier #8EA5A8
        and hovers to the body text tier, never to the near-black `$dark` (1.07:1 on the panel)."""
        css = self._css(DARK_BUNDLE)
        selector = ".btn-link.btn-dark"
        self.assertEqual(self._colour(css, selector, "color", "rest"), DARK_PLACEHOLDER)
        for state in (":hover", ":focus"):
            hover = _last_value(css, selector + state, "color")
            self.assertEqual(
                hover, "var(--color, #EDF4F5)",
                "%s must fall back to the body text tier." % (selector + state),
            )
        self.assertGreaterEqual(_contrast_ratio(DARK_READABLE_TEXT, DARK_BODY_BG), WCAG_AA_NORMAL_TEXT)

    def test_input_placeholder_reads_the_muted_text_rung_in_dark_and_is_untouched_in_light(self):
        """A placeholder in dark is #8EA5A8 (6.75:1 on the panel #111B1E); the ramp mix would give
        2.59:1. The light placeholder is core's."""
        dark = self._colour(
            self._css(DARK_BUNDLE), ".form-control::placeholder", "color", "dark placeholder"
        )
        self.assertEqual(dark, DARK_PLACEHOLDER)
        self.assertGreaterEqual(_contrast_ratio(dark, DARK_BODY_BG), WCAG_AA_NORMAL_TEXT)
        light = self._colour(
            self._css(BACKEND_BUNDLE), ".form-control::placeholder", "color", "light placeholder"
        )
        self.assertEqual(light, LIGHT_PLACEHOLDER)

    # ------------------------------------------------------------------------------------------
    # Survey rows and the sample card
    # ------------------------------------------------------------------------------------------
    def test_survey_section_row_and_sample_card_hover_are_the_dark_border_rung(self):
        """A survey section row paints #25383C under its #EDF4F5 label (11.03:1) and the empty-state
        sample card hovers to the same #25383C with a readable label."""
        if not self._installed("survey"):
            self.skipTest("survey is not installed")
        css = self._css(DARK_BUNDLE)
        section = self._colour(
            css, ".o_survey_form", "--SurveyForm__section-background-color", "section row"
        )
        self.assertEqual(section, "#25383c")
        self.assertGreaterEqual(_contrast_ratio(DARK_READABLE_TEXT, section), 11.0)
        hover = self._colour(
            css, ".o_survey_sample_card", "--SurveySampleCard-background-hover", "sample card"
        )
        self.assertEqual(hover, "#25383c")
        self.assertGreaterEqual(_contrast_ratio(DARK_READABLE_TEXT, hover), WCAG_AA_NORMAL_TEXT)

    # ------------------------------------------------------------------------------------------
    # Scheme-aware teal text
    # ------------------------------------------------------------------------------------------
    def test_notebook_active_tab_label_and_underline_are_teal_per_scheme(self):
        """The active notebook tab label and its 2px underline are #4FD4E2 in dark (9.9:1 on the
        panel) and #007F8E in light."""
        for bundle_name, expected in ((DARK_BUNDLE, DARK_TEAL_TEXT), (BACKEND_BUNDLE, LIGHT_TEAL_TEXT)):
            css = self._css(bundle_name)
            for state in ("", ":hover", ":focus", ":active"):
                selector = NOTEBOOK_ACTIVE + state
                self.assertEqual(
                    self._colour(css, selector, "color", "tab label"), expected,
                    "%s label in %s" % (selector, bundle_name),
                )
                self.assertEqual(
                    self._colour(css, selector, "border-bottom-color", "tab underline"), expected,
                    "%s underline in %s" % (selector, bundle_name),
                )
        self.assertGreaterEqual(_contrast_ratio(DARK_TEAL_TEXT, DARK_BODY_BG), 9.8)

    def test_selection_box_active_item_label_is_teal_per_scheme(self):
        """The active item of the control-panel selection box reads #4FD4E2 in dark and #007F8E in
        light."""
        for bundle_name, expected in ((DARK_BUNDLE, DARK_TEAL_TEXT), (BACKEND_BUNDLE, LIGHT_TEAL_TEXT)):
            self.assertEqual(
                self._colour(self._css(bundle_name), SELECTION_ACTIVE, "color", "active item"),
                expected, bundle_name,
            )

    def test_empty_state_link_is_core_link_colour_in_dark_and_brand_teal_in_light(self):
        """The empty-state help link and its create CTA are #4FD4E2 / hover #7FE0EA in dark, taken
        from core's `--link-color` (the module declares no colour for them in the dark bundle), and
        #007F8E / hover #005E68 in light."""
        dark_css = self._css(DARK_BUNDLE)
        for selector in (NOCONTENT_LINK, NOCONTENT_CTA):
            for state in ("", ":hover", ":focus"):
                self.assertIsNone(
                    _last_value(dark_css, selector + state, "color"),
                    "%s declares a colour in the dark bundle; the link must stay core's."
                    % (selector + state),
                )
        self.assertEqual(_normalize_colour(_root_value(dark_css, "link-color")), DARK_TEAL_TEXT)
        self.assertEqual(
            _normalize_colour(_root_value(dark_css, "link-hover-color")), DARK_TEAL_TEXT_HOVER
        )
        light_css = self._css(BACKEND_BUNDLE)
        for selector in (NOCONTENT_LINK, NOCONTENT_CTA):
            self.assertEqual(
                self._colour(light_css, selector, "color", "light link"), LIGHT_TEAL_TEXT
            )
            for state in (":hover", ":focus"):
                self.assertEqual(
                    self._colour(light_css, selector + state, "color", "light link hover"),
                    LIGHT_TEAL_TEXT_HOVER,
                )

    # ------------------------------------------------------------------------------------------
    # Settings chrome
    # ------------------------------------------------------------------------------------------
    def test_settings_sidebar_tabs_and_section_titles_read_the_ramp(self):
        """Settings: sidebar #152225 under a #EDF4F5 idle label (14.6:1), selected tab #21464B with
        a #EDF4F5 label (9.2:1), section title band #1D2D31."""
        css = self._css(DARK_BUNDLE)
        renderer = ".o_base_settings_view .o_form_renderer"
        sidebar = self._colour(css, renderer, "--settings__tab-bg", "sidebar")
        selected = self._colour(css, renderer, "--settings__tab-bg--active", "selected tab")
        title = self._colour(css, renderer, "--settings__title-bg", "section title band")
        self.assertEqual((sidebar, selected, title), ("#152225", "#21464b", "#1d2d31"))
        label = self._colour(css, renderer, "--settings__tab-color", "tab label")
        self.assertEqual(label, DARK_READABLE_TEXT)
        self.assertGreaterEqual(_contrast_ratio(label, sidebar), 14.6)
        self.assertGreaterEqual(_contrast_ratio(label, selected), 9.2)
        for state in (".tab:hover", ".tab.selected"):
            selector = (
                ".o_base_settings_view .o_form_renderer .o_setting_container .settings_tab " + state
            )
            self.assertEqual(
                _last_value(css, selector, "color"), "var(--settings__tab-color)",
                "%s must keep the light tab colour, not core's black." % state,
            )

    def test_text_primary_utility_reads_the_dark_link_teal(self):
        """`.text-primary` text is #4FD4E2 (hover #7FE0EA) in dark, 9.88:1 on the panel, and keeps
        the chrome teal #007F8E in light."""
        dark = self._css(DARK_BUNDLE)
        self.assertEqual(
            self._colour(dark, ".text-primary", "--color", "dark text-primary"), DARK_TEAL_TEXT
        )
        self.assertIn(
            "var(--text-opacity", _last_value(dark, ".text-primary", "--color"),
            "`.text-primary` must keep the utility's `--text-opacity` contract.",
        )
        self.assertEqual(
            self._colour(dark, ".text-primary:hover", "--color", "dark hover"), DARK_TEAL_TEXT_HOVER
        )
        self.assertGreaterEqual(_contrast_ratio(DARK_TEAL_TEXT, DARK_BODY_BG), WCAG_AA_NORMAL_TEXT)
        light = self._css(BACKEND_BUNDLE)
        self.assertEqual(
            self._colour(light, ".text-primary", "--color", "light text-primary"), LIGHT_TEAL_TEXT
        )

    # ------------------------------------------------------------------------------------------
    # Tooltips and the file viewer
    # ------------------------------------------------------------------------------------------
    def test_bootstrap_tooltip_label_is_readable_on_its_background(self):
        """`.tooltip`: #1D2D31 label on a #C9D6D8 background, 9.6:1."""
        css = self._css(DARK_BUNDLE)
        label = self._colour(css, ".tooltip", "--tooltip-color", "tooltip label")
        background_value = _last_value(css, ".tooltip", "--tooltip-bg")
        self.assertIsNotNone(background_value)
        if background_value.startswith("var("):
            background_value = _root_value(css, background_value[4:-1].split(",")[0][2:])
        background = _normalize_colour(background_value)
        self.assertEqual((label, background), ("#1d2d31", "#c9d6d8"))
        self.assertGreaterEqual(_contrast_ratio(label, background), 9.5)

    def test_odoo_tooltip_label_is_readable_on_its_background(self):
        """`.o-tooltip`: the label (`--tooltip-color`) reads at least 4.5:1 on the chip
        (`--tooltip-bg`) in dark, resolving both through the `:root` tokens they point at."""
        css = self._css(DARK_BUNDLE)

        def resolve(value):
            for _depth in range(3):
                if value is None or not value.startswith("var("):
                    break
                value = _root_value(css, value[4:-1].split(",")[0].strip()[2:])
            return _normalize_colour(value or "")

        label = resolve(_last_value(css, ".o-tooltip", "--tooltip-color"))
        background = resolve(_last_value(css, ".o-tooltip", "--tooltip-bg"))
        self.assertIsNotNone(label)
        self.assertIsNotNone(background)
        self.assertGreaterEqual(
            round(_contrast_ratio(label, background), 2), WCAG_AA_NORMAL_TEXT,
            ".o-tooltip label %s on %s" % (label, background),
        )

    def test_file_viewer_chrome_keeps_white_labels_on_dark_fills(self):
        """The file viewer header and toolbar buttons paint #1D2D31 under white (14.2:1) and the
        previous/next circles (`bg-dark text-white`) paint #0B1315 under white (18.8:1)."""
        css = self._css(DARK_BUNDLE)
        for selector in (".o-FileViewer-header", ".o-FileViewer-toolbarButton"):
            fill = self._colour(css, selector, "--FileViewer-toolbarBgColor", "toolbar fill")
            self.assertEqual(fill, "#1d2d31", selector)
            self.assertGreaterEqual(_contrast_ratio("#ffffff", fill), 14.1, selector)
        dark_utility = _last_value(css, ".bg-dark", "--background-color")
        self.assertIsNotNone(dark_utility, "the dark bundle declares no .bg-dark fill.")
        circle = _normalize_colour(dark_utility)
        self.assertEqual(circle, "#0b1315")
        self.assertGreaterEqual(_contrast_ratio("#ffffff", circle), 18.7)
        white_text = _normalize_colour(_last_value(css, ".text-white", "--color") or "")
        self.assertEqual(white_text, "#ffffff")

    # ------------------------------------------------------------------------------------------
    # Activity view status cells
    # ------------------------------------------------------------------------------------------
    def test_activity_view_status_cells_and_counter_stay_readable_in_dark(self):
        """In the dark lazy bundle the count label of a `.today` / `.planned` / `.overdue` activity
        cell reads at least 3:1 (large bold text) on its status fill, a `.done` cell label at least
        3:1 on its fill, and the cell counter label at least 4.5:1 on its `.bg-light` badge.

        The lazy bundle holds no media chrome, so `$light` / `$dark` follow the dark ramp there
        (dark label on a bright status fill); the scheme-invariant pins live in the non-lazy
        bundle only."""
        if not self._installed("mail"):
            self.skipTest("mail is not installed")
        css = self._css(LAZY_DARK_BUNDLE)
        for state in ("today", "planned", "overdue"):
            selector = ".o_activity_view .o_activity_summary_cell.%s" % state
            fill = self._colour(css, selector, "background-color", "%s fill" % state)
            label = self._colour(css, selector, "color", "%s label" % state)
            self.assertGreaterEqual(
                round(_contrast_ratio(label, fill), 2), WCAG_AA_LARGE_TEXT,
                "%s cell: %s on %s" % (state, label, fill),
            )
        done = ".o_activity_view .o_activity_summary_cell.done"
        done_fill = self._colour(css, done, "background-color", "done fill")
        done_label = self._colour(css, done + " a", "color", "done label")
        self.assertGreaterEqual(
            round(_contrast_ratio(done_label, done_fill), 2), WCAG_AA_LARGE_TEXT,
            "done cell: %s on %s" % (done_label, done_fill),
        )
        counter = self._colour(
            css, ".o_activity_view .o_activity_summary_cell .o-mail-ActivityCell-counter",
            "color", "counter label",
        )
        badge = self._colour(self._css(DARK_BUNDLE), ".bg-light", "--background-color", "badge")
        self.assertGreaterEqual(
            round(_contrast_ratio(counter, badge), 2), WCAG_AA_NORMAL_TEXT,
            "activity counter: %s on %s" % (counter, badge),
        )

    # ------------------------------------------------------------------------------------------
    # Theme-colour tints, calendar event header, labels on gray-ramp chips
    # ------------------------------------------------------------------------------------------
    def test_theme_colour_tints_are_dark_surfaces_with_readable_emphasis_in_dark(self):
        """`alert-*`, `list-group-item-*` and the `*-subtle` utilities read the tint tokens: in dark
        the subtle background is a dark surface (relative luminance at most 0.45) carrying its
        emphasis text at 4.5:1 or more; in light the subtle background stays a pale tint."""
        dark = self._css(DARK_BUNDLE)
        light = self._css(BACKEND_BUNDLE)
        for name in ("primary", "success", "info", "warning", "danger"):
            with self.subTest(colour=name):
                background = _normalize_colour(_root_value(dark, name + "-bg-subtle") or "")
                text = _normalize_colour(_root_value(dark, name + "-text-emphasis") or "")
                self.assertIsNotNone(background)
                self.assertIsNotNone(text)
                self.assertLessEqual(_relative_luminance(background), 0.45, "%s tint" % name)
                self.assertGreaterEqual(
                    round(_contrast_ratio(text, background), 2), WCAG_AA_NORMAL_TEXT,
                    "%s emphasis %s on %s" % (name, text, background),
                )
                light_background = _normalize_colour(_root_value(light, name + "-bg-subtle") or "")
                self.assertGreater(_relative_luminance(light_background), 0.7, "light %s tint" % name)

    def test_calendar_event_dialog_header_text_reads_on_every_colour_band(self):
        """The mobile event dialog paints a pale band per colour index; its title and buttons are
        the black label of a pale chip, at 4.5:1 or more on every band, and the light bundle keeps
        core's body-text label."""
        css = self._css(DARK_BUNDLE)
        bands = {}
        for _order, selector, body in _iter_rules(css):
            parts = " ".join(selector.split())
            prefix = ".modal.o_technical_modal.o_modal_full .modal-dialog .modal-content.o_calendar_color_"
            if parts.startswith(prefix) and parts.endswith(" .modal-header"):
                for value, _important in _declarations(body, ("background-color",)):
                    bands[parts[len(prefix):].split(" ")[0]] = _normalize_colour(value)
        self.assertTrue(bands, "no calendar colour band compiled in the dark bundle")
        header = (
            '.modal.o_technical_modal.o_modal_full .modal-dialog '
            '.modal-content[class*="o_calendar_color_"] .modal-header'
        )
        for part in (".modal-title", ".btn"):
            label = self._colour(css, header + " " + part, "color", "dialog " + part)
            for index, band in bands.items():
                with self.subTest(part=part, colour=index):
                    self.assertGreaterEqual(
                        round(_contrast_ratio(label, band), 2), WCAG_AA_NORMAL_TEXT,
                        "dialog %s %s on band %s" % (part, label, band),
                    )
        self.assertIsNone(_last_value(self._css(BACKEND_BUNDLE), header + " .modal-title", "color"))

    def test_badge_on_a_gray_ramp_chip_reads_the_body_text_in_dark(self):
        """`.badge.bg-100` .. `.bg-400` (the calendar week badge) sit on the dark ramp chip, so
        their label is the body text tier at 4.5:1 or more on that chip; light is core's black."""
        dark = self._css(DARK_BUNDLE)
        light = self._css(BACKEND_BUNDLE)
        for name in ("100", "200", "300", "400", "secondary", "light"):
            with self.subTest(chip=name):
                chip = self._colour(dark, ".bg-" + name, "--background-color", "chip")
                label = self._colour(dark, ".badge.bg-" + name, "color", "badge label")
                self.assertGreaterEqual(round(_contrast_ratio(label, chip), 2), WCAG_AA_NORMAL_TEXT)
                self.assertIsNone(_last_value(light, ".badge.bg-" + name, "color"))

    def test_bare_badge_label_is_the_body_text_in_dark_and_core_black_in_light(self):
        """A badge with no `bg-*`, `text-*` or `o_badge_color_*` class sits on the dark panel, so
        its label is the body text tier at 4.5:1 or more on it; the rule adds no specificity over
        core's `.badge` (so a component that paints its own label on its own fill keeps it) and
        the light bundle keeps core's black."""
        selector = '.badge:where(:not([class*="bg-"]):not([class*="text-"]):not([class*="o_badge_color"]))'
        dark = self._css(DARK_BUNDLE)
        label = self._colour(dark, selector, "color", "bare badge label")
        self.assertGreaterEqual(round(_contrast_ratio(label, DARK_BODY_BG), 2), WCAG_AA_NORMAL_TEXT)
        self.assertEqual(label, DARK_READABLE_TEXT)
        self.assertIsNone(_last_value(self._css(BACKEND_BUNDLE), selector, "color"))
