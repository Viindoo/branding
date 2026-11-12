# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Compiled-render contrast guards for the mail Chatter embedded in the spreadsheet editor's side
# panel (the editor is a LIGHT ISLAND inside the dark app).
#
# Core re-lights the editor subtree in the dark bundle (`color-scheme: light`, `.bg-white`,
# `.border*`, and `.o-spreadsheet .btn { color: <light label> }`, (0,2,0), no `!important`) but
# repaints the LABEL only, never a fill or a surface. A Chatter dropped into the side panel would
# therefore serve its labels from the light scheme and everything behind them from the dark one.
# spreadsheet_chatter_island.dark.scss switches the embedded Chatter to the island's light scheme,
# reading the engine's own `$os-*` tokens; these guards hold the pairs it must keep.
#
# Every assertion measures the WCAG 2.x ratio of the COMPILED dark-bundle colours against a fixed
# threshold, resolved through the cluster's cascade resolver over the real ancestor chain, so a
# later re-tune that still clears the threshold is not a false alarm. Nothing here needs the
# spreadsheet editor mounted: the ancestor chain is a list of class strings and the one core value
# that is read (the forced label) comes off the addons path with `file_open`.
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

# The island surface and body text: the engine's own white and `$os-text-body` (10.3:1).
ISLAND_SURFACE = "#ffffff"
ISLAND_BODY_TEXT = "#374151"
# A bubble's border must stay perceptible against the island surface without becoming a frame.
ISLAND_BUBBLE_BORDER_MIN_RATIO = 1.15

CORE_SPREADSHEET_DARK_SCSS = "spreadsheet/static/src/o_spreadsheet/o_spreadsheet_extended.dark.scss"

# The `.btn` block nested inside that file's `.o-spreadsheet { ... }` wrapper. Anchored at the start
# of a line so the `.badge` / `.o_input` blocks around it can never be read instead, and capturing
# the VALUE rather than asserting one: the light-island label is core's design decision, and if core
# re-tunes it the contrast arithmetic below changes with it instead of going stale.
_ISLAND_BUTTON_COLOUR_RE = re.compile(
    r"^\s*\.btn\s*\{[^{}]*?(?<![\w-])color\s*:\s*([^;}]+)", re.MULTILINE | re.DOTALL
)

SPREADSHEET_ISLAND_ROOT = frozenset({"o-spreadsheet"}) | WEBCLIENT_ANCESTORS
SPREADSHEET_SIDE_PANEL = frozenset({"o-sidePanel"})
# The panel root carries NO background utility: the o-spreadsheet engine hardcodes a light-mode text
# colour on its own side panel that Odoo's dark recompile cannot reach, so this layer paints nothing
# and the engine's `.o-sidePanel` shows through. No rule names a business-module class.
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

# chatter.xml:13-30. The RESTING state of a CLOSED composer - the state the collision shows
# in, and the one a user meets on opening a comment thread: "Send message" is the resting
# `.btn-primary`, "Log note" and "Activity" the resting `.btn-secondary`. Each entry carries its
# real preceding sibling, which is load-bearing for the same reason the chatter-toggle model above
# says it is: Bootstrap's `.btn-check:checked + .btn` group (0,3,0) carries no state pseudo-class on
# its subject, and only a real, non-`.btn-check` sibling rules it out.
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

# The `(edited)` marker inside the island. The placeholder's stack is already
# `ISLAND_MESSAGE_BODY_MUTED_LAYERS` (the `Subject:` line shares it); only the marker needs its own.
ISLAND_EDITED_MARKER_LAYERS = _edited_marker_layers(ISLAND_MESSAGE_LAYERS)
ISLAND_COMPOSER_INPUT_LAYERS = COMPOSER_INPUT_CHATTER_LAYERS + ISLAND_PANEL_LAYERS
ISLAND_BUBBLE_CLASSES = MESSAGE_BUBBLE_CLASSES


