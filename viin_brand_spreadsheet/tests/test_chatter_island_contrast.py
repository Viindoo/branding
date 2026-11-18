# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Compiled-render contrast guards for the mail Chatter embedded in the spreadsheet editor's side
# panel, which is a light island inside the dark app. Each assertion measures the WCAG ratio of the
# compiled dark-bundle colours against a fixed threshold, so a re-tune that still clears it is not
# a false alarm. The spreadsheet editor is not mounted.
import re

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.misc import file_open

from odoo.addons.viin_brand_mail.tests.test_mail_contrast_compile import (
    ACTIVE_CHATTER_TOGGLE_CLASSES,
    BACKGROUND_PROPS,
    CHATTER_CONTENT_CLASSES,
    CHATTER_ROOT_CLASSES,
    CHATTER_THREAD_HOST_LAYERS,
    CHATTER_TOGGLE_PREV_SIBLING,
    CHATTER_TOP_CLASSES,
    CHATTER_TOPBAR_CLASSES,
    COMPOSER_INPUT_CHATTER_LAYERS,
    COMPOSER_INPUT_CLASSES,
    DARK_BUNDLE,
    FOLLOWERS_BUTTON_CLASSES,
    MESSAGE_BODY_CLASSES,
    MESSAGE_BODY_MUTED_CLASSES,
    MESSAGE_BUBBLE_CLASSES,
    MESSAGE_BUBBLE_SIBLING_BY_VARIANT,
    MESSAGE_CORE_CLASSES,
    MESSAGE_DATE_CLASSES,
    MESSAGE_EDITED_MARKER_CLASSES,
    MESSAGE_EDITED_MARKER_TAG,
    MESSAGE_EMPTY_PLACEHOLDER_CLASSES,
    MESSAGE_EMPTY_PLACEHOLDER_TAG,
    MESSAGE_HEADER_CLASSES,
    MESSAGE_ROOT_CLASSES,
    MESSAGE_SUBTREE_TO_THREAD_LAYERS,
    MESSAGE_TEXT_BODY_CLASSES,
    THREAD_CLASSES,
    WCAG_AA_NON_TEXT,
    WCAG_AA_NORMAL_TEXT,
    WEBCLIENT_ANCESTORS,
    ContrastCompileHelpers,
    _computed_value,
    _composite,
    _contrast_ratio,
    _edited_marker_layers,
    _element_chain,
    _MESSAGE_CONTENT_WRAPPER,
    _normalize_value,
    _opaque_rgb,
    _to_alpha,
)

ISLAND_SURFACE = "#ffffff"
ISLAND_BODY_TEXT = "#374151"
# Lower bound that keeps a bubble border perceptible on the island surface without becoming a frame.
ISLAND_BUBBLE_BORDER_MIN_RATIO = 1.15

CORE_SPREADSHEET_DARK_SCSS = "spreadsheet/static/src/o_spreadsheet/o_spreadsheet_extended.dark.scss"

# The `.btn` block inside that file's `.o-spreadsheet` wrapper, anchored at a line start so the
# neighbouring `.badge` / `.o_input` blocks are not read. The value is captured, not pinned.
_ISLAND_BUTTON_COLOUR_RE = re.compile(
    r"^\s*\.btn\s*\{[^{}]*?(?<![\w-])color\s*:\s*([^;}]+)", re.MULTILINE | re.DOTALL
)

SPREADSHEET_ISLAND_ROOT = frozenset({"o-spreadsheet"}) | WEBCLIENT_ANCESTORS
SPREADSHEET_SIDE_PANEL = frozenset({"o-sidePanel"})
# The panel root carries no background utility, so the engine's own `.o-sidePanel` shows through.
SPREADSHEET_COMMENTS_PANEL = frozenset({"p-3"})
SPREADSHEET_COMMENTS_ITEM = frozenset({"border-bottom", "pb-2", "mb-2"})
SPREADSHEET_COMMENTS_THREAD = frozenset({"mt-2"})

# Outwards from the Chatter root: the layers every embedded-Chatter element shares.
ISLAND_PANEL_LAYERS = (
    SPREADSHEET_COMMENTS_THREAD, SPREADSHEET_COMMENTS_ITEM, SPREADSHEET_COMMENTS_PANEL,
    SPREADSHEET_SIDE_PANEL, SPREADSHEET_ISLAND_ROOT,
)
ISLAND_TOPBAR_LAYERS = (
    CHATTER_TOPBAR_CLASSES, CHATTER_TOP_CLASSES, CHATTER_ROOT_CLASSES,
) + ISLAND_PANEL_LAYERS

# Resting state of a closed composer (chatter.xml): "Send message" is `.btn-primary`, "Log note" and
# "Activity" are `.btn-secondary`. Each entry carries its real preceding sibling, which rules out
# Bootstrap's `.btn-check:checked + .btn` group.
_ISLAND_SEND_MESSAGE = frozenset({
    "o-mail-Chatter-sendMessage", "btn", "text-nowrap", "me-1", "btn-primary", "my-2",
})
_ISLAND_LOG_NOTE = frozenset({
    "o-mail-Chatter-logNote", "btn", "text-nowrap", "me-1", "btn-secondary", "my-2",
})
_ISLAND_ACTIVITY = frozenset({
    "o-mail-Chatter-activity", "btn", "btn-secondary", "text-nowrap", "my-2",
})
ISLAND_COMPOSER_BUTTONS = (
    ("Send message", _ISLAND_SEND_MESSAGE, frozenset()),
    ("Log note", _ISLAND_LOG_NOTE, _ISLAND_SEND_MESSAGE),
    ("Activity", _ISLAND_ACTIVITY, _ISLAND_LOG_NOTE),
)

ISLAND_MESSAGE_LAYERS = (
    MESSAGE_SUBTREE_TO_THREAD_LAYERS + CHATTER_THREAD_HOST_LAYERS + ISLAND_PANEL_LAYERS
)
ISLAND_TEXT_BODY_LAYERS = (MESSAGE_TEXT_BODY_CLASSES,) + ISLAND_MESSAGE_LAYERS
ISLAND_MESSAGE_HEADER_LAYERS = (
    MESSAGE_HEADER_CLASSES, _MESSAGE_CONTENT_WRAPPER, MESSAGE_CORE_CLASSES, MESSAGE_ROOT_CLASSES,
    THREAD_CLASSES, CHATTER_CONTENT_CLASSES, CHATTER_ROOT_CLASSES,
) + ISLAND_PANEL_LAYERS
ISLAND_MESSAGE_BODY_MUTED_LAYERS = (MESSAGE_BODY_CLASSES,) + ISLAND_TEXT_BODY_LAYERS

# The placeholder shares ISLAND_MESSAGE_BODY_MUTED_LAYERS with the `Subject:` line; the `(edited)`
# marker needs its own stack.
ISLAND_EDITED_MARKER_LAYERS = _edited_marker_layers(ISLAND_MESSAGE_LAYERS)
ISLAND_COMPOSER_INPUT_LAYERS = COMPOSER_INPUT_CHATTER_LAYERS + ISLAND_PANEL_LAYERS
ISLAND_BUBBLE_CLASSES = MESSAGE_BUBBLE_CLASSES