@tagged("post_install", "-at_install")
class SpreadsheetChatterIslandContrastTest(ContrastCompileHelpers, TransactionCase):
    """The Chatter embedded in the spreadsheet editor reads as part of the editor's light island."""

    def _island_forced_button_text(self):
        """Return ``(value, rgb)`` of the label core forces on every `.btn` inside `.o-spreadsheet`.

        Read out of core's OWN dark stylesheet rather than pinned here: that label is core's
        choice for the light island, this module cannot change it, and reading it keeps the
        arithmetic below correct through a core re-tune instead of measuring a stale literal. It is
        also what makes both guards independent of whether `spreadsheet` is INSTALLED - `file_open`
        resolves a source file off the addons path, never a module registry."""
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
        """Return ``(depth, value, rgb)`` of the DARK-bundle surface an element renders on.

        The ancestor-only reading of :meth:`_rendered_backdrop`, kept as the entry point for the
        island guards whose subjects have no overlay in their subtree."""
        backdrop = self._rendered_backdrop(css, chain, DARK_BUNDLE, label)
        return backdrop.depth, backdrop.value, backdrop.rgb

    def _island_inherited_colour(self, css, chain, label):
        """The dark-bundle reading of :meth:`_inherited_colour`."""
        return self._inherited_colour(css, chain, DARK_BUNDLE, label)

    def test_dark_spreadsheet_island_chatter_buttons_clear_aa_under_the_forced_light_label(self):
        """The embedded Chatter's composer buttons must be readable inside the spreadsheet island.

        THE COLLISION. Core keeps `.o-spreadsheet` a LIGHT island in dark mode and forces
        `.o-spreadsheet .btn { color: <light-island label> }` (0,2,0, no `!important`), which outranks
        Bootstrap's `.btn { color: var(--btn-color) }` (0,1,0) and repaints the LABEL of every button
        in the editor. It does not touch the FILL, so the three composer buttons keep resolving their
        background through the app-wide dark ladder - `.btn-secondary` onto dark_buttons.scss'
        $o-viin-dark-control-bg, `.btn-primary` onto the chrome teal. Each button therefore serves its
        label from the light scheme and its fill from the dark one: Log note and Activity read 1.19:1,
        Send message 2.17:1, while the dark_buttons pairing is 10.95:1 - a mismatched pair, not a
        mis-designed colour.

        WHAT IS ASSERTED, AND WHY NOT A HEX. The rule, not a shade: whatever fill each button
        resolves to inside the island must clear WCAG AA against the label core forces on it. The
        label is read from core's own stylesheet, so a core re-tune moves the arithmetic instead of
        going stale; the fill is resolved through the cluster's cascade resolver over the real
        ancestor chain, so a fix is free to land on the Chatter, the comments panel or the button map
        and free to pick any readable tone. It cannot be satisfied by a different-but-equally-
        unreadable shade, which a pinned hex could not promise.

        WOULD FAIL IF REVERTED: with no island-scoped rule the resolver returns the dark ladder's
        fills, and each ratio lands where the live measurement put it - far under 4.5:1."""
        # The element models are transcribed from this template; assert the transcription is still
        # true, or the guard silently measures buttons core stopped rendering.
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
        """The embedded Chatter's surface must be the island's LIGHT one, readable both ways.

        THE SECOND HALF OF THE SAME DEFECT. The buttons above at least paint their own fill; every
        transparent control in the panel - the cell-address toggle, Resolve, the Chatter's own
        link-style topbar actions - has none, so it renders core's forced light-island label directly
        on whatever the stack behind it paints. The comments panel paints nothing, so the walk
        continues outwards. WHICH layer wins is exactly what this guard refuses to pin. Re-lighting
        the buttons would leave every one of those controls exactly as unreadable, which is why this
        is asserted separately and can fail on its own.

        AND THE TRAP ON THE WAY OUT. Lighting the surface is only half a fix. The message text
        carries the app-wide dark near-white, so a light surface under un-re-pointed text moves the
        unreadability from the buttons to the message body instead of ending it. The pair therefore
        has to be coherent in BOTH directions: a light surface under core's forced dark label, and
        text that stays readable on whatever surface wins.

        WHERE THE TEXT IS READ, AND WHY NOT AT THE CHATTER ROOT. `.o-mail-Message-body` declares no
        colour (message.scss:45-58); it inherits from `.o-discuss-text-body` (message.xml:82), the
        wrapper around it, which core styles as a BARE class with `!important` in both schemes
        (core.scss:99-101, core.dark.scss:13-15). `!important` outranks any normal declaration at any
        specificity, so an island rule on `.o-mail-Chatter` (0,2,0, normal) never reaches this text.
        Resolving `color` at the Chatter root answers for a different element; the body text is
        resolved through :meth:`_island_inherited_colour` over the real message chain, which walks
        outwards from the body and stops at the wrapper that actually declares the winning colour.

        HOW A POSITIONED SIBLING IS ACCOUNTED FOR. `.o-mail-Message-bubble` (message.xml:89) is
        `position-absolute top-0 start-0 w-100 h-100` inside that same wrapper - a preceding SIBLING
        of the body, not an ancestor of it - so it is invisible to any walk that composites only
        ancestor backgrounds, and such a walk reports the panel behind the bubble as the surface. It
        is instead resolved as its OWN element, on the same ancestors as the body, and its fill is
        handed to the arithmetic as the surface for every bubbled variant the island's bubble map
        paints. The no-bubble message keeps the ancestor walk, which is the correct model for it:
        with no bubble in the subtree there is nothing between the glyphs and the panel.

        WOULD FAIL IF REVERTED: with no island-scoped rule the ancestor walk lands on a dark
        surface - the one measured at 1.70:1, or whichever layer paints once the panel does not -
        and the forced-label assertion reports a ratio far under the floor. With the
        surface lit but the text left on core's bare-class `!important`, the body subTests report the
        near-white on the island's own light fills - the coherence half of the same defect."""
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
                # No island-scoped colour reaches the Chatter, so its text inherits from the
                # document body - core's own :root emission is the honest source for that.
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

        # The body text is resolved where it is DECLARED, not where the Chatter is: the walk starts
        # at `.o-mail-Message-body` and stops at the first ancestor carrying a colour, which is the
        # `.o-discuss-text-body` wrapper and its bare-class `!important`.
        body_chain = _element_chain(MESSAGE_BODY_CLASSES, ISLAND_TEXT_BODY_LAYERS)
        body_value, body_rgb = self._island_inherited_colour(
            css, body_chain, "spreadsheet island message body text"
        )

        for variant in sorted(ISLAND_BUBBLE_CLASSES):
            with self.subTest(message_surface=variant):
                # The bubble is obtained through the cluster's ONE painted-sibling model rather than
                # re-derived here: two models of the same overlay drift, and the drift is invisible
                # until it produces the false green this guard exists to prevent.
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
            # A note and a notification carry no bubbleColor (message.xml:89 gates the bubble on
            # it), so for them the ancestor walk IS the right model - nothing is painted between the
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
        """The island's muted secondary tier must clear AA on EVERY surface the island paints under it.

        THE SURFACE, NOT THE TIER, IS WHAT MOVES. The two guards above restored the island's BODY
        tier (#374151-class, 9-10:1 everywhere) and re-lit the three bubbles with core's own LIGHT
        formula. The SECONDARY tier is a second, quieter tier that rides the same surfaces and is set
        by different rules: `.o-mail-Message-date` reads `var(--secondary-color)`, re-pointed on the
        Chatter root, while the in-body `.text-muted` markers are re-pointed by their own
        `!important` rule. A muted tier chosen against the panel alone is a tier chosen against the
        LIGHTEST surface in the island - every bubble is darker than the panel, so a tier that only
        just clears AA on the panel cannot clear it on any of them. That is the whole defect class:
        the model gets the SURFACE wrong, not the colour.

        WHERE EACH SUBJECT IS READ, AND WHY THEY DIFFER. The timestamp lives in
        `.o-mail-Message-header` (message.xml:44 inside :38), a SIBLING of the content container - the
        bubble is `position-absolute` inside `.o-discuss-text-body` several layers further in, so no
        bubble is ever painted behind a timestamp and its surface is the panel the ancestor walk
        lands on. The muted markers core renders INSIDE `.o-mail-Message-body` (:110, :113, :117,
        :120) are inside that wrapper, so on a bubbled message the bubble is the surface under them -
        resolved as its own element, on the same ancestors, exactly as the body text is. Both
        subjects are resolved through the cascade rather than pinned, so a fix is free to land on the
        Chatter token, the `.text-muted` rule or the bubble map, and free to pick any readable tone.

        WOULD FAIL IF REVERTED: a secondary tier tuned only against the island's white panel reads
        4.69:1 there and lands under 4.5:1 on all three bubbles - 4.21:1 blue, 4.23:1 green, 4.49:1
        orange - so the bubble subTests report the shortfall the panel subTests cannot see."""
        # The element models are transcribed from this template; assert the transcription is still
        # true, or the guard silently measures markers core stopped rendering.
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.xml",
            ('class="o-mail-Message-date o-xsmaller"',
             "o-mail-Message-header d-flex flex-wrap align-items-baseline lh-1",
             'class="d-block text-muted smaller">Subject:'),
            "The muted secondary markers do not carry those classes, so the element models below "
            "are keyed on markup core stopped rendering - re-transcribe them from message.xml.",
        )
        css = self._compiled_css(DARK_BUNDLE)

        # Each subject resolves its OWN colour: the timestamp takes the tier through a custom
        # property on an ancestor, the in-body markers through an important rule on themselves. Two
        # rules, one tier - and reading each where it is declared is what lets either half go RED on
        # its own instead of one standing in for the other.
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
                # Same single painted-sibling model as the body guard above - the overlay is
                # declared once and applied by DOM containment, never transcribed per guard.
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
            # A note and a notification carry no bubbleColor (message.xml:89 gates the bubble on it),
            # so their in-body markers keep the ancestor walk - nothing is painted between the glyphs
            # and the panel.
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
        """The embedded composer's input text must be readable on the field's own fill.

        THE SAME BARE-CLASS RULE, A SECOND SURFACE. The textarea at composer.xml:77 carries
        `o-discuss-text-body` ITSELF, so it takes the identical `!important` colour core declares at
        core.dark.scss:13-15 - the app-wide dark near-white. It also paints its OWN fill:
        `.o-mail-Composer-bg` reads `var(--mail-Composer-bg, $o-view-background-color)`
        (composer.scss:103-105), a token the island is free to re-point. Those two halves are set by
        different rules in different files, so lighting the field without re-pointing the text - or
        the reverse - leaves the user typing in a colour they cannot see, and neither of the two
        guards above would notice: this element is not in the message subtree and is not the Chatter
        root either.

        WHAT IS ASSERTED. The rule, not a shade: whatever fill the field resolves to inside the
        island must clear WCAG AA against whatever colour its text resolves to, both read out of the
        compiled dark bundle over the real chain. A fix may light the field, darken the text, or
        re-point the token - any coherent pair passes, and no incoherent one does.

        WOULD FAIL IF REVERTED: with the island lighting `--mail-Composer-bg` and core's bare-class
        `!important` left in place, the near-white text resolves onto the island's light field."""
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
        """The contentless-message placeholder must be readable on the island's light ground too.

        The island keeps a LIGHT ground in dark mode, so the placeholder there is a DARK muted tier
        dimmed toward a light surface - the opposite direction to the dark-palette case, and a
        different arithmetic reaching the same failure. `.opacity-75` composites the island muted
        tier down to a grey that clears AA on none of the four surfaces the island paints; the
        correction cancels the multiplier and lets the node keep its de-emphasis through the tier it
        shares with every other muted marker in the body.

        WOULD FAIL IF REVERTED: without the correction the placeholder reads 3.26:1 on the blue
        bubble, 3.27:1 green, 3.40:1 orange and 3.49:1 on an unbubbled message - under the floor on
        all four."""
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
        """The `(edited)` marker must stay readable on the island's light ground too.

        Unlike the placeholder the marker has no tier of its own - it inherits the island body text
        and the 50% IS its whole de-emphasis - so flattening it is not an option: at full opacity it
        would be body copy in a smaller size. The rule thins it to the least Bootstrap rung
        that still clears AA on every bubble, which keeps a visible quarter of thinning while the
        0.65rem size carries the rest.

        WOULD FAIL IF REVERTED: without the correction the marker reads 2.54:1 on the blue bubble,
        2.55:1 green, 2.60:1 orange and 2.63:1 on an unbubbled message - roughly half the floor
        everywhere."""
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
        """The embedded Chatter renders its body text on the island's white surface.

        The pair is the engine's own: a white panel carrying `$os-text-body`, 10.3:1. The values are
        asserted as stated, not as whatever the compile happens to emit.

        WOULD FAIL IF REVERTED: with no island rule the Chatter inherits the dark scheme, and
        both the surface and the body text resolve to dark-scheme tones."""
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

        The label is the one core forces on every island `.btn`, and the one the island declares
        per state; both are measured on the fill the same state resolves to. The open composer
        toggles paint their fill directly and are measured as well.

        WOULD FAIL IF REVERTED: a state whose fill stays on the dark scheme's control rung puts
        the light-island label on a dark fill."""
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
        """Each bubble border is >= 1.15:1 against the island surface.

        WOULD FAIL IF REVERTED: a border that mixes into the white surface vanishes, and the
        bubble loses its edge.

        :raises AssertionError: when a variant's border is not an opaque colour"""
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
        """Resolver chain of one island element, optionally in a pseudo-class state."""
        chain = _element_chain(classes, layers, prev_sibling, tag)
        if state:
            chain[0]["states"] = frozenset({state})
        return chain

    def test_island_link_buttons_clear_aa_idle_and_hover_on_the_white_surface(self):
        """A link-style button that carries a semantic colour class reads on the island's white.

        Core's dark file paints `.btn-link.text-danger` and `.btn-link.text-action` with the dark
        scheme's muted tone (idle) and a dark-ground tint (hover), both important - a tone chosen for
        a dark panel, on the island's white surface. The island states its own tones, so each pair is
        measured as the cascade resolves it at the fixed AA threshold. The surface is the engine's
        own white, which the editor injects at runtime and no compiled bundle carries.

        WOULD FAIL IF REVERTED: the dark muted tone reads 2.59:1 on white."""
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
        """The followers button of a followed record reads on the island's white.

        The dark scheme paints the followed state with a light teal chosen for the dark chatter; the
        island's own white surface needs its AA teal.

        WOULD FAIL IF REVERTED: the dark-ground teal reads 1.77:1 on white."""
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

        Core forces the label of every button in the editor to the engine's body tone, so a primary
        or outline toggle in a panel needs a light fill like the Chatter's own buttons. The outline
        variant paints no fill at rest, so its resting surface is the island's white.

        WOULD FAIL IF REVERTED: the label reads 2.17:1 on the brand teal of a primary toggle.
        Disabled controls are exempt from WCAG 1.4.3 and not asserted."""
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
        """The delivery-failure envelope of a message reads on the island's white.

        It is `text-danger opacity-75`: the dark scheme's lightened danger tint thinned again by the
        important utility. The island states its own danger tone and returns the opacity to 100%,
        measured as the composited ink against the white surface at the non-text floor.

        WOULD FAIL IF REVERTED: the thinned dark-ground tint reads 2.20:1 on white."""
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