@tagged("post_install", "-at_install")
class SpreadsheetChatterIslandContrastTest(ContrastCompileHelpers, TransactionCase):
    """The Chatter embedded in the spreadsheet editor reads as part of the editor's light island.

    Core keeps the editor light in dark mode and repaints only button labels, so an embedded Chatter
    would serve labels from the light scheme over fills from the dark one.
    """

    def _island_forced_button_text(self):
        """Return the label core forces on every ``.btn`` inside ``.o-spreadsheet``.

        The value is read from core's dark stylesheet off the addons path, so it does not depend on
        ``spreadsheet`` being installed.

        :return: ``(value, rgb)`` of the label
        """
        try:
            with file_open(CORE_SPREADSHEET_DARK_SCSS, "r") as core_file:
                content = core_file.read()
        except OSError:
            content = None
        self.assertIsNotNone(
            content,
            "%s could not be read off the addons path. It is the core stylesheet that forces the "
            "spreadsheet editor to stay a LIGHT island in dark mode; without it the light-island "
            "label these guards measure against cannot be grounded - re-ground them against "
            "whatever core replaced it with rather than pinning a literal here."
            % CORE_SPREADSHEET_DARK_SCSS,
        )
        match = _ISLAND_BUTTON_COLOUR_RE.search(content)
        self.assertIsNotNone(
            match,
            "%s declares no `.btn { color: ... }` inside its `.o-spreadsheet` wrapper. That "
            "declaration is the whole reason a dark-palette Chatter goes unreadable inside the "
            "editor; if core dropped it, re-ground these guards rather than deleting them."
            % CORE_SPREADSHEET_DARK_SCSS,
        )
        value = _normalize_value(match.group(1))
        return value, self._assert_rgb(value, "spreadsheet light-island .btn label")

    def _island_rendered_surface(self, css, chain, label):
        """Return the dark-bundle surface an element renders on, by ancestor walk only.

        :return: ``(depth, value, rgb)`` of the surface
        """
        backdrop = self._rendered_backdrop(css, chain, DARK_BUNDLE, label)
        return backdrop.depth, backdrop.value, backdrop.rgb

    def _island_inherited_colour(self, css, chain, label):
        """Return the dark-bundle inherited text colour of an element."""
        return self._inherited_colour(css, chain, DARK_BUNDLE, label)

    def test_dark_spreadsheet_island_chatter_buttons_clear_aa_under_the_forced_light_label(self):
        """Every composer button of the embedded Chatter clears AA under core's forced light label.

        Core repaints the label of each island ``.btn`` but not its fill, so the fill must be one
        that reads against that label. The label is read from core, the fill is resolved over the
        real ancestor chain, so any readable fill passes.
        """
        # The element models are transcribed from this template.
        self._assert_core_source_contains(
            "mail/static/src/chatter/web/chatter.xml",
            ("o-mail-Chatter-sendMessage btn", "o-mail-Chatter-logNote btn",
             "o-mail-Chatter-activity btn btn-secondary"),
            "The chatter composer buttons do not carry those classes, so the island element "
            "models below are keyed on markup core stopped rendering.",
        )
        css = self._compiled_css(DARK_BUNDLE)
        label_value, label_rgb = self._island_forced_button_text()

        for name, classes, prev_sibling in ISLAND_COMPOSER_BUTTONS:
            with self.subTest(button=name):
                chain = _element_chain(classes, ISLAND_TOPBAR_LAYERS, prev_sibling)
                fill_value = _computed_value(css, chain, BACKGROUND_PROPS)
                self.assertIsNotNone(
                    fill_value,
                    "No compiled background applies to the %r composer button inside the spreadsheet "
                    "island in %s - Bootstrap's own `.btn { background-color: var(--btn-bg) }` is in "
                    "the bundle, so an empty resolution means the modelled element does not match "
                    "the markup." % (name, DARK_BUNDLE),
                )
                fill_rgb = _opaque_rgb(fill_value)
                self.assertIsNotNone(
                    fill_rgb,
                    "The %r composer button resolves the background %r inside the spreadsheet "
                    "island, which is not an opaque colour this contrast guard can measure. A "
                    "composer button is a filled control: it must paint its own opaque surface, "
                    "otherwise its label sits on whatever the panel behind it happens to be."
                    % (name, fill_value),
                )
                ratio = _contrast_ratio(label_rgb, fill_rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "Inside the spreadsheet light island the %r button renders core's forced label "
                    "%s on the fill %s (rgb%r) - only %.2f:1, where WCAG AA normal text needs "
                    ">= %.1f:1. Core repaints the label and not the fill, so a dark-ladder fill "
                    "leaves half of the pair in the wrong scheme; the button must render on the "
                    "island's LIGHT surface."
                    % (name, label_value, fill_value, fill_rgb, ratio, WCAG_AA_NORMAL_TEXT),
                )

    def test_dark_spreadsheet_island_chatter_surface_is_light_and_keeps_its_message_text_readable(
        self,
    ):
        """The embedded Chatter's surface is the island's light one and its message text reads on it.

        Transparent controls (cell-address toggle, Resolve, link-style topbar actions) render core's
        forced label directly on the surface, so the surface must be light. The message text must be
        coherent with it: ``.o-discuss-text-body`` carries a bare-class ``!important`` colour that
        an island rule on the Chatter root cannot outrank, so the body is resolved over the real
        message chain. ``.o-mail-Message-bubble`` is a positioned sibling of the body and is
        resolved as its own element; a message with no bubble keeps the ancestor walk.
        """
        css = self._compiled_css(DARK_BUNDLE)
        label_value, label_rgb = self._island_forced_button_text()
        chain = _element_chain(CHATTER_ROOT_CLASSES, ISLAND_PANEL_LAYERS)

        depth, surface_value, surface_rgb = self._island_rendered_surface(
            css, chain, "spreadsheet island chatter surface"
        )
        painted_by = "the app body background" if depth >= len(chain) else (
            "layer %d of the modelled chain" % depth
        )

        with self.subTest(direction="core's forced light-island label"):
            ratio = _contrast_ratio(label_rgb, surface_rgb)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "Inside the spreadsheet light island the Chatter renders on %s (%s, rgb%r, painted "
                "by %s), and core's forced light-island label %s reads only %.2f:1 on it - WCAG AA "
                "normal text needs >= %.1f:1. Every transparent control in the panel (the "
                "cell-address toggle, Resolve, the Chatter's link-style topbar actions) carries that "
                "label with no fill of its own, so the surface itself has to be the island's light "
                "one." % (DARK_BUNDLE, surface_value, surface_rgb, painted_by, label_value, ratio,
                          WCAG_AA_NORMAL_TEXT),
            )

        with self.subTest(direction="the chatter's inherited text tier"):
            text_value = _computed_value(css, chain, ("color",))
            if text_value is None:
                # The text inherits from the document body, whose colour core emits on :root.
                text_value = self._dark_root_token(
                    css, "body-color", "spreadsheet island chatter text"
                )
            text_value, text_rgb = self._resolve_dark_colour(
                css, text_value, "spreadsheet island chatter text"
            )
            ratio = _contrast_ratio(text_rgb, surface_rgb)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "Inside the spreadsheet light island the Chatter's inherited text tier %s reads "
                "only %.2f:1 on the surface it renders on (%s, rgb%r) - WCAG AA normal text needs "
                ">= %.1f:1. This is the tier every descendant with no colour of its own takes - the "
                "message author name, the date row, the activity labels - so lighting the island "
                "surface without re-pointing it moves the unreadability from the buttons to those "
                "labels instead of ending it. The message BODY does not inherit from here; it is "
                "asserted separately below, against the wrapper that really colours it."
                % (text_value, ratio, surface_value, surface_rgb, WCAG_AA_NORMAL_TEXT),
            )

        # The body colour is declared on the `.o-discuss-text-body` wrapper, so the walk starts at
        # `.o-mail-Message-body`.
        body_chain = _element_chain(MESSAGE_BODY_CLASSES, ISLAND_TEXT_BODY_LAYERS)
        body_value, body_rgb = self._island_inherited_colour(
            css, body_chain, "spreadsheet island message body text"
        )

        for variant in sorted(ISLAND_BUBBLE_CLASSES):
            with self.subTest(message_surface=variant):
                # The bubble comes from the cluster's single painted-sibling model.
                backdrop = self._rendered_backdrop(
                    css, body_chain, DARK_BUNDLE, "spreadsheet island message body surface",
                    siblings=(MESSAGE_BUBBLE_SIBLING_BY_VARIANT[variant],),
                )
                bubble_value, bubble_rgb = backdrop.value, backdrop.rgb
                ratio = _contrast_ratio(body_rgb, bubble_rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "Inside the spreadsheet light island a %s message renders its body text %s on "
                    "the bubble fill %s (rgb%r) - only %.2f:1, where WCAG AA normal text needs "
                    ">= %.1f:1. The bubble is a `position-absolute` SIBLING of the body "
                    "(message.xml:89), so this is the colour under the glyphs however light the "
                    "panel behind it is; and the body's colour comes from the bare-class "
                    "`!important` on `.o-discuss-text-body` (core.dark.scss:13-15), which no normal "
                    "island rule can outrank. Re-point that wrapper inside `.o-spreadsheet` so the "
                    "text matches the island's own bubbles."
                    % (variant, body_value, bubble_value, bubble_rgb, ratio, WCAG_AA_NORMAL_TEXT),
                )

        with self.subTest(message_surface="no bubble"):
            # A note and a notification carry no bubbleColor, so nothing is painted between the
            # glyphs and the panel.
            _depth, plain_value, plain_rgb = self._island_rendered_surface(
                css, body_chain, "spreadsheet island message body surface"
            )
            ratio = _contrast_ratio(body_rgb, plain_rgb)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "Inside the spreadsheet light island a message with no bubble renders its body text "
                "%s directly on the panel surface %s (rgb%r) - only %.2f:1, where WCAG AA normal "
                "text needs >= %.1f:1. Every note and every notification body lands here, so "
                "re-pointing only the bubbled variants would leave them exactly as unreadable."
                % (body_value, plain_value, plain_rgb, ratio, WCAG_AA_NORMAL_TEXT),
            )

    def test_dark_spreadsheet_island_muted_secondary_text_clears_aa_on_every_surface_it_lands_on(
        self,
    ):
        """The island's muted secondary tier clears AA on every surface the island paints under it.

        The timestamp sits in ``.o-mail-Message-header``, outside the bubble, so its surface is the
        panel. The muted markers inside ``.o-mail-Message-body`` sit on the bubble when the message
        has one, and every bubble is darker than the panel, so a tier tuned only against the panel
        fails there. Each subject is resolved through the cascade where it is declared.
        """
        # The element models are transcribed from this template.
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.xml",
            ('class="o-mail-Message-date o-xsmaller"',
             "o-mail-Message-header d-flex flex-wrap align-items-baseline lh-1",
             'class="d-block text-muted smaller">Subject:'),
            "The muted secondary markers do not carry those classes, so the element models below "
            "are keyed on markup core stopped rendering - re-transcribe them from message.xml.",
        )
        css = self._compiled_css(DARK_BUNDLE)

        # The timestamp takes the tier through a custom property on an ancestor, the in-body markers
        # through an important rule on themselves; each is read where it is declared.
        date_chain = _element_chain(MESSAGE_DATE_CLASSES, ISLAND_MESSAGE_HEADER_LAYERS)
        date_value, date_rgb = self._island_inherited_colour(
            css, date_chain, "spreadsheet island message timestamp"
        )
        muted_chain = _element_chain(MESSAGE_BODY_MUTED_CLASSES, ISLAND_MESSAGE_BODY_MUTED_LAYERS)
        muted_value, muted_rgb = self._island_inherited_colour(
            css, muted_chain, "spreadsheet island in-body muted marker"
        )

        with self.subTest(muted_surface="panel, under the message timestamp"):
            _depth, panel_value, panel_rgb = self._island_rendered_surface(
                css, date_chain, "spreadsheet island message timestamp surface"
            )
            ratio = _contrast_ratio(date_rgb, panel_rgb)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "Inside the spreadsheet light island the message timestamp renders %s on the panel "
                "surface %s (rgb%r) - only %.2f:1, where WCAG AA normal text needs >= %.1f:1. The "
                "timestamp is in `.o-mail-Message-header` (message.xml:44), outside "
                "`.o-discuss-text-body`, so this panel IS its surface: no bubble is ever painted "
                "behind it and there is no darker case to fall back on."
                % (date_value, panel_value, panel_rgb, ratio, WCAG_AA_NORMAL_TEXT),
            )

        for variant in sorted(ISLAND_BUBBLE_CLASSES):
            with self.subTest(muted_surface="%s bubble" % variant):
                # Same painted-sibling model as the body guard above.
                backdrop = self._rendered_backdrop(
                    css, muted_chain, DARK_BUNDLE,
                    "spreadsheet island in-body muted marker surface",
                    siblings=(MESSAGE_BUBBLE_SIBLING_BY_VARIANT[variant],),
                )
                bubble_value, bubble_rgb = backdrop.value, backdrop.rgb
                ratio = _contrast_ratio(muted_rgb, bubble_rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "Inside the spreadsheet light island a %s message renders its muted markers %s "
                    "on the bubble fill %s (rgb%r) - only %.2f:1, where WCAG AA normal text needs "
                    ">= %.1f:1. The `Subject:` line, the empty-message placeholder and the two "
                    "translation notes (message.xml:110-120) all sit INSIDE "
                    "`.o-mail-Message-body`, so the bubble - a `position-absolute` sibling filling "
                    "the wrapper edge to edge (message.xml:89) - is the colour under them, not the "
                    "panel. Every bubble is darker than the panel, so a secondary tier tuned "
                    "against the panel alone cannot clear AA here."
                    % (variant, muted_value, bubble_value, bubble_rgb, ratio, WCAG_AA_NORMAL_TEXT),
                )

        with self.subTest(muted_surface="panel, under an unbubbled message body"):
            # A note and a notification carry no bubbleColor, so nothing is painted between the
            # glyphs and the panel.
            _depth, plain_value, plain_rgb = self._island_rendered_surface(
                css, muted_chain, "spreadsheet island in-body muted marker surface"
            )
            ratio = _contrast_ratio(muted_rgb, plain_rgb)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "Inside the spreadsheet light island a message with no bubble renders its muted "
                "markers %s directly on the panel surface %s (rgb%r) - only %.2f:1, where WCAG AA "
                "normal text needs >= %.1f:1. Every note and every notification lands here, so "
                "re-pointing only the bubbled variants would leave them exactly as unreadable."
                % (muted_value, plain_value, plain_rgb, ratio, WCAG_AA_NORMAL_TEXT),
            )

    def test_dark_spreadsheet_island_composer_input_text_reads_on_the_field_it_types_into(self):
        """The embedded composer's input text is readable on the field's own fill.

        The textarea carries ``o-discuss-text-body``, so its colour is core's bare-class
        ``!important`` rule, and it paints its own fill through ``--mail-Composer-bg``. Fill and
        text are set by different rules, so any coherent pair passes.
        """
        self._assert_core_source_contains(
            "mail/static/src/core/common/composer.xml",
            ("o-mail-Composer-input o-mail-Composer-bg", "o-discuss-text-body"),
            "The composer textarea does not carry those classes, so the element model below is "
            "keyed on markup core stopped rendering - re-transcribe it from composer.xml.",
        )
        css = self._compiled_css(DARK_BUNDLE)
        chain = _element_chain(COMPOSER_INPUT_CLASSES, ISLAND_COMPOSER_INPUT_LAYERS)

        _depth, field_value, field_rgb = self._island_rendered_surface(
            css, chain, "spreadsheet island composer field"
        )
        text_value, text_rgb = self._island_inherited_colour(
            css, chain, "spreadsheet island composer text"
        )
        ratio = _contrast_ratio(text_rgb, field_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "Inside the spreadsheet light island the composer input renders its text %s on the "
            "field fill %s (rgb%r) - only %.2f:1, where WCAG AA normal text needs >= %.1f:1. The "
            "textarea carries `o-discuss-text-body` (composer.xml:77), whose bare-class "
            "`!important` (core.dark.scss:13-15) no normal island rule can outrank, and it paints "
            "its own fill through `--mail-Composer-bg` (composer.scss:103-105). Both halves have to "
            "be set for the field to be typable."
            % (text_value, field_value, field_rgb, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_spreadsheet_island_empty_message_placeholder_clears_aa_on_every_surface(self):
        """The contentless-message placeholder is readable on every surface the island paints.

        ``.opacity-75`` dims the island's muted tier toward a light surface, so the dimming must be
        cancelled or the tier re-pointed.
        """
        self._assert_readable_on_every_message_surface(
            DARK_BUNDLE,
            _element_chain(MESSAGE_EMPTY_PLACEHOLDER_CLASSES, ISLAND_MESSAGE_BODY_MUTED_LAYERS,
                           tag=MESSAGE_EMPTY_PLACEHOLDER_TAG),
            "spreadsheet island empty-message placeholder",
            "Inside the light island the placeholder is the muted tier dimmed a second time by "
            "`opacity-75` (message.xml:110). Cancel the multiplier or re-point the tier; the floor "
            "is the same one every other island surface is held to.",
            panel_label="the island panel",
        )

    def test_dark_spreadsheet_island_edited_marker_clears_aa_on_every_surface(self):
        """The ``(edited)`` marker is readable on every surface the island paints.

        The marker inherits the island body tier and its opacity is its whole de-emphasis, so it is
        thinned only as far as AA allows rather than flattened to body copy.
        """
        self._assert_readable_on_every_message_surface(
            DARK_BUNDLE,
            _element_chain(MESSAGE_EDITED_MARKER_CLASSES, ISLAND_EDITED_MARKER_LAYERS,
                           tag=MESSAGE_EDITED_MARKER_TAG),
            "spreadsheet island (edited) marker",
            "Inside the light island `opacity-50` (message.xml:152) halves the island body tier "
            "this marker inherits. Thin it less or re-point what it inherits; flattening it to 100% "
            "removes the de-emphasis rather than fixing the contrast.",
            panel_label="the island panel",
        )

    def test_island_chatter_surface_and_body_text_are_the_engines_light_tones(self):
        """The embedded Chatter renders its body text in the engine's own tone on the engine's white.

        The values are asserted as stated, not as whatever the compile emits.
        """
        css = self._compiled_css(DARK_BUNDLE)
        chain = _element_chain(CHATTER_ROOT_CLASSES, ISLAND_PANEL_LAYERS)
        _depth, surface_value, surface_rgb = self._island_rendered_surface(
            css, chain, "island chatter surface"
        )
        self.assertEqual(surface_value.lower(), ISLAND_SURFACE)
        body_chain = _element_chain(MESSAGE_BODY_CLASSES, ISLAND_TEXT_BODY_LAYERS)
        body_value, body_rgb = self._island_inherited_colour(
            css, body_chain, "island message body text"
        )
        self.assertEqual(body_value.lower(), ISLAND_BODY_TEXT)
        self.assertGreaterEqual(_contrast_ratio(body_rgb, surface_rgb), 10.3)

    def test_island_composer_buttons_clear_aa_in_every_state(self):
        """Every composer button label clears AA on its own fill: idle, hover, active, disabled.

        Both the label core forces on island ``.btn`` and the label the island declares per state
        are measured on the fill of the same state; the open composer toggles paint their fill
        directly and are measured too.
        """
        css = self._compiled_css(DARK_BUNDLE)
        _forced_value, forced_rgb = self._island_forced_button_text()
        states = (
            ("idle", "--btn-bg", "--btn-color"),
            ("hover", "--btn-hover-bg", "--btn-hover-color"),
            ("active", "--btn-active-bg", "--btn-active-color"),
            ("disabled", "--btn-disabled-bg", "--btn-disabled-color"),
        )
        for name, classes, prev_sibling in ISLAND_COMPOSER_BUTTONS:
            chain = _element_chain(classes, ISLAND_TOPBAR_LAYERS, prev_sibling)
            for state, fill_prop, label_prop in states:
                with self.subTest(button=name, state=state):
                    fill_rgb = _opaque_rgb(_computed_value(css, chain, (fill_prop,)))
                    self.assertIsNotNone(fill_rgb, "%s %s fill is not opaque" % (name, state))
                    _label_value, label_rgb = self._resolve_dark_colour(
                        css, _computed_value(css, chain, (label_prop,)),
                        "%s %s label" % (name, state),
                    )
                    for label in (forced_rgb, label_rgb):
                        self.assertGreaterEqual(
                            _contrast_ratio(label, fill_rgb), WCAG_AA_NORMAL_TEXT,
                            "%s %s: label rgb%r on fill rgb%r is under AA."
                            % (name, state, label, fill_rgb),
                        )
        for toggle, classes in ACTIVE_CHATTER_TOGGLE_CLASSES.items():
            with self.subTest(button=toggle, state="open"):
                chain = _element_chain(
                    classes, ISLAND_TOPBAR_LAYERS, CHATTER_TOGGLE_PREV_SIBLING
                )
                fill_rgb = _opaque_rgb(_computed_value(css, chain, BACKGROUND_PROPS))
                self.assertIsNotNone(fill_rgb, "%s open fill is not opaque" % toggle)
                self.assertGreaterEqual(
                    _contrast_ratio(forced_rgb, fill_rgb), WCAG_AA_NORMAL_TEXT,
                    "%s open: the forced label on fill rgb%r is under AA." % (toggle, fill_rgb),
                )

    def test_island_message_bubble_border_stays_perceptible_on_the_surface(self):
        """Each bubble border is at least 1.15:1 against the island surface."""
        css = self._compiled_css(DARK_BUNDLE)
        surface_rgb = _opaque_rgb(ISLAND_SURFACE)
        for variant, classes in sorted(ISLAND_BUBBLE_CLASSES.items()):
            with self.subTest(variant=variant):
                chain = _element_chain(classes, ISLAND_TEXT_BODY_LAYERS)
                border_rgb = _opaque_rgb(_computed_value(css, chain, ("border-color",)))
                self.assertIsNotNone(border_rgb, "%s border is not opaque" % variant)
                self.assertGreaterEqual(
                    _contrast_ratio(border_rgb, surface_rgb), ISLAND_BUBBLE_BORDER_MIN_RATIO,
                    "%s border rgb%r is lost against the island surface." % (variant, border_rgb),
                )

    def _island_state_chain(self, classes, layers, state=None, prev_sibling=frozenset(), tag=None):
        """Return the resolver chain of one island element, optionally in a pseudo-class state."""
        chain = _element_chain(classes, layers, prev_sibling, tag)
        if state:
            chain[0]["states"] = frozenset({state})
        return chain

    def test_island_link_buttons_clear_aa_idle_and_hover_on_the_white_surface(self):
        """A link-style button with a semantic colour class reads on the island's white, idle and hover.

        The engine's white is injected at runtime and no compiled bundle carries it.
        """
        css = self._compiled_css(DARK_BUNDLE)
        surface_rgb = _opaque_rgb(ISLAND_SURFACE)
        subjects = (
            ("delete link", frozenset({"btn", "btn-sm", "btn-link", "text-danger"}), ISLAND_PANEL_LAYERS),
            ("action icon button", frozenset({"btn", "btn-link", "text-action", "px-1"}), ISLAND_TOPBAR_LAYERS),
        )
        for name, classes, layers in subjects:
            for state in (None, "hover"):
                with self.subTest(button=name, state=state or "idle"):
                    chain = self._island_state_chain(classes, layers, state)
                    value = self._resolve(css, chain, ("color",), "%s %s" % (name, state or "idle"))
                    rgb = _opaque_rgb(value)
                    self.assertIsNotNone(rgb, "%s resolves the colour %r, not an opaque one." % (name, value))
                    ratio = _contrast_ratio(rgb, surface_rgb)
                    self.assertGreaterEqual(
                        ratio, WCAG_AA_NORMAL_TEXT,
                        "The %s (%s) renders %s on the island's white - only %.2f:1, where WCAG AA "
                        "normal text needs >= %.1f:1." % (name, state or "idle", value, ratio, WCAG_AA_NORMAL_TEXT),
                    )

    def test_island_followed_followers_button_clears_aa_on_the_white_surface(self):
        """The followers button of a followed record reads on the island's white."""
        css = self._compiled_css(DARK_BUNDLE)
        chain = _element_chain(
            FOLLOWERS_BUTTON_CLASSES,
            (frozenset({"o-mail-Followers", "d-flex", "me-1"}),) + ISLAND_TOPBAR_LAYERS,
            tag="button",
        )
        value = self._resolve(css, chain, ("color",), "followers button")
        rgb = _opaque_rgb(value)
        self.assertIsNotNone(rgb, "The followers button resolves %r, not an opaque colour." % value)
        ratio = _contrast_ratio(rgb, _opaque_rgb(ISLAND_SURFACE))
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The followed followers button renders %s on the island's white - only %.2f:1, where "
            "WCAG AA normal text needs >= %.1f:1." % (value, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_island_panel_buttons_clear_aa_in_every_state(self):
        """The Bootstrap buttons of an editor side panel clear AA on their own fill: idle, hover, active.

        The outline variant paints no fill at rest, so its resting surface is the island's white.
        Disabled controls are exempt from WCAG 1.4.3 and not asserted.
        """
        css = self._compiled_css(DARK_BUNDLE)
        _forced_value, forced_rgb = self._island_forced_button_text()
        surface_rgb = _opaque_rgb(ISLAND_SURFACE)
        layers = (frozenset({"btn-group", "mb-3"}),) + ISLAND_PANEL_LAYERS
        states = (
            ("idle", "--btn-bg", "--btn-color"),
            ("hover", "--btn-hover-bg", "--btn-hover-color"),
            ("active", "--btn-active-bg", "--btn-active-color"),
        )
        for name, classes in (
            ("primary toggle", frozenset({"btn", "btn-sm", "btn-primary"})),
            ("outline toggle", frozenset({"btn", "btn-sm", "btn-outline-primary"})),
            ("secondary button", frozenset({"btn", "btn-sm", "btn-secondary"})),
        ):
            chain = _element_chain(classes, layers)
            for state, fill_prop, label_prop in states:
                with self.subTest(button=name, state=state):
                    fill_rgb = _opaque_rgb(_computed_value(css, chain, (fill_prop,))) or surface_rgb
                    _label_value, label_rgb = self._resolve_dark_colour(
                        css, _computed_value(css, chain, (label_prop,)), "%s %s label" % (name, state),
                    )
                    for label in (forced_rgb, label_rgb):
                        self.assertGreaterEqual(
                            _contrast_ratio(label, fill_rgb), WCAG_AA_NORMAL_TEXT,
                            "%s %s: label rgb%r on fill rgb%r is under AA." % (name, state, label, fill_rgb),
                        )

    def test_island_delivery_failure_icon_clears_the_non_text_floor(self):
        """The delivery-failure envelope of a message reads on the island's white at the non-text floor.

        The icon is ``text-danger opacity-75``; the composited ink is measured against the surface.
        """
        css = self._compiled_css(DARK_BUNDLE)
        chain = _element_chain(
            frozenset({"fa", "fa-envelope", "text-danger", "opacity-75"}), ISLAND_MESSAGE_LAYERS, tag="i",
        )
        value = self._resolve(css, chain, ("color",), "delivery-failure icon")
        rgb = _opaque_rgb(value)
        self.assertIsNotNone(rgb, "The icon resolves %r, not an opaque colour." % value)
        opacity = _to_alpha(_normalize_value(_computed_value(css, chain, ("opacity",)) or "1"))
        surface_rgb = _opaque_rgb(ISLAND_SURFACE)
        ratio = _contrast_ratio(_composite(rgb, surface_rgb, opacity), surface_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NON_TEXT,
            "The delivery-failure icon renders %s at opacity %s on the island's white - only %.2f:1, "
            "where WCAG 1.4.11 needs >= %.1f:1." % (value, opacity, ratio, WCAG_AA_NON_TEXT),
        )
