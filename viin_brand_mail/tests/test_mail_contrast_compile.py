# Compiled-render contrast guards for the viin_brand_mail chrome. Each test measures the WCAG 2.x
# contrast ratio of the compiled colours against the surface they render on, so a swapped-in but
# equally unreadable shade cannot pass a literal-hex comparison.
#
# Rules are read from the compiled bundle the way a browser resolves them: the last matching
# declaration wins, a rule demanding an ancestor class the element lacks is dropped, and a custom
# property is resolved through the core rule that reads it, so a core rename turns the guard red.
import collections
import os
import re

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.misc import file_open

try:
    # The cluster's single cascade resolver and ancestor model, imported rather than copied. Only
    # private helpers are imported: a TestCase class would re-run that suite under this module.
    from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
        _computed_value,
        _selector_scope_applies,
        _winning_declaration,
    )
except ImportError:
    _computed_value = _winning_declaration = _selector_scope_applies = None

try:
    # The stock neutral button model, to compare the open "Log note" toggle against a real
    # `.btn-secondary` resolved in the same bundle.
    from odoo.addons.viin_brand.tests.test_brand_cascade_compile import (
        PAGER_ANCESTORS,
        PAGER_PREVIOUS_CLASSES,
    )
except ImportError:
    PAGER_ANCESTORS = PAGER_PREVIOUS_CLASSES = None

try:
    # Odoo's own SCSS asset class, used to re-compile a bundle with one extra spliced line.
    from odoo.addons.base.models.assetsbundle import ScssStylesheetAsset
except ImportError:
    ScssStylesheetAsset = None

# `$o-viin-chrome-base` (viin_brand/static/src/scss/brand_variables.scss): the teal of the frame of
# the application (the navbar, the chat-window header); white on it is 4.74:1.
CHROME_BASE = "#007f8e"

# `$o-brand-primary`: the brand purple every content, interactive and glyph surface resolves to;
# white on it is 6.99:1.
BRAND_PURPLE = "#7f4282"

# `$o-viin-action-deep`: the pressed / open tone of the content. The chatter's open "Send message"
# toggle uses it because the brand purple is already that button's resting fill.
ACTION_DEEP = "#592e5b"
# The dark scheme's content colour is the brand cyan, and its deep rung is the cyan 15% toward black.
BRAND_CYAN = "#00bbce"
DARK_ACTION_DEEP = "#009faf"

# The dark muted tier (`$body-secondary-color` in dark_palette.scss): only 2.59:1 under core's
# forced-white badge label, so the Discuss badge needs its own dark arm.
DARK_MUTED_TIER = "#8ea5a8"

# The brand cyan, a decoration in the light scheme (2.33:1 on white): it must never carry a glyph
# or a fill under text.
FLAT_BRAND_CYAN = "#00bbce"

# The chat-window header fill the header must not use: `mix(black, $o-brand-primary, 15%)`.
FORBIDDEN_HEADER_PURPLE = "#6c386f"

# `$o-success`, core's default `$o-navbar-badge-bg`: white counter text on it is 2.75:1.
CORE_SUCCESS_GREEN = "#00b365"
# The identity purple the systray counters take from `$o-navbar-badge-bg`, in both schemes.
IDENTITY_PURPLE = "#7f4282"
# The chat-window header counter: an important `o-discuss-badge` on the teal chrome of the header.
CHAT_WINDOW_COUNTER_CLASSES = frozenset({
    "o-mail-ChatWindow-counter", "mx-1", "badge", "rounded-pill", "fw-bold", "o-discuss-badge",
    "shadow-sm",
})
CHAT_WINDOW_HEADER_ANCESTORS = frozenset({
    "o_web_client", "o-mail-ChatWindow", "o-mail-ChatWindow-header",
})

# `$o-viin-status-away` (viin_brand, brand_variables.scss), asserted as a literal rather than
# re-derived from `darken(#ffa500, 15%)`. The dot and the picker swatch read that one variable so
# they cannot drift apart.
AWAY_AMBER = "#b27400"
# The success fill $o-success, the text colour of the online and bot glyph.
SUCCESS_GREEN = "#00884d"
# Values idle must not regress to, asserted negatively: the flat orange (1.97:1 on white) and a
# lighter amber that fails on the focused dropdown row.
FLAT_AWAY_ORANGE = "#ffa500"
LIGHTER_AWAY_AMBER = "#cc8400"
# Core's untouched `.o-yellow { color: $yellow }`: what renders when this module's two rules
# stop matching (1.63:1 on white).
CORE_YELLOW = "#ffc107"

# The surfaces the idle glyph renders on, each re-asserted against core's source by the guard that
# uses it: the view surface is pure white; the dropdown menu is `$dropdown-bg` = `var(--body-bg)`
# in the backend; the focused row is core's `rgba($black, 0.08)` wash over that menu
# (248*0.92 = 228.16, 249*0.92 = 229.08, 250*0.92 = 230 -> #e4e5e6).
WHITE_SURFACE = "#ffffff"
DROPDOWN_MENU_SURFACE = "#f8f9fa"
DROPDOWN_ROW_FOCUS_SURFACE = "#e4e5e6"

# WCAG 2.x thresholds: normal text needs >= 4.5:1, large (bold) text and a meaningful non-text
# indicator (1.4.11) >= 3:1.
WCAG_AA_NORMAL_TEXT = 4.5
WCAG_AA_NON_TEXT = 3.0
WCAG_AA_LARGE_TEXT = 3.0

# A divider must stay perceptible without glaring: the floor keeps a Discuss seam from vanishing
# into the panel, the ceiling keeps it from reading as a bright rule like the untouched light-mode
# grey (13.3:1).
DISCUSS_SEAM_MIN_RATIO = 1.2
DISCUSS_SEAM_MAX_RATIO = 2.0

# `background` and `background-color` are one property family: the shorthand resets the colour.
BACKGROUND_PROPS = ("background-color", "background")

BACKEND_BUNDLE = "web.assets_backend"

# `web.assets_web_dark` is `web.assets_web` plus core's `web/static/src/**/*.dark.scss`; viin_brand's
# dark_palette.scss redefines the surface, text and border Sass variables there, so mail surfaces
# reading an overridable variable recompile dark-correct.
DARK_BUNDLE = "web.assets_web_dark"
# The lazy-loaded views (activity, pivot, graph...) are compiled into their own dark bundle, which
# holds no media chrome: `$light` / `$dark` follow the dark ramp there.
LAZY_DARK_BUNDLE = "web.assets_backend_lazy_dark"
# The mail-owned dark rules reach the dark bundle only through an explicit manifest entry (core's
# dark glob is web/mail-only), so their wiring is guarded structurally.
DARK_SURFACE_SOURCE = "viin_brand_mail/static/src/scss/mail_dark.scss"

# A translucent `rgba(r, g, b, a)` wash (a < 1) in a compiled value.
_RGBA_ALPHA_RE = re.compile(r"rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*([0-9.]+%?)\s*\)")
_VAR_REF_RE = re.compile(r"var\(\s*--([\w-]+)\s*(?:,[^)]*)?\)")
# One non-nested `selectors { body }` rule; rules wrapped in @media are captured individually.
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
_BACKGROUND_RE = re.compile(r"background(?:-color)?\s*:\s*([^;]+)", re.IGNORECASE)
# The lookbehind keeps a plain `color` from matching `background-color`, `border-color` or
# `--btn-color`.
_COLOR_RE = re.compile(r"(?<![\w-])color\s*:\s*([^;]+)", re.IGNORECASE)
# `border-color` and `border-<side>-color`, kept apart from `_COLOR_RE`, whose lookbehind excludes them.
_BORDER_COLOR_RE = re.compile(
    r"border(?:-(?:top|right|bottom|left))?-color\s*:\s*([^;]+)", re.IGNORECASE
)


def _custom_property_re(name):
    """Return a regex capturing the value of the CSS custom property ``--<name>``.

    The ``\\s*:`` guard keeps ``--btn-color`` from matching ``--btn-color-rgb``."""
    return re.compile(r"--%s\s*:\s*([^;}]+)" % re.escape(name))


def _normalize_value(value):
    """Lower-case a declaration value, drop `!important` and collapse whitespace.

    Selectors keep their case: a mis-cased class selector must fail the match."""
    return re.sub(r"\s+", " ", value.replace("!important", "")).strip().lower()


def _iter_rules(css):
    """Yield ``(selector_tokens, body)`` for every compiled rule, in document order."""
    for selectors, body in _RULE_RE.findall(css):
        # Bundle fragments start with a `/* <source-url> */` banner that `_RULE_RE` glues to the
        # first selector group; it is stripped before selector matching.
        tokens = [
            re.sub(r"\s+", " ", token).strip()
            for token in re.sub(r"/\*.*?\*/", "", selectors, flags=re.DOTALL).split(",")
        ]
        yield [token for token in tokens if token], body


# The ancestor pool passed when an element's chain is not modelled: no context is claimed, so every
# rule whose subject matches is returned. A required argument rather than a default, so each use
# stays visible.
ANY_ANCESTORS = None


def _rules_in_scope(css, ancestors):
    """Yield ``(selector_tokens, body)`` for the compiled rules that can reach the element.

    :param ancestors: class names on the element's ancestor chain, or ``ANY_ANCESTORS``
    :return: each rule reduced to the selectors ``ancestors`` satisfies; a rule left with none is
        dropped, so reading the last declaration reads the last one a browser would apply
    """
    for tokens, body in _iter_rules(css):
        if ancestors is ANY_ANCESTORS:
            yield tokens, body
            continue
        in_scope = [token for token in tokens if _selector_scope_applies(token, ancestors)]
        if in_scope:
            yield in_scope, body


def _bodies_matching(css, selector_matches, ancestors):
    """Return, in document order, the bodies of in-scope rules with a selector satisfying the
    predicate; ``ancestors`` is the element's ancestor pool or ``ANY_ANCESTORS``."""
    return [
        body for tokens, body in _rules_in_scope(css, ancestors)
        if any(map(selector_matches, tokens))
    ]


def _selector_subject(selector):
    """Return the compound a rule styles: the rightmost compound of ``selector`` with any
    functional-pseudo argument (``:has()``/``:is()``/``:where()``/``:not()``) stripped.

    A rule such as ``.o-mail-Chatter-top:has(.o-mail-Chatter-sendMessage.active) .o-mail-Composer``
    styles the composer, so it must not be read as the send button's own fill."""
    stripped = re.sub(r":(?:has|is|where|not)\([^)]*\)", "", selector)
    return re.split(r"\s*[>+~]\s*|\s+", stripped.strip())[-1]


def _declared_values(bodies, pattern):
    """Return every normalised value the pattern declares across ``bodies``, in document order."""
    return [_normalize_value(match.group(1)) for body in bodies for match in pattern.finditer(body)]


def _declared_hexes(bodies, pattern):
    """Return the lower-cased hex literals declared by ``pattern`` across ``bodies``, in order."""
    return [
        hex_literal.lower()
        for value in _declared_values(bodies, pattern)
        for hex_literal in re.findall(r"#[0-9A-Fa-f]{3,8}", value)
    ]


def _to_alpha(value):
    """Parse a CSS opacity value (``1``, ``.5``, ``50%``) into a float; return None if it is not one."""
    value = value.strip().lower()
    try:
        return float(value[:-1]) / 100.0 if value.endswith("%") else float(value)
    except ValueError:
        return None


def _to_rgb(value):
    """Parse a CSS colour literal into ``(r, g, b)``; return None when it is not a plain colour."""
    value = value.strip().lower()
    if value == "white":
        value = "#ffffff"
    short_hex = re.fullmatch(r"#([0-9a-f]{3})", value)
    if short_hex:
        value = "#" + "".join(digit * 2 for digit in short_hex.group(1))
    full_hex = re.fullmatch(r"#([0-9a-f]{6})", value)
    if full_hex:
        digits = full_hex.group(1)
        return tuple(int(digits[start:start + 2], 16) for start in (0, 2, 4))
    functional = re.fullmatch(
        r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,[^)]+)?\)", value.replace(" ", "")
    )
    if functional:
        return tuple(int(channel) for channel in functional.groups())
    return None


def _relative_luminance(rgb):
    """WCAG 2.x relative luminance of an sRGB triplet (www.w3.org/TR/WCAG21/#dfn-relative-luminance)."""
    linear = []
    for raw_channel in rgb:
        channel = raw_channel / 255.0
        linear.append(channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first_rgb, second_rgb):
    """WCAG 2.x contrast ratio between two opaque sRGB colours (order-independent)."""
    luminances = (_relative_luminance(first_rgb), _relative_luminance(second_rgb))
    return (max(luminances) + 0.05) / (min(luminances) + 0.05)


def _rgb_distance(first_rgb, second_rgb):
    """Return the squared Euclidean distance between two sRGB triplets.

    No square root: only the ordering is compared, to state that one surface is closer to a colour
    than another."""
    return sum((first - second) ** 2 for first, second in zip(first_rgb, second_rgb))


def _root_custom_property(css, name):
    """Return the last value declared for ``--<name>`` on a ``:root`` rule, or None.

    Reads core's own emission of the theme tokens (``--danger``, ``--body-color``), which the
    class-based cascade resolver does not model."""
    values = []
    pattern = _custom_property_re(name)
    for tokens, body in _iter_rules(css):
        if not any(token == ":root" or token.startswith(":root") for token in tokens):
            continue
        for match in pattern.finditer(body):
            values.append(_normalize_value(match.group(1)))
    return values[-1] if values else None


# Core dims the composer placeholder with its own `::placeholder { opacity }` rules (mail's
# composer.scss): read, never assumed.
_COMPOSER_PLACEHOLDER_SELECTOR = "o-mail-Composer-input::placeholder"


def _composite(foreground_rgb, background_rgb, alpha):
    """Return the opaque colour a foreground at ``alpha`` opacity paints over a background.

    Source-over compositing, as a browser applies ``opacity``."""
    return tuple(
        round(foreground * alpha + background * (1 - alpha))
        for foreground, background in zip(foreground_rgb, background_rgb)
    )


def _injected_sources(assets, bundle_name):
    """Return every asset source path a manifest bundle injects, whatever the operation form
    (bare string, ``(directive, source)`` or ``(directive, anchor, source)``)."""
    sources = set()
    for operation in assets.get(bundle_name, []):
        if isinstance(operation, str):
            sources.add(operation)
        elif isinstance(operation, (tuple, list)) and operation:
            sources.add(operation[-1])
    return sources


WHITE_RGB = (255, 255, 255)


# Element models: each surface is its own classes plus the union of its ancestors' classes, read
# off the core template that renders it. Pools are generous: an extra ancestor can only add a
# competing rule and make a guard fail loudly, never hide the override that broke the surface.

# mail's chatter.xml: the active toggle is `btn-primary active` (sendMessage for a message
# composer, logNote for a note); the resting `btn-secondary` is not under test.
CHATTER_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o-mail-Chatter", "o-mail-Chatter-top", "o-mail-Chatter-topbar",
    "bg-inherit", "d-flex", "flex-column", "position-sticky", "overflow-x-auto",
})
ACTIVE_CHATTER_TOGGLE_CLASSES = {
    ".o-mail-Chatter-sendMessage": frozenset({
        "o-mail-Chatter-sendMessage", "btn", "text-nowrap", "me-1", "btn-primary", "active", "my-2",
    }),
    ".o-mail-Chatter-logNote": frozenset({
        "o-mail-Chatter-logNote", "btn", "text-nowrap", "me-1", "btn-primary", "active", "my-2",
    }),
}
# The two toggles are each other's immediate siblings and neither is a `.btn-check`. Without a real
# previous sibling, Bootstrap's `.btn-check:checked + .btn` (no state pseudo-class in its subject,
# specificity (0,3,0)) would outrank `.btn.active` and hand the query the checked value.
CHATTER_TOGGLE_PREV_SIBLING = frozenset({
    "o-mail-Chatter-sendMessage", "o-mail-Chatter-logNote", "btn", "text-nowrap", "me-1",
})

# `.o-mail-Composer` renders in the chatter (inside `.o-mail-Chatter-top`, which core's `:has()`
# danger-cue selector keys on), in Discuss and in the chat window. The pool is the union of the
# three chains: an extra ancestor can only add a competing rule and make a guard fail loudly.
COMPOSER_ANCESTORS = CHATTER_ANCESTORS | frozenset({
    "o_action_manager",
    "o-mail-Discuss", "o-mail-DiscussContent", "o-mail-DiscussContent-main",
    "o-mail-DiscussContent-core", "o-mail-ChatWindow",
    "h-100", "w-100", "flex-grow-1", "flex-shrink-0", "o-min-width-0", "fixed-bottom", "shadow",
    "bg-100", "overflow-auto", "overflow-hidden", "o-scrollbar-thin",
})

# `.o-mail-Message-bubble` is the absolutely-positioned wash behind a message's text: Message >
# Message-core > Message-contentContainer > Message-content > Message-textContent >
# `.o-discuss-text-body`, in a thread reached from Discuss or from a form view's chatter (the union).
MESSAGE_BUBBLE_ANCESTORS = frozenset({
    "o_web_client", "o_action_manager", "o_form_view",
    "o-mail-Discuss", "o-mail-DiscussContent", "o-mail-DiscussContent-main",
    "o-mail-DiscussContent-core", "o-mail-Chatter", "o-mail-Chatter-content", "o-mail-Thread",
    "o-mail-Message", "o-mail-Message-core", "o-mail-Message-contentContainer",
    "o-mail-Message-content", "o-mail-Message-textContent", "o-discuss-text-body",
    "o-rounded-bubble", "o-rounded-bottom-bubble", "o-rounded-start-bubble",
    "o-rounded-end-bubble", "position-relative", "d-flex", "flex-column", "flex-grow-1",
    "bg-inherit", "overflow-auto", "o-scrollbar-thin", "overflow-x-auto", "overflow-y-hidden",
    "d-inline-block", "o-min-width-0", "w-100", "rounded-0",
})

# The systray counter is `<span class="o-mail-*-counter badge rounded-pill">` inside
# `.o_main_navbar > .o_menu_systray`; `badge` is what core's navbar consumer keys on.
SYSTRAY_ANCESTORS = frozenset({
    "o_web_client", "o_main_navbar", "o_menu_systray", "dropdown", "dropdown-toggle",
    "o-mail-MessagingMenuInDropdown", "o-mail-ActivityMenu",
})
SYSTRAY_COUNTER_CLASSES = {
    ".o-mail-MessagingMenuInDropdown-counter": frozenset({
        "o-mail-MessagingMenuInDropdown-counter", "badge", "rounded-pill",
    }),
    ".o-mail-ActivityMenu-counter": frozenset({
        "o-mail-ActivityMenu-counter", "badge", "rounded-pill",
    }),
}

# The chat-window header and its "more actions" toggle
# (`<button class="o-mail-ChatWindow-moreActions btn ...">`).
CHAT_WINDOW_HEADER_ELEMENT = frozenset({
    "o-mail-ChatWindow-header", "d-flex", "align-items-center", "flex-shrink-0", "bg-100", "z-1",
    "border-bottom", "border-secondary",
})
CHAT_WINDOW_ANCESTORS = frozenset({
    "o_web_client", "o-mail-ChatWindow", "fixed-bottom", "overflow-hidden", "d-flex",
    "flex-column", "shadow", "bg-100",
})
CHAT_WINDOW_HEADER_ANCESTORS = CHAT_WINDOW_ANCESTORS | CHAT_WINDOW_HEADER_ELEMENT | {
    "text-truncate", "bg-inherit",
}
CHAT_WINDOW_MORE_ACTIONS_CLASSES = frozenset({
    "o-mail-ChatWindow-moreActions", "btn", "rounded-0", "d-flex", "align-items-center",
    "o-ps-1_5", "pe-0", "py-1", "my-0", "w-100", "rounded-end-0", "bg-inherit", "rounded-top-3",
})

# The unread counter of a Discuss conversation row (an important `NotificationItem` badge), chosen
# over the other `.o-discuss-badge` sites because core deliberately overrides two of them at higher
# specificity (a non-`.o-important` NotificationItem badge, the messaging menu's tab-unread dot).
# `o-muted` is absent on purpose: core keeps a muted counter grey.
DISCUSS_SIDEBAR_ANCESTORS = frozenset({
    "o_web_client", "o-mail-Discuss", "o-mail-DiscussApp-sidebar", "o-mail-MessagingMenu",
    "o-mail-MessagingMenuItem", "o-mail-NotificationItem", "list-group-item",
})
DISCUSS_UNREAD_BADGE_CLASSES = frozenset({
    "o-mail-NotificationItem-badge", "o-mail-NotificationItem-counter", "o-discuss-badge",
    "o-important", "badge", "rounded-pill", "shadow-sm", "fw-bold", "d-flex", "flex-shrink-0",
})

# `<span class="o-mail-MessageSeenIndicator position-relative">` plus `o-hasEveryoneSeen opacity-75`
# once every member has seen the message: the first keys core's colour rule, the second dims the
# glyph, so this surface is asserted on its composited value.
MESSAGE_SEEN_ANCESTORS = frozenset({
    "o_web_client", "o-mail-Thread", "o-mail-Message", "o-mail-Message-seenContainer",
    "position-absolute",
})
MESSAGE_SEEN_EVERYONE_CLASSES = frozenset({
    "o-mail-MessageSeenIndicator", "position-relative", "o-hasEveryoneSeen", "opacity-75",
})

# The idle glyph is `<i class="oi o-mail-ImStatus d-flex o-yellow rounded-circle bg-transparent">`:
# the colour class sits on the glyph element itself, with no wrapper of its own.
IM_STATUS_ANCESTORS = frozenset({"o_web_client"})
# The Away swatch is `<i class="oi o-yellow me-1">` inside a DropdownItem of the
# `o-mail-ImStatusDropdown` menu. `o-mail-ImStatus` is absent on purpose: only the dropdown toggle
# is an ImStatus, so the ImStatus rule must not be credited for the swatch.
IM_STATUS_DROPDOWN_ANCESTORS = frozenset({
    "o_web_client", "o-mail-ImStatusDropdown", "o-dropdown--menu", "dropdown-menu", "show",
    "o-dropdown-item", "dropdown-item", "o-navigable",
})
IDLE_GLYPH_CLASSES = frozenset({
    "oi", "o-mail-ImStatus", "d-flex", "o-yellow", "rounded-circle", "bg-transparent",
})
IDLE_SWATCH_CLASSES = frozenset({"oi", "o-yellow", "me-1"})


# A compiled `rgb()`/`rgba()` value with its alpha slot captured whole. Odoo's `o-print-color`
# mixin emits the `bg-*` utilities as `RGBA(r, g, b, var(--bg-opacity, 1))`, which `_to_rgb`
# cannot read.
_RGB_FUNCTIONAL_RE = re.compile(
    r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(.+?)\s*)?\)", re.IGNORECASE
)

# Values that paint nothing at all, so the element shows whatever its ancestors paint.
_NON_PAINTING_VALUES = frozenset({
    "transparent", "inherit", "initial", "unset", "revert", "none", "currentcolor",
})


def _alpha_slot(text):
    """Parse the alpha slot of a compiled ``rgb()``/``rgba()`` value into a float, or None.

    Reads the bare number Sass emits and the ``var(--<token>, <fallback>)`` form of
    ``o-print-color``, which resolves to its fallback absent a ``.bg-opacity-*`` utility.

    :return: None for a slot that cannot be resolved, which :func:`_opaque_rgb` treats as not
        provably opaque
    """
    text = text.strip().lower()
    var_fallback = re.fullmatch(r"var\(\s*--[\w-]+\s*,\s*([^()]+)\)", text)
    if var_fallback:
        text = var_fallback.group(1).strip()
    return _to_alpha(text)


def _opaque_rgb(value):
    """Return ``(r, g, b)`` when ``value`` paints a fully opaque colour, else None.

    Unlike :func:`_to_rgb`, which ignores the alpha of an ``rgba()``, anything translucent,
    unresolvable or non-painting reads as "keep looking outwards"."""
    if value is None:
        return None
    text = re.sub(r"\s+", " ", value.strip())
    if not text or text.lower() in _NON_PAINTING_VALUES:
        return None
    functional = _RGB_FUNCTIONAL_RE.fullmatch(text)
    if functional:
        alpha_slot = functional.group(4)
        alpha = 1.0 if alpha_slot is None else _alpha_slot(alpha_slot)
        if alpha is None or alpha < 1.0:
            return None
        return tuple(int(channel) for channel in functional.groups()[:3])
    return _to_rgb(text)


WEBCLIENT_ANCESTORS = frozenset({"o_web_client", "o_action_manager"})
CHATTER_ROOT_CLASSES = frozenset({
    "o-mail-Chatter", "w-100", "h-100", "flex-grow-1", "d-flex", "flex-column", "bg-inherit",
})
CHATTER_TOP_CLASSES = frozenset({"o-mail-Chatter-top", "d-print-none", "position-sticky", "top-0"})
CHATTER_TOPBAR_CLASSES = frozenset({
    "o-mail-Chatter-topbar", "d-flex", "flex-shrink-0", "flex-grow-0", "overflow-x-auto",
})

# The message subtree, outwards from the rendered glyphs: `.o-mail-Message-body` >
# `.o-discuss-text-body` > `.o-mail-Message-textContent` > `.o-mail-Message-content` >
# `.o-mail-Message-contentContainer` > `.o-mail-Message-core` > `.o-mail-Message` > `.o-mail-Thread`
# > `.o-mail-Chatter-content`.
#
# Two layers carry the measurement. The message colour is declared on `.o-discuss-text-body`, the
# wrapper containing `.o-mail-Message-body`, as a bare class (0,1,0) with `!important`: it outranks
# any normal rule on `.o-mail-Chatter`, and the body inherits from the wrapper, not the Chatter.
# `.o-mail-Message-bubble` is a full-bleed absolutely-positioned preceding sibling of the body
# inside that wrapper, painted behind the text and never its ancestor, so it is resolved as its own
# element and handed to the arithmetic as the surface.
CHATTER_CONTENT_CLASSES = frozenset({
    "o-mail-Chatter-content", "d-flex", "flex-column", "flex-grow-1", "bg-inherit",
})
THREAD_CLASSES = frozenset({
    "o-mail-Thread", "position-relative", "flex-grow-1", "d-flex", "flex-column", "overflow-auto",
    "o-scrollbar-thin", "bg-inherit",
})
MESSAGE_ROOT_CLASSES = frozenset({
    "o-mail-Message", "position-relative", "rounded-0", "bg-inherit",
})
MESSAGE_CORE_CLASSES = frozenset({
    "o-mail-Message-core", "position-relative", "d-flex", "flex-shrink-0", "bg-inherit",
})
MESSAGE_CONTENT_CONTAINER_CLASSES = frozenset({
    "o-mail-Message-contentContainer", "position-relative", "d-flex",
})
MESSAGE_CONTENT_CLASSES = frozenset({"o-mail-Message-content", "o-min-width-0"})
MESSAGE_TEXT_CONTENT_CLASSES = frozenset({
    "o-mail-Message-textContent", "position-relative", "d-flex",
})
MESSAGE_TEXT_BODY_CLASSES = frozenset({
    "o-discuss-text-body", "position-relative", "overflow-x-auto", "overflow-y-hidden",
    "d-inline-block",
})
# The resting state the collision is measured in: a posted, non-note, non-squashed, non-editing
# message with text to show.
MESSAGE_BODY_CLASSES = frozenset({
    "o-mail-Message-body", "position-relative", "text-break", "mb-0", "py-2", "align-self-start",
    "o-rounded-end-bubble", "o-rounded-bottom-bubble",
})
# The variant class is what each bubble map keys on.
_MESSAGE_BUBBLE_BASE = frozenset({
    "o-mail-Message-bubble", "position-absolute", "top-0", "start-0", "w-100", "h-100", "border",
    "o-rounded-bottom-bubble", "o-rounded-end-bubble",
})
MESSAGE_BUBBLE_CLASSES = {
    variant: _MESSAGE_BUBBLE_BASE | {variant} for variant in ("o-blue", "o-green", "o-orange")
}

# The message subtree out to the thread list, the deepest layer every container shares; each
# container (form-view chatter, Discuss, chat window) appends its own tail, so no two of them can
# silently model the same panel. The thread's inner `d-flex flex-column ... bg-inherit` wrapper is
# left out: it declares no colour and paints nothing.
MESSAGE_SUBTREE_TO_THREAD_LAYERS = (
    MESSAGE_TEXT_CONTENT_CLASSES, MESSAGE_CONTENT_CLASSES, MESSAGE_CONTENT_CONTAINER_CLASSES,
    MESSAGE_CORE_CLASSES, MESSAGE_ROOT_CLASSES, THREAD_CLASSES,
)
# The two Chatter layers between the thread and whatever the Chatter is dropped into.
CHATTER_THREAD_HOST_LAYERS = (CHATTER_CONTENT_CLASSES, CHATTER_ROOT_CLASSES)

# The composer textarea carries `o-discuss-text-body` itself, so it takes the same bare-class
# `!important` colour as the message body, and paints its own fill through `.o-mail-Composer-bg`: a
# second place the pairing can go incoherent. Only the unconditional input classes are listed.
COMPOSER_INPUT_CLASSES = frozenset({
    "o-mail-Composer-input", "o-mail-Composer-bg", "shadow-none", "overflow-auto",
    "o-scrollbar-thin", "o-discuss-text-body", "user-select-auto", "o-mail-Composer-inputStyle",
    "form-control", "border-0", "o-rounded-bubble",
})
# The textarea's wrapper and the Composer root.
COMPOSER_INPUT_WRAPPER_CLASSES = frozenset({"position-relative", "flex-grow-1"})
COMPOSER_ROOT_CLASSES = frozenset({
    "o-mail-Composer", "d-grid", "flex-shrink-0", "pt-0", "position-relative",
})
# Outwards from the textarea to the Chatter root; a caller appends the panel the Chatter sits in.
COMPOSER_INPUT_CHATTER_LAYERS = (
    COMPOSER_INPUT_WRAPPER_CLASSES, COMPOSER_ROOT_CLASSES, CHATTER_TOP_CLASSES, CHATTER_ROOT_CLASSES,
)

# A suggestion row is an `<a>` inside the `.o-mail-NavigableList-item` wrapper. The active row paints
# its fill through `.o-mail-NavigableList-active`, the hovered row through
# `.o-mail-NavigableList-item:hover` on its wrapper.
NAVIGABLE_LIST_ROOT_CLASSES = frozenset({
    "o-mail-NavigableList", "bg-view", "m-0", "p-0", "shadow-sm", "o-mail-Composer-suggestionList",
})
NAVIGABLE_LIST_OPEN_CLASSES = frozenset({"o-open", "d-flex", "flex-column", "bg-inherit"})
NAVIGABLE_LIST_ITEM_CLASSES = frozenset({"o-mail-NavigableList-item", "o-mail-Composer-suggestion"})
NAVIGABLE_LIST_ROW_CLASSES = frozenset({
    "d-flex", "align-items-center", "w-100", "px-3", "py-1", "small",
})
NAVIGABLE_LIST_LAYERS = (
    NAVIGABLE_LIST_ITEM_CLASSES, NAVIGABLE_LIST_OPEN_CLASSES, NAVIGABLE_LIST_ROOT_CLASSES,
    WEBCLIENT_ANCESTORS,
)

# The day divider is a sibling of the messages in the thread.
DATE_SECTION_CLASSES = frozenset({
    "o-mail-DateSection", "d-flex", "align-items-center", "w-100", "fw-bold", "z-1", "pt-2", "px-2",
})
DATE_SECTION_LABEL_CLASSES = frozenset({"px-2", "smaller", "text-muted", "opacity-50"})

# A read conversation row (a `NotificationItem` without `o-interest`, which core dims as a whole) and
# its lines: the preview and the timestamp carry `o-muted`, which dims them again. The row's
# `bg-transparent`-like `--list-group-bg: transparent` paints nothing.
NOTIFICATION_ITEM_CLASSES = frozenset({
    "o-mail-NotificationItem", "o-navigable", "rounded-4", "border", "border-dark",
    "list-group-item", "d-flex", "cursor-pointer", "align-items-center", "w-100",
    "position-relative", "o-px-1_5", "py-2", "gap-2",
})
NOTIFICATION_ITEM_LINE_CLASSES = frozenset({"o-mail-NotificationItem-line", "d-flex", "text-nowrap"})
# The section header of the Discuss members panel, inside the action panel that Discuss puts in the
# sidebar-coloured `.o-mail-DiscussContent-panelContainer`.
MEMBER_LIST_HEADER_CLASSES = frozenset({
    "text-muted", "pt-4", "text-uppercase", "o-xsmaller", "opacity-75",
})
MEMBER_LIST_PANEL_LAYERS = (
    frozenset({
        "o-mail-ActionPanel-content", "px-1", "d-flex", "flex-column", "flex-grow-1", "bg-inherit",
        "o-min-height-0",
    }),
    frozenset({
        "o-mail-ActionPanel", "overflow-auto", "o-scrollbar-thin", "d-flex", "flex-column",
        "flex-shrink-0", "position-relative", "py-2", "pt-0", "h-100", "bg-inherit", "px-2",
    }),
    frozenset({
        "o-mail-DiscussContent-panelContainer", "o-mail-discussSidebarBgColor", "h-100",
        "border-start", "border-secondary", "flex-shrink-0",
    }),
    WEBCLIENT_ANCESTORS,
)

# The rows sit in the tab content of the messaging menu, whose root paints the fill.
NOTIFICATION_LIST_CLASSES = frozenset({
    "o-mail-MessagingMenu-tabContent", "d-flex", "flex-column", "overflow-auto", "o-scrollbar-thin",
    "flex-grow-1", "o-px-1_5", "o-gap-0_5",
})
NOTIFICATION_ITEM_NAME_CLASSES = frozenset({
    "o-mail-NotificationItem-name", "align-items-baseline", "fw-bold", "text-truncate",
})
NOTIFICATION_ITEM_TEXT_CLASSES = frozenset({
    "o-mail-NotificationItem-text", "text-start", "pe-none", "small", "o-muted",
})
NOTIFICATION_ITEM_DATE_CLASSES = frozenset({
    "o-mail-NotificationItem-date", "ms-2", "me-1", "flex-shrink-0", "align-self-end",
    "o-xsmaller", "o-muted",
})

NOTIFICATION_ITEM_LAYERS = (
    NOTIFICATION_ITEM_LINE_CLASSES, NOTIFICATION_ITEM_CLASSES,
    frozenset({"o-mail-MessagingMenuItem", "rounded-4"}), NOTIFICATION_LIST_CLASSES,
    frozenset({"o-mail-MessagingMenu", "d-flex", "flex-column", "flex-grow-1", "overflow-hidden"}),
    WEBCLIENT_ANCESTORS,
)

# The followers button in the chatter topbar: `active` when the user follows the record, coloured
# by `text-action` through `--color`.
FOLLOWERS_BUTTON_CLASSES = frozenset({
    "o-mail-Followers-button", "btn", "btn-link", "d-flex", "align-items-center", "text-action",
    "px-1", "my-2", "active",
})
FOLLOWERS_BUTTON_LAYERS = (
    frozenset({"o-mail-Followers", "d-flex", "me-1"}),
    CHATTER_TOPBAR_CLASSES, CHATTER_TOP_CLASSES, CHATTER_ROOT_CLASSES,
    frozenset({"o-mail-ChatterContainer", "o-mail-Form-chatter"}), WEBCLIENT_ANCESTORS,
)

# The navigation of the messaging menu: the active tab is a `.btn` whose label and icon both take
# their colour from the tab.
MESSAGING_MENU_NAVBAR_CLASSES = frozenset({
    "o-mail-MessagingMenu-navbar", "d-flex", "flex-column", "flex-shrink-0", "px-1", "o-py-2_5",
    "gap-2", "overflow-auto", "h-100", "o-scrollbar-thin",
})
MESSAGING_MENU_TAB_CLASSES = frozenset({
    "o-mail-MessagingMenu-tab", "o-navigable", "btn", "d-flex", "flex-column", "align-items-center",
    "w-100", "flex-shrink-0", "p-1", "bg-transparent", "position-relative", "border-0", "active",
})
MESSAGING_MENU_TAB_LABEL_CLASSES = frozenset({"o-xsmaller", "text-center", "lh-1", "mt-1"})
MESSAGING_MENU_TAB_ICON_CLASSES = frozenset({
    "oi", "o-mail-MessagingMenu-tabIcon", "rounded-pill", "mx-auto", "p-2", "fs-5",
})
MESSAGING_MENU_LAYERS = (
    MESSAGING_MENU_TAB_CLASSES, MESSAGING_MENU_NAVBAR_CLASSES,
    frozenset({"o-mail-MessagingMenu-container", "d-flex", "flex-grow-1", "overflow-hidden"}),
    WEBCLIENT_ANCESTORS,
)

# The muted secondary tier is read on two different surfaces. A timestamp (`.o-mail-Message-date`
# and its squashed twin in `.o-mail-Message-sidebar`) sits outside the bubble, in a sibling of
# `.o-mail-Message-contentContainer`, so the ancestor walk is its correct surface model. The four
# `.text-muted` markers inside `.o-mail-Message-body` (empty placeholder, `Subject:` line, two
# translation notes) sit on the bubble; the `Subject:` line models them, as the one carrying no
# `opacity` of its own, so the tier is measured undimmed.
MESSAGE_DATE_CLASSES = frozenset({"o-mail-Message-date", "o-xsmaller"})
MESSAGE_HEADER_CLASSES = frozenset({
    "o-mail-Message-header", "d-flex", "flex-wrap", "align-items-baseline", "lh-1", "mb-1",
})
_MESSAGE_CONTENT_WRAPPER = frozenset({"w-100", "o-min-width-0"})
MESSAGE_BODY_MUTED_CLASSES = frozenset({"d-block", "text-muted", "smaller"})


def _element_chain(element_classes, ancestor_layers, prev_sibling=frozenset(), tag=None):
    """Return the cascade-resolver chain for one modelled element and its styling ancestors.

    :param element_classes: the classes of the element itself
    :param ancestor_layers: the class sets of its styling ancestors, innermost first. Consecutive
        layers are a true parent relation, so a child combinator (``>``) is decided exactly; a pool
        such as ``WEBCLIENT_ANCESTORS`` folds several DOM levels into one superset, which stays
        permissive where it cannot decide
    :param prev_sibling: the classes of the element's previous sibling; only the element carries one
    :param tag: the element's HTML tag, only the element carries one; ``None`` keeps the resolver's
        conservative "type selectors do not match" reading
    :return: one entry per layer, innermost first, each with ``classes``, ``ancestors`` (the union
        of the classes outside it), ``prev_sibling``, ``parent`` and ``tag``
    """
    layers = [frozenset(element_classes)] + [frozenset(layer) for layer in ancestor_layers]
    chain = []
    for index, classes in enumerate(layers):
        outer = layers[index + 1:]
        chain.append({
            "classes": classes,
            "ancestors": frozenset().union(*outer) if outer else frozenset(),
            "prev_sibling": prev_sibling if index == 0 else frozenset(),
            "parent": outer[0] if outer else None,
            "tag": tag if index == 0 else None,
        })
    return chain


# The surface an element is read on is not always an ancestor. An absolutely-positioned full-bleed
# element paints behind every later sibling in its containing block, so a resolver compositing only
# ancestor backgrounds walks past it. `.o-mail-Message-bubble` is a preceding sibling of
# `.o-mail-Message-body` inside `.o-discuss-text-body`, so it is the body's surface; the timestamp
# lives in the message header, away from the bubble, and must not be credited with one.
#
# The overlay is behind an element iff the overlay's parent is a STRICT ancestor of it: an element
# carrying the container class itself (the composer textarea carries `o-discuss-text-body`) is the
# container, not a sibling of anything inside it. The overlay's chain is derived from the subject's
# chain rather than transcribed a second time.
PaintedSibling = collections.namedtuple("PaintedSibling", "label classes container_class")

# The three bubble variants core paints; `container_class` is the wrapper the bubble is a child of.
MESSAGE_BUBBLE_SIBLING_BY_VARIANT = {
    variant: PaintedSibling(
        label="%s message bubble" % variant,
        classes=MESSAGE_BUBBLE_CLASSES[variant],
        container_class="o-discuss-text-body",
    )
    for variant in MESSAGE_BUBBLE_CLASSES
}
MESSAGE_BUBBLE_SIBLINGS = tuple(
    MESSAGE_BUBBLE_SIBLING_BY_VARIANT[variant] for variant in sorted(MESSAGE_BUBBLE_CLASSES)
)


def _painted_sibling_chain(chain, sibling):
    """Return ``sibling``'s own resolver chain when it paints behind ``chain[0]``, else None.

    The walk starts at index 1: an element carrying the container class itself contains the overlay
    rather than sitting next to it."""
    for depth in range(1, len(chain)):
        if sibling.container_class in chain[depth]["classes"]:
            return _element_chain(sibling.classes, [entry["classes"] for entry in chain[depth:]])
    return None


# The same message subtree in an ordinary form-view chatter. `.o-mail-Form-chatter` (emitted by
# core's form compiler) is the outermost layer that paints, with `$o-webclient-background-color`
# (`$o-gray-100`, darker than white); every layer inside it down to `.o-mail-Message` is `bg-inherit`.
FORM_CHATTER_CONTAINER_CLASSES = frozenset({"o-mail-ChatterContainer", "o-mail-Form-chatter"})
CHATTER_PANEL_LAYERS = (FORM_CHATTER_CONTAINER_CLASSES, WEBCLIENT_ANCESTORS)
CHATTER_MESSAGE_LAYERS = (
    MESSAGE_SUBTREE_TO_THREAD_LAYERS + CHATTER_THREAD_HOST_LAYERS + CHATTER_PANEL_LAYERS
)
CHATTER_TEXT_BODY_LAYERS = (MESSAGE_TEXT_BODY_CLASSES,) + CHATTER_MESSAGE_LAYERS
CHATTER_MESSAGE_HEADER_LAYERS = (
    MESSAGE_HEADER_CLASSES, _MESSAGE_CONTENT_WRAPPER, MESSAGE_CORE_CLASSES, MESSAGE_ROOT_CLASSES,
    THREAD_CLASSES, CHATTER_CONTENT_CLASSES, CHATTER_ROOT_CLASSES,
) + CHATTER_PANEL_LAYERS
CHATTER_BODY_MUTED_LAYERS = (MESSAGE_BODY_CLASSES,) + CHATTER_TEXT_BODY_LAYERS

# The placeholder core renders instead of a body when a message has no content: a direct child of
# `.o-mail-Message-body`, so a bubbled message paints its bubble behind it. Its tag is load-bearing:
# core styles it through `.o-mail-Message-body > i.text-muted.opacity-75`, so a class-only model
# skips that rule and measures the dimmed opacity the rule cancels.
MESSAGE_EMPTY_PLACEHOLDER_TAG = "i"
MESSAGE_EMPTY_PLACEHOLDER_CLASSES = frozenset({"text-muted", "opacity-75"})

# The `<span class="o-mail-Message-edited"/>` marker the server writes into the body HTML and core's
# JS fills: it renders in the rich-body div inside `.o-mail-Message-body`, so it is inside
# `.o-discuss-text-body` too.
MESSAGE_EDITED_MARKER_TAG = "span"
MESSAGE_EDITED_MARKER_CLASSES = frozenset({"o-xsmaller", "opacity-50"})
_MESSAGE_EDITED_SPAN = frozenset({"o-mail-Message-edited"})
_MESSAGE_RICH_BODY_CLASSES = frozenset({"o-mail-Message-richBody", "overflow-x-auto"})


def _body_muted_layers(message_layers):
    """Return the ancestor layers of a muted marker rendered directly inside the message body.

    :param message_layers: the layers from the message subtree outwards, which vary with the
        container the message list is dropped into
    """
    return (MESSAGE_BODY_CLASSES, MESSAGE_TEXT_BODY_CLASSES) + message_layers


def _edited_marker_layers(message_layers):
    """Return the ancestor layers of the `(edited)` span, two wrappers deeper than a body marker.

    :param message_layers: see :func:`_body_muted_layers`
    """
    return (
        _MESSAGE_EDITED_SPAN, _MESSAGE_RICH_BODY_CLASSES,
    ) + _body_muted_layers(message_layers)


CHATTER_EDITED_MARKER_LAYERS = _edited_marker_layers(CHATTER_MESSAGE_LAYERS)

# The same message subtree renders in Discuss and in a chat window, each painting a different panel
# under it (two distinct greys in the dark bundle): a fix tuned against one panel is not a fix for
# the others, so each container is modelled separately.

# Discuss: the `.o-mail-DiscussContent-core` layer paints (`background-color: $body-bg`), which the
# dark recompile drives to the dark view surface.
DISCUSS_THREAD_COLUMN_CLASSES = frozenset({
    "d-flex", "flex-column", "flex-grow-1", "bg-inherit", "min-w-0", "mt-1",
})
DISCUSS_CONTENT_CORE_CLASSES = frozenset({
    "o-mail-DiscussContent-core", "overflow-auto", "o-scrollbar-thin", "d-flex", "flex-grow-1",
    "w-100", "gap-2",
})
DISCUSS_CONTENT_MAIN_CLASSES = frozenset({
    "o-mail-DiscussContent-main", "d-flex", "overflow-hidden", "flex-grow-1", "gap-2",
})
DISCUSS_CONTENT_CLASSES = frozenset({
    "o-mail-DiscussContent", "d-flex", "flex-column", "h-100", "flex-grow-1", "overflow-auto",
    "o-scrollbar-thin",
})
DISCUSS_ROOT_CLASSES = frozenset({"o-mail-Discuss", "d-flex", "h-100", "flex-grow-1", "gap-2", "p-2"})
DISCUSS_PANEL_LAYERS = (
    DISCUSS_THREAD_COLUMN_CLASSES, DISCUSS_CONTENT_CORE_CLASSES, DISCUSS_CONTENT_MAIN_CLASSES,
    DISCUSS_CONTENT_CLASSES, DISCUSS_ROOT_CLASSES, WEBCLIENT_ANCESTORS,
)
DISCUSS_MESSAGE_LAYERS = MESSAGE_SUBTREE_TO_THREAD_LAYERS + DISCUSS_PANEL_LAYERS

# Chat window: the root paints through the `bg-100` utility, an `!important` (0,1,0) declaration no
# normal rule outranks, so the dark de-light of this surface carries the flag too. The window is
# `fixed-bottom` on the web client root, not inside the action manager.
CHAT_WINDOW_ROOT_CLASSES = frozenset({
    "o-mail-ChatWindow", "fixed-bottom", "overflow-hidden", "d-flex", "flex-column", "shadow",
    "bg-100",
})
CHAT_WINDOW_CONTENT_CLASSES = frozenset({
    "d-flex", "flex-column", "h-100", "overflow-auto", "o-scrollbar-thin", "position-relative",
    "bg-inherit",
})
CHAT_WINDOW_PANEL_LAYERS = (
    CHAT_WINDOW_CONTENT_CLASSES, CHAT_WINDOW_ROOT_CLASSES, frozenset({"o_web_client"}),
)
CHAT_WINDOW_MESSAGE_LAYERS = MESSAGE_SUBTREE_TO_THREAD_LAYERS + CHAT_WINDOW_PANEL_LAYERS

# The three containers a message renders in, each with the panel its ancestor walk lands on,
# declared as data so no subject is measured in two of them and skips the third.
DARK_MESSAGE_CONTAINERS = (
    ("form-view chatter", "the form-view chatter panel", CHATTER_MESSAGE_LAYERS),
    ("Discuss", "the Discuss thread canvas", DISCUSS_MESSAGE_LAYERS),
    ("chat window", "the chat-window body", CHAT_WINDOW_MESSAGE_LAYERS),
)


# The surface a resolution landed on and who painted it: `painter` makes a failure message
# actionable ("the o-blue bubble" and "layer 9 of the chain" point to different files).
Backdrop = collections.namedtuple("Backdrop", "painter depth value rgb")

# The Discuss panel edges, each an element core draws with the bare Bootstrap `.border` utility;
# no viin_brand_mail rule targets these classes for a border colour. `element_class` is the
# element's own semantic class, `source` the core file that declares it.
DiscussSeam = collections.namedtuple("DiscussSeam", "label element_class source")

DISCUSS_DARK_SEAMS = (
    DiscussSeam(
        "the Discuss sidebar menu's edge", ".o-mail-MessagingMenu",
        "mail/static/src/core/public_web/messaging_menu/messaging_menu.xml",
    ),
    DiscussSeam(
        "the Discuss content header box's edge", ".o-mail-DiscussContent-headerBox",
        "mail/static/src/core/public_web/discuss_content.xml",
    ),
    DiscussSeam(
        "the Discuss side panel's edge", ".o-mail-DiscussContent-panelContainer",
        "mail/static/src/core/public_web/discuss_content.xml",
    ),
)

# `.o_mail_discuss` is the one class separating the two contexts: core adds it to the body while
# Discuss is the open app and keys its Discuss-only dark rules on it. Modelling the same element
# under both bodies lets a guard ask what opening Discuss changes instead of pinning either colour.
WEBCLIENT_BODY = frozenset({"o_web_client"})
DISCUSS_WEBCLIENT_BODY = WEBCLIENT_BODY | {"o_mail_discuss"}

# The navbar surfaces whose paint must not depend on which app is open, innermost first. Core paints
# the menu entry from `var(--NavBar-entry-backgroundColor, #{$o-navbar-background})`, the variable
# core mail re-points for Discuss, and gives it the full border-box height, so an entry whose fill
# differs from the bar's paints across the bar's 1px bottom rule and chops it into dashes.
NAVBAR_CHROME_SURFACES = (
    ("the navbar itself", frozenset({"o_main_navbar"}), ()),
    (
        "a navbar menu entry",
        frozenset({"o_nav_entry"}),
        (frozenset({"o_menu_sections"}), frozenset({"o_main_navbar"})),
    ),
)


class ContrastCompileHelpers:
    """Compile-and-resolve helpers shared by the contrast guards of the brand cluster.

    A mixin rather than a test case, so a module that guards its own dark surfaces reuses the
    resolvers without collecting this module's tests a second time."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Memoised per class: the payload derives purely from source files, so every test method
        # sees the same CSS and a recompile per assertion is avoided.
        cls._compiled_css_cache = {}

    def _compile(self, bundle_name):
        """Compile ``bundle_name`` and return ``(bundle, css_text)``.

        The attachments are joined so a split bundle is handled, and decoded leniently so an
        assertion, not a decode error, reports a problem."""
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        attachments = bundle.css() or self.env["ir.attachment"]
        css = "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )
        return bundle, css

    def _compiled_css(self, bundle_name):
        """Return the compiled CSS of ``bundle_name``, asserting it is non-empty."""
        if bundle_name not in self._compiled_css_cache:
            self._compiled_css_cache[bundle_name] = self._compile(bundle_name)[1]
        css = self._compiled_css_cache[bundle_name]
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS - the bundle did not build, so its branded mail surfaces "
            "cannot be verified." % bundle_name,
        )
        return css

    def _assert_rgb(self, value, label):
        """Parse a compiled colour value, failing with a locatable message when it is unusable."""
        rgb = _to_rgb(value)
        self.assertIsNotNone(
            rgb, "%s compiled to %r, which is not a plain colour this contrast guard can measure."
            % (label, value),
        )
        return rgb

    def _require_cascade_resolver(self):
        """Fail crisply when the cluster's shared cascade resolver could not be imported."""
        self.assertIsNotNone(
            _computed_value,
            "viin_brand/tests/test_brand_cascade_compile.py must expose _computed_value and "
            "_winning_declaration: they are the cluster's single cascade resolver, and a guard that "
            "resolves through core's own consumer goes red on a core rename instead of orphaning "
            "our declaration silently.",
        )

    def _require_scope_filter(self):
        """Fail crisply when the cluster's shared ancestor model could not be imported.

        Without the ancestor filter a rule scoped under another module's root is the later writer
        for the same subject, and a guard would report a colour that renders in a context it does
        not measure."""
        self.assertIsNotNone(
            _selector_scope_applies,
            "viin_brand/tests/test_brand_cascade_compile.py must expose _selector_scope_applies: it "
            "is the cluster's single ancestor model, used to drop rules scoped to a context the "
            "element is not in, which a browser never applies.",
        )

    def _resolve(self, css, chain, prop_names, surface):
        """Return the raw value the CSS cascade computes for ``prop_names`` on ``chain[0]``.

        The answer comes from the core rule that reads the property (Bootstrap's
        `.btn.active { color: var(--btn-active-color) }`, ...), with `var()` followed outwards
        through the chain as a browser does; if core renames the property, our declaration is
        unreachable and this fails.

        :param chain: the element and its styling ancestors, innermost first
        """
        self._require_cascade_resolver()
        value = _computed_value(css, chain, prop_names)
        self.assertIsNotNone(
            value,
            "No compiled declaration of %s applies to %s. Either core moved the surface to a "
            "different lever, or the selector this module overrides does not match - in both "
            "cases the branded value is not reaching the pixel."
            % ("/".join(prop_names), surface),
        )
        return value

    def _resolve_colour(self, css, chain, prop_names, surface):
        """Resolve ``prop_names`` on ``chain[0]`` and return ``(raw_value, rgb)``.

        Colours are normalised through this file's own ``_to_rgb`` rather than the resolver
        module's ``_normalize_colour``: several declarations are the keyword ``white``, which Sass
        emits verbatim inside a custom property and which a hex-only normaliser reads as no colour."""
        value = self._resolve(css, chain, prop_names, surface)
        return value, self._assert_rgb(value, surface)

    def _require_root_property(self, css, name, bundle_name):
        """Return the ``:root`` value of ``--<name>``, failing crisply when core stops emitting it."""
        value = _root_custom_property(css, name)
        self.assertIsNotNone(
            value,
            "%s emits no `--%s` on :root. Bootstrap emits the theme tokens there from their Sass "
            "variables, so this guard's anchor is gone - re-ground it against the new lever rather "
            "than pinning a literal in this file." % (bundle_name, name),
        )
        return value

    def _assert_core_source_contains(self, source, needles, why):
        """Assert core's own source contains each needle: the name-existence fallback.

        Used only where cascade resolution is inexpressible. A core rename of the property makes
        this fail instead of silently orphaning our declaration. ``file_open`` resolves the path
        against the addons path, so any checkout layout works."""
        with file_open(source, "r") as core_file:
            content = core_file.read()
        for needle in needles:
            self.assertIn(
                needle, content,
                "%s does not contain %r. %s Re-ground this guard against the new lever rather "
                "than deleting it." % (source, needle, why),
            )

    def _root_token(self, css, token, bundle_name, label):
        """Return the value core's Bootstrap ``_root.scss`` emits for ``:root --<token>`` in ``css``.

        Odoo sets ``$variable-prefix: ''``, so the token has no ``bs-`` prefix. This reads core's
        own :root emission, not this module's declaration, so a core rename orphans our
        ``var(--<token>)`` reference and the guard goes red. Both bundles emit their own :root
        block; only the compiled CSS handed in differs between light and dark."""
        root_bodies = _bodies_matching(css, lambda selector: selector == ":root", ANY_ANCESTORS)
        values = _declared_values(root_bodies, _custom_property_re(token))
        self.assertTrue(
            values,
            "The compiled %s emits no :root --%s, so %s cannot be resolved. Core's Bootstrap "
            "_root.scss emits --%s from the scheme's Sass var (Odoo sets $variable-prefix:''); a "
            "rename orphans this module's var(--%s) reference."
            % (bundle_name, token, label, token, token),
        )
        return values[-1]

    def _dark_root_token(self, css, token, label):
        """The dark-bundle reading of :meth:`_root_token`."""
        return self._root_token(css, token, DARK_BUNDLE, label)

    def _resolve_scheme_colour(self, css, value, bundle_name, label):
        """Resolve a compiled colour that is a bare literal or a ``var(--token[, fallback])``.

        A custom-property lookup is followed through core's :root emission (:meth:`_root_token`);
        a literal is returned as-is.

        :return: ``(raw_value, rgb)``
        """
        match = _VAR_REF_RE.fullmatch(value.strip())
        if match:
            value = self._root_token(css, match.group(1), bundle_name, label)
        return value, self._assert_rgb(value, label)

    def _resolve_dark_colour(self, css, value, label):
        """The dark-bundle reading of :meth:`_resolve_scheme_colour`."""
        return self._resolve_scheme_colour(css, value, DARK_BUNDLE, label)

    def _rendered_backdrop(self, css, chain, bundle_name, label, siblings=()):
        """Return the :class:`Backdrop` an element in ``chain`` is really read on.

        :param siblings: the full-bleed overlays that may be painted behind the element; each
            applies only when its container is a strict ancestor of the subject (see
            :func:`_painted_sibling_chain`). Empty for a subtree with no overlay.

        With no overlay applying, the walk goes outwards and stops at the first ancestor that paints
        a fully opaque colour, so a guard is indifferent to where a surface gets re-lit. A stack
        that paints nothing falls back to the app body background read from core's ``:root``
        emission, which stays available when the modules contributing the outer chrome are not
        installed."""
        self._require_cascade_resolver()
        for sibling in siblings:
            sibling_chain = _painted_sibling_chain(chain, sibling)
            if sibling_chain is None:
                continue
            value = _computed_value(css, sibling_chain, BACKGROUND_PROPS)
            self.assertIsNotNone(
                value,
                "No compiled background applies to the %s in %s. Core's own message stylesheets "
                "paint every variant, so an empty resolution means the modelled overlay does not "
                "match core's message.xml." % (sibling.label, bundle_name),
            )
            rgb = _opaque_rgb(value)
            self.assertIsNotNone(
                rgb,
                "The %s is modelled as painted behind this element, but it resolves the background "
                "%r in %s, which is not an opaque colour. A full-bleed overlay that stops painting "
                "one lets the glyphs above it fall onto the layer behind, and this guard can no "
                "longer say what a reader sees - re-model the overlay rather than measuring the "
                "wrong surface." % (sibling.label, value, bundle_name),
            )
            return Backdrop(sibling.label, None, value, rgb)
        for depth in range(len(chain)):
            value = _computed_value(css, chain[depth:], BACKGROUND_PROPS)
            rgb = _opaque_rgb(value)
            if rgb is not None:
                return Backdrop("layer %d of the modelled chain" % depth, depth, value, rgb)
        fallback = self._root_token(css, "body-bg", bundle_name, label)
        return Backdrop(
            "the app body background", len(chain), fallback, self._assert_rgb(fallback, label),
        )

    def _inherited_colour(self, css, chain, bundle_name, label):
        """Return ``(value, rgb)`` of the colour an element in ``chain`` really renders its text in.

        `color` inherits, so the value comes from the nearest ancestor that declares one and from
        the document body only when none does. Walking outwards makes a declaration on a wrapper
        visible, and lets a bare-class `!important` (0,1,0) on an ancestor beat a more specific
        normal rule further out, the cascade order core's `.o-discuss-text-body` turns on in both
        schemes."""
        self._require_cascade_resolver()
        for depth in range(len(chain)):
            value = _computed_value(css, chain[depth:], ("color",))
            if value is not None:
                return self._resolve_scheme_colour(css, value, bundle_name, label)
        fallback = self._root_token(css, "body-color", bundle_name, label)
        return self._resolve_scheme_colour(css, fallback, bundle_name, label)

    def _rendered_ink(self, css, chain, bundle_name, label, dimmed_by_ancestors=False):
        """Return ``(value, rgb, alpha)`` of the ink an element paints, alpha included.

        The colour is not always opaque: `$text-muted` is `rgba($o-gray-700, $o-opacity-muted)` and
        an element, or with ``dimmed_by_ancestors`` one of its ancestors, may carry an `opacity`.
        All of them multiply into one effective alpha, read from the compiled bundle rather than
        pinned."""
        self._require_cascade_resolver()
        value, rgb = self._inherited_colour(css, chain, bundle_name, label)
        alpha_match = _RGBA_ALPHA_RE.search(value)
        alpha = 1.0 if alpha_match is None else (_to_alpha(alpha_match.group(1)) or 1.0)
        # `opacity` composes through the tree: an ancestor that dims its subtree dims the element.
        # Read only where the model of the ancestors is exact: a state-dependent dimming of a
        # message (`.o-mail-Thread:has(.o-selected)`) is not one the class model can decide.
        for depth in range(len(chain) if dimmed_by_ancestors else 1):
            opacity = _computed_value(css, chain[depth:], ("opacity",))
            if opacity is None:
                continue
            element_alpha = _to_alpha(_normalize_value(opacity))
            self.assertIsNotNone(
                element_alpha,
                "%s resolves the opacity %r in %s, which is not a number this guard can composite. "
                "The dimming is part of the contrast rule, so an unreadable opacity has to fail "
                "rather than be silently treated as fully opaque."
                % (label, opacity, bundle_name),
            )
            alpha *= element_alpha
        return value, rgb, alpha

    def _assert_readable_on_every_message_surface(
        self, bundle_name, chain, subject, why, panel_label="the chatter panel",
        dimmed_by_ancestors=False,
    ):
        """Assert ``subject`` clears AA on the panel and on each bubble it can be read on.

        Each tier is set by one rule and lands on several backdrops, so a fix that satisfies the
        lightest one only is the defect guarded against. Values are resolved from the compiled
        bundle, so any coherent re-tune passes.

        :param panel_label: names the container the ancestor walk lands on, so a failure points at
            the right stylesheet
        """
        css = self._compiled_css(bundle_name)
        ink_value, ink_rgb, alpha = self._rendered_ink(
            css, chain, bundle_name, subject, dimmed_by_ancestors=dimmed_by_ancestors,
        )
        surfaces = [(panel_label, ())]
        surfaces += [(sibling.label, (sibling,)) for sibling in MESSAGE_BUBBLE_SIBLINGS
                     if _painted_sibling_chain(chain, sibling) is not None]
        for label, siblings in surfaces:
            with self.subTest(surface=label):
                backdrop = self._rendered_backdrop(
                    css, chain, bundle_name, "%s surface" % subject, siblings=siblings,
                )
                painted = _composite(ink_rgb, backdrop.rgb, alpha)
                ratio = _contrast_ratio(painted, backdrop.rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "In %s the %s renders %s at an effective alpha of %.4f - painting rgb%r - on %s "
                    "(%s, rgb%r), only %.2f:1 where WCAG AA normal text needs >= %.1f:1. %s"
                    % (bundle_name, subject, ink_value, alpha, painted, label, backdrop.value,
                       backdrop.rgb, ratio, WCAG_AA_NORMAL_TEXT, why),
                )


@tagged("post_install", "-at_install")
class MailContrastCompileTest(ContrastCompileHelpers, TransactionCase):
    """Every branded mail surface must compile to a colour pair its glyphs can be read on."""

    def _plain_composer_surface(self, css, bundle_name, all_rules, gated_rules):
        """Return the surface a composer not in send-message mode renders on, as ``(r, g, b)``.

        Derived per bundle rather than pinned: the dark tail declares ``--mail-Composer-bg`` on
        ``.o-mail-Composer`` (the last ungated declaration wins), while in the light bundle every
        composer falls through to the fallback inside core's consumer
        ``var(--mail-Composer-bg, <x>)``."""
        gated_bodies = [body for _tokens, body in gated_rules]
        ungated = _declared_values(
            [body for _tokens, body in all_rules if body not in gated_bodies],
            _custom_property_re("mail-Composer-bg"),
        )
        if ungated:
            return self._assert_rgb(ungated[-1], "plain composer surface (%s)" % bundle_name)

        consumer_bodies = _bodies_matching(
            css, lambda selector: selector == ".o-mail-Composer-bg", COMPOSER_ANCESTORS
        )
        fallbacks = [
            match.group(1).strip()
            for body in consumer_bodies
            for match in re.finditer(
                r"var\(\s*--mail-Composer-bg\s*,\s*([^)]+)\)", body, re.IGNORECASE
            )
        ]
        self.assertTrue(
            fallbacks,
            "No ungated --mail-Composer-bg declaration AND no `var(--mail-Composer-bg, <fallback>)` "
            "consumer found in %s, so the plain Log-note composer surface cannot be resolved - core "
            "moved the composer fill to a different lever." % bundle_name,
        )
        return self._assert_rgb(fallbacks[-1], "plain composer surface fallback (%s)" % bundle_name)

    def _composer_placeholder_opacity(self, css, bundle_name):
        """Return the dimmest opacity core applies to the composer placeholder in ``css``.

        The lowest alpha is the faintest placeholder, hence the honest worst case to composite."""
        alphas = []
        for tokens, body in _iter_rules(css):
            if not any(_COMPOSER_PLACEHOLDER_SELECTOR in token for token in tokens):
                continue
            for match in re.finditer(r"(?<![\w-])opacity\s*:\s*([^;]+)", body, re.IGNORECASE):
                alpha = _to_alpha(_normalize_value(match.group(1)))
                if alpha is not None:
                    alphas.append(alpha)
        self.assertTrue(
            alphas,
            "No `%s` opacity rule found in %s - core stopped dimming the composer placeholder, so "
            "the composited value this guard measures cannot be derived."
            % (_COMPOSER_PLACEHOLDER_SELECTOR, bundle_name),
        )
        return min(alphas)

    def test_chat_window_header_renders_the_chrome_teal_not_the_brand_purple(self):
        """The chat-window header must be the chrome teal carrying readable white text, in both schemes.

        The header floats over the application, so it is frame and reads the chrome ladder; the
        conversation inside it is content. Only the ``.o-mail-ChatWindow-header`` element is read;
        its descendants carry their own colours."""
        for bundle in (BACKEND_BUNDLE, DARK_BUNDLE):
            with self.subTest(bundle=bundle):
                self._assert_chat_window_header_is_chrome_teal(bundle)

    def _assert_chat_window_header_is_chrome_teal(self, bundle):
        css = self._compiled_css(bundle)
        header_element = re.compile(r"^\.o-mail-ChatWindow-header([:.]|$)")
        bodies = _bodies_matching(css, header_element.match, ANY_ANCESTORS)
        self.assertTrue(
            bodies,
            "No rule targets the .o-mail-ChatWindow-header element itself in compiled %s - the "
            "module's chat-window de-brand did not reach the bundle." % bundle,
        )

        backgrounds = _declared_hexes(bodies, _BACKGROUND_RE)
        self.assertTrue(
            backgrounds,
            "The .o-mail-ChatWindow-header element declares no background colour in compiled %s; "
            "the branded header chrome cannot be verified." % bundle,
        )
        self.assertNotIn(
            FORBIDDEN_HEADER_PURPLE, backgrounds,
            "Chat-window header compiled to the darkened purple %s (backgrounds: %r); the header "
            "chrome is the CHROME-BASE tier." % (FORBIDDEN_HEADER_PURPLE, backgrounds),
        )

        # Last writer wins at equal specificity - this is what actually renders.
        self.assertEqual(
            backgrounds[-1], CHROME_BASE,
            "Chat-window header must render the CHROME-BASE teal %s (the $o-viin-chrome-base "
            "SSOT token); compiled backgrounds were %r." % (CHROME_BASE, backgrounds),
        )

        header_colors = _declared_values(bodies, _COLOR_RE)
        self.assertTrue(
            header_colors,
            "The .o-mail-ChatWindow-header element declares no text colour; white-on-teal must be "
            "explicit.",
        )
        foreground = self._assert_rgb(header_colors[-1], "chat-window header text colour")
        background = self._assert_rgb(backgrounds[-1], "chat-window header background")
        ratio = _contrast_ratio(foreground, background)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "Chat-window header text (%s) on its background (%s) is only %.2f:1 - WCAG AA normal "
            "text needs >= %.1f:1." % (header_colors[-1], backgrounds[-1], ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_chat_window_header_action_icons_are_readable_as_composited(self):
        """Header action glyphs must be readable as rendered: colour and opacity together.

        Core dims idle header actions with ``--o-mail-ActionList-Button-opacity: .5``, which
        composites even pure white below the 3:1 non-text floor, so the glyph colour
        alone is not enough: the pass/fail rule is stated on the composited colour.

        The rules are read directly rather than resolved through the cascade: this module's subject
        is the type selector ``button``, which the class-based resolver does not model, and core's
        opacity consumer hangs off a ``:has()`` selector. A core rename of the properties is caught
        by asserting that core's own source still reads each of them."""
        css = self._compiled_css(BACKEND_BUNDLE)

        # The properties this surface is fed through must still be the ones core reads;
        # otherwise every assertion below passes on our own orphaned declarations.
        self._assert_core_source_contains(
            "web/static/lib/bootstrap/scss/_buttons.scss",
            (
                "--#{$prefix}btn-color", "color: var(--#{$prefix}btn-color)",
                "color: var(--#{$prefix}btn-hover-color)",
                "color: var(--#{$prefix}btn-active-color)",
            ),
            "Bootstrap does not resolve a .btn's foreground through that custom property, so the "
            "white glyph this module pins on the chat-window header is an orphaned declaration and "
            "the header actions have silently reverted to the Bootstrap secondary foreground.",
        )
        self._assert_core_source_contains(
            "mail/static/src/core/common/action_list.scss",
            ("opacity: var(--o-mail-ActionList-Button-opacity)",),
            "Core does not dim ActionList buttons through that custom property, so this module's "
            "`--o-mail-ActionList-Button-opacity: 1` un-dims nothing and the header glyphs sit "
            "below the non-text contrast floor.",
        )

        def targets_header_action_button(selector):
            return ".o-mail-ChatWindow-header" in selector and ".o-mail-ActionList" in selector

        bodies = _bodies_matching(css, targets_header_action_button, ANY_ANCESTORS)
        self.assertTrue(
            bodies,
            "No compiled rule targets the chat-window header's ActionList buttons in %s."
            % BACKEND_BUNDLE,
        )

        header_backgrounds = _declared_hexes(
            _bodies_matching(
                css, re.compile(r"^\.o-mail-ChatWindow-header([:.]|$)").match, ANY_ANCESTORS
            ),
            _BACKGROUND_RE,
        )
        self.assertTrue(header_backgrounds, "chat-window header background not found; see the header test.")
        header_rgb = self._assert_rgb(header_backgrounds[-1], "chat-window header background")

        for token in ("btn-color", "btn-hover-color", "btn-active-color"):
            values = _declared_values(bodies, _custom_property_re(token))
            self.assertTrue(
                values,
                "The chat-window header's ActionList buttons declare no --%s. Core resolves the "
                "button foreground through that token, so leaving it unset keeps the Bootstrap "
                "secondary glyph #212529, unreadable on the teal header." % token,
            )
            glyph_rgb = self._assert_rgb(values[-1], "chat-window header --%s" % token)
            self.assertEqual(
                glyph_rgb, WHITE_RGB,
                "Chat-window header --%s compiled to %r; the glyph must be WHITE on the purple "
                "chrome." % (token, values[-1]),
            )

        opacity_values = _declared_values(bodies, _custom_property_re("o-mail-ActionList-Button-opacity"))
        self.assertTrue(
            opacity_values,
            "The chat-window header's ActionList buttons declare no "
            "--o-mail-ActionList-Button-opacity, so core's idle `.5` stands and even a white "
            "glyph composites below the contrast floor on the teal header.",
        )
        effective_alpha = _to_alpha(opacity_values[-1])
        self.assertIsNotNone(
            effective_alpha,
            "--o-mail-ActionList-Button-opacity compiled to %r, which is not an opacity this "
            "contrast guard can composite." % (opacity_values[-1],),
        )

        composited = _composite(WHITE_RGB, header_rgb, effective_alpha)
        ratio = _contrast_ratio(composited, header_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "A white header action glyph at opacity %s composites to rgb%r on the header (%s), "
            "which is only %.2f:1. Un-dimming the glyph (`opacity: 1`) is what takes it to "
            "AA; the glyph colour alone is not enough."
            % (opacity_values[-1], composited, header_backgrounds[-1], ratio),
        )

    def test_chat_window_header_muted_glyph_is_realigned_to_the_white_chrome(self):
        """A `.text-muted` glyph in the header must take the header's white, not Bootstrap grey.

        Core's parent-channel breadcrumb chevron is `text-muted opacity-75`: a `!important`
        Bootstrap grey (#495057) that stays under the 3:1 non-text floor on the teal chrome.
        Asserted as ``color: inherit`` beating that ``!important`` rather than as a hex, because the
        legible value is whatever the header foreground computes to."""
        css = self._compiled_css(BACKEND_BUNDLE)
        bodies = _bodies_matching(
            css,
            lambda selector: ".o-mail-ChatWindow-header" in selector and ".text-muted" in selector,
            ANY_ANCESTORS,
        )
        self.assertTrue(
            bodies,
            "No compiled rule realigns a `.text-muted` glyph inside .o-mail-ChatWindow-header in "
            "%s, so core's Bootstrap grey #495057 (a `!important` utility) still paints the "
            "parent-channel breadcrumb chevron on the teal header, below the 3:1 non-text "
            "floor." % BACKEND_BUNDLE,
        )
        colors = _declared_values(bodies, _COLOR_RE)
        self.assertTrue(
            colors, "the header `.text-muted` rule declares no color; it cannot beat Bootstrap's.",
        )
        self.assertEqual(
            colors[-1], "inherit",
            "The header `.text-muted` glyph must take the header's inherited white "
            "(`color: inherit !important`), matching the channel-name span beside it; compiled "
            "color declarations were %r. A fixed hex here would drift from the header foreground "
            "the header test pins - inherit keeps the two in lock-step." % colors,
        )

    def test_chatter_open_composer_toggles_are_deep_content_colour_for_send_and_the_default_grey_for_log_note(self):
        """"Send message" and "Log note", while open, must differ and both be readable.

        A Log note is internal and a Send message goes to the customer, so the two open toggles must
        not share one colour, and the label must not be pinned to the literal `white` (2.90:1 on a
        dark purple arm). "Log note" renders the stock `.btn-secondary`, asserted against a real
        stock `.btn-secondary` resolved out of the same bundle (the core web pager arrow, whose
        element model viin_brand owns) rather than a hex: that holds in both schemes and cannot be
        met by a grey that merely looks right. Left to core, the toggle carries `btn-primary active`
        and resolves the primary map's near-white active state.

        "Send message" is the deep content rung (purple in light, cyan in dark): the content colour is
        already the button's resting
        `.btn-primary` fill, so reusing it would make an open composer look like a closed one.

        The labels are resolved through Bootstrap's `.btn.active { color: var(--btn-active-color) }`
        consumer, never read back out of this module's own declaration, so a Bootstrap rename makes
        the value unresolvable and the guard red."""
        self._require_scope_filter()
        # The element models below are transcribed from this template: a class rename must fail
        # here rather than leave the guard measuring an element that does not exist.
        self._assert_core_source_contains(
            "mail/static/src/chatter/web/chatter.xml",
            ("o-mail-Chatter-sendMessage btn", "'btn-primary active'"),
            "The chatter toggles do not carry those classes, so both this module's override and "
            "the modelled active elements below are keyed on markup core does not render.",
        )
        self.assertIsNotNone(
            PAGER_PREVIOUS_CLASSES,
            "viin_brand/tests/test_brand_cascade_compile.py must expose PAGER_ANCESTORS / "
            "PAGER_PREVIOUS_CLASSES: they model the stock `.btn-secondary` this guard compares the "
            "open Log-note toggle against.",
        )

        for arm, bundle_name, surface_note in (
            ("light", BACKEND_BUNDLE, "the light chatter"),
            ("dark", DARK_BUNDLE, "the dark chatter (#111b1e panel)"),
        ):
            css = self._compiled_css(bundle_name)

            # The oracle: what a stock `.btn-secondary` computes in this bundle.
            stock_neutral = {
                "classes": PAGER_PREVIOUS_CLASSES, "ancestors": PAGER_ANCESTORS,
                "prev_sibling": frozenset(),
            }
            neutral_fill_value, neutral_fill_rgb = self._resolve_colour(
                css, [stock_neutral], BACKGROUND_PROPS, "stock .btn-secondary fill (%s arm)" % arm
            )
            neutral_label_value, neutral_label_rgb = self._resolve_colour(
                css, [stock_neutral], ("color",), "stock .btn-secondary label (%s arm)" % arm
            )

            fills = {}
            for toggle in (".o-mail-Chatter-sendMessage", ".o-mail-Chatter-logNote"):
                with self.subTest(arm=arm, toggle=toggle):
                    # Match only rules that style the toggle itself (the subject), not rules where
                    # `<toggle>.active` sits in a :has()/ancestor condition styling another element,
                    # as the send-message composer danger cue does. CHATTER_ANCESTORS is the model
                    # the resolved read below uses, so a rule scoped under another module's root
                    # never counts.
                    bodies = _bodies_matching(
                        css,
                        lambda selector, toggle=toggle: toggle in _selector_subject(selector)
                        and ".active" in _selector_subject(selector),
                        CHATTER_ANCESTORS,
                    )
                    self.assertTrue(
                        bodies,
                        "No compiled rule styles the ACTIVE state of %s in %s - the chatter toggle "
                        "de-brand did not reach the bundle." % (toggle, bundle_name),
                    )

                    backgrounds = _declared_hexes(bodies, _BACKGROUND_RE)
                    self.assertTrue(
                        backgrounds, "active %s declares no background colour." % toggle,
                    )
                    fills[toggle] = backgrounds[-1]    # last writer wins at equal specificity

                    resting_fill = BRAND_PURPLE if arm == "light" else BRAND_CYAN
                    self.assertNotIn(
                        resting_fill, backgrounds,
                        "The OPEN %s compiled the resting fill %s in the %s bundle, which is the "
                        "RESTING fill of a `.btn-primary`: an open composer would look like a "
                        "closed one. Send message is the deep rung, Log note the default neutral."
                        % (toggle, resting_fill, arm),
                    )

                    label_values = _declared_values(bodies, _custom_property_re("btn-active-color"))
                    self.assertTrue(
                        label_values,
                        "Active %s declares no --btn-active-color, so `.btn.active { color: "
                        "var(--btn-active-color) }` falls back to the primary-button map's dark "
                        "dark purple - an unreadable label on the deep purple, and the wrong label on the "
                        "neutral." % toggle,
                    )

                    # It must also be the token Bootstrap resolves the element's `color` through:
                    # reading our own declaration back would stay green after a Bootstrap rename.
                    element = {
                        "classes": ACTIVE_CHATTER_TOGGLE_CLASSES[toggle],
                        "ancestors": CHATTER_ANCESTORS,
                        "prev_sibling": CHATTER_TOGGLE_PREV_SIBLING,
                    }
                    label_value, label_rgb = self._resolve_colour(
                        css, [element], ("color",), "active %s label (%s arm)" % (toggle, arm)
                    )
                    fill_rgb = self._assert_rgb(
                        backgrounds[-1], "active %s background (%s arm)" % (toggle, arm)
                    )
                    ratio = _contrast_ratio(label_rgb, fill_rgb)
                    self.assertGreaterEqual(
                        ratio, WCAG_AA_NORMAL_TEXT,
                        "Active %s resolves its label to %s on %s (%s) - only %.2f:1, below the "
                        "WCAG AA normal-text threshold of %.1f:1."
                        % (toggle, label_value, surface_note, backgrounds[-1], ratio,
                           WCAG_AA_NORMAL_TEXT),
                    )

                    if toggle == ".o-mail-Chatter-logNote":
                        self.assertEqual(
                            fill_rgb, neutral_fill_rgb,
                            "The OPEN 'Log note' toggle compiled %s in the %s bundle, but a stock "
                            "`.btn-secondary` in the same bundle computes %s. It must be "
                            "the DEFAULT secondary button, so the fill must be read out of "
                            "$o-btns-bs-override[\"secondary\"] - not re-typed, and not left to "
                            "core's `btn-primary active` near-white #E6F2F4."
                            % (backgrounds[-1], arm, neutral_fill_value),
                        )
                        self.assertEqual(
                            label_rgb, neutral_label_rgb,
                            "The OPEN 'Log note' label compiled %s in the %s bundle, but a stock "
                            "`.btn-secondary` computes %s. Forward the map's `color` key too, or "
                            "the neutral pill carries the primary map's label."
                            % (label_value, arm, neutral_label_value),
                        )

            send_fill = fills[".o-mail-Chatter-sendMessage"]
            note_fill = fills[".o-mail-Chatter-logNote"]
            self.assertNotEqual(
                send_fill, note_fill,
                "Both chatter toggles compiled the SAME fill %s in the %s bundle. 'Send message' is "
                "customer-facing (PURPLE = ACT) and 'Log note' is internal (the default neutral); one "
                "colour for both erases the distinction while composing." % (send_fill, arm),
            )
            expected_deep = ACTION_DEEP if arm == "light" else DARK_ACTION_DEEP
            self.assertEqual(
                send_fill, expected_deep,
                "The OPEN 'Send message' toggle compiled %s instead of the deep content rung %s in "
                "the %s bundle. Customer-facing = ACT = the content colour; its resting fill is "
                "this button's RESTING fill (open would look identical to closed) and core's "
                "untouched active-background is the near-white #F2ECF2."
                % (send_fill, expected_deep, arm),
            )

    def test_send_message_composer_carries_a_readable_danger_cue_log_note_does_not(self):
        """Composing to a customer must look different, and dangerous, from logging a note.

        Core gives the composer no per-mode chrome: its only theming hook, `--mail-Composer-bg`, is
        re-pointed per scheme, never per mode. The behaviour under test:

        1. the cue exists and is danger-derived: the send-message composer surface is measurably
           closer to $danger than the untinted fill (a property of a tint, not a hex snapshot);
        2. it is a tint, not a fill: the composer text clears WCAG AA on it in both schemes, and the
           core-dimmed placeholder is not made worse than on the untinted surface;
        3. it is scoped to send-message mode: every rule carrying it is gated on
           `.o-mail-Chatter-sendMessage.active`.

        The cue hangs off a `:has()` selector, which the class-based cascade resolver cannot
        evaluate, so the declarations are read directly and the rename hole is closed by asserting
        that core's own source still reads each lever: the `--mail-Composer-bg` consumer, the
        `border` utility's `--border-color` and the `.o-mail-Chatter-sendMessage` + `active` markup.
        The `$danger` anchor is core's own `:root --danger` emission, not a hex this module chose.

        The rule pool is ancestor-filtered through COMPOSER_ANCESTORS: a rule scoped under another
        module's root shares the `.o-mail-Composer` subject and the `:has()` gate, and would
        otherwise corrupt both halves of the comparison."""
        self._require_scope_filter()
        self._assert_core_source_contains(
            "mail/static/src/core/common/composer.scss",
            ("background-color: var(--mail-Composer-bg",),
            "Core does not paint the composer surface through --mail-Composer-bg, so the danger "
            "tint is fed to a property nothing reads and the customer-facing composer looks "
            "identical to an internal note.",
        )
        self._assert_core_source_contains(
            "mail/static/src/chatter/web/chatter.xml",
            ("o-mail-Chatter-sendMessage btn", "'active': this.state.composerType === 'message'"),
            "The chatter does not mark the Send-message toggle `active` while the message composer "
            "is open, so the `:has()` gate matches nothing and the danger cue never appears.",
        )

        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            danger_rgb = self._assert_rgb(
                self._require_root_property(css, "danger", bundle_name), "the :root --danger token"
            )
            body_rgb = self._assert_rgb(
                self._require_root_property(css, "body-color", bundle_name),
                "the :root --body-color token",
            )

            # Every declaration of the composer surface token that is not core's own must be
            # gated on the send-message toggle being active; otherwise the cue restyles every
            # composer.
            composer_bg_rules = [
                (tokens, body)
                for tokens, body in _rules_in_scope(css, COMPOSER_ANCESTORS)
                if _custom_property_re("mail-Composer-bg").search(body)
            ]
            self.assertTrue(
                composer_bg_rules,
                "Nothing declares --mail-Composer-bg in %s - the composer surface is unstyled, so "
                "the danger cue cannot be reaching it." % bundle_name,
            )
            gated = [
                (tokens, body) for tokens, body in composer_bg_rules
                if any("o-mail-Chatter-sendMessage" in token for token in tokens)
            ]
            self.assertTrue(
                gated,
                "No --mail-Composer-bg declaration in %s is gated on "
                "`.o-mail-Chatter-sendMessage.active`. The danger cue must apply to the CUSTOMER-"
                "facing composer only; an ungated one would paint the internal Log-note composer red "
                "too and destroy the very distinction it exists to make. Compiled selectors: %r"
                % (bundle_name, [tokens for tokens, _body in composer_bg_rules]),
            )
            for tokens, _body in gated:
                for token in tokens:
                    self.assertIn(
                        "active", token,
                        "A danger-tint rule matches `.o-mail-Chatter-sendMessage` without requiring "
                        "`.active` (%r), so the composer would be tinted whenever the chatter is "
                        "rendered - including while a Log note is open." % token,
                    )

            tinted_values = _declared_values(
                [body for _tokens, body in gated], _custom_property_re("mail-Composer-bg")
            )
            tinted_rgb = self._assert_rgb(tinted_values[-1], "send-message composer surface")
            untinted_rgb = self._plain_composer_surface(css, bundle_name, composer_bg_rules, gated)
            self.assertNotEqual(
                tinted_rgb, untinted_rgb,
                "The send-message composer (%s) compiled the SAME surface as the plain Log-note "
                "composer (%s) in the %s bundle - there is no cue at all."
                % (tinted_rgb, untinted_rgb, arm),
            )
            self.assertLess(
                _rgb_distance(tinted_rgb, danger_rgb), _rgb_distance(untinted_rgb, danger_rgb),
                "The send-message composer surface %s is not closer to the semantic $danger %s than "
                "the plain composer surface %s is, in the %s bundle. Whatever it is tinted with, it "
                "is not danger - and a cue the user cannot read as 'risky' is not the cue."
                % (tinted_rgb, danger_rgb, untinted_rgb, arm),
            )

            # The frame: Bootstrap's `border` utility reads --border-color, the lever core drives
            # for the composer's focus state.
            self._assert_core_source_contains(
                "mail/static/src/core/common/composer.scss",
                ("--border-color",),
                "Core does not drive the composer container's border through --border-color, so "
                "the danger frame is an orphaned declaration.",
            )
            frame_bodies = [
                body for tokens, body in _rules_in_scope(css, COMPOSER_ANCESTORS)
                if any("o-mail-Chatter-sendMessage" in token for token in tokens)
                and _custom_property_re("border-color").search(body)
            ]
            self.assertTrue(
                frame_bodies,
                "The send-message composer declares no --border-color in %s, so its container keeps "
                "the neutral hairline and the cue is a wash with no frame." % bundle_name,
            )
            frame_rgb = self._assert_rgb(
                _declared_values(frame_bodies, _custom_property_re("border-color"))[-1],
                "send-message composer frame",
            )
            self.assertEqual(
                frame_rgb, danger_rgb,
                "The send-message composer frame compiled %s instead of the semantic $danger %s in "
                "the %s bundle. The frame is the danger token, not a new hex."
                % (frame_rgb, danger_rgb, arm),
            )

            # A tint, not a fill: the composer text is a `.form-control`, so it resolves the body
            # colour and must clear AA against the tinted surface in both schemes.
            text_ratio = _contrast_ratio(body_rgb, tinted_rgb)
            self.assertGreaterEqual(
                text_ratio, WCAG_AA_NORMAL_TEXT,
                "Composer text %s on the danger-tinted surface %s is only %.2f:1 in the %s bundle - "
                "below the WCAG AA normal-text threshold of %.1f:1. The cue must stay a TINT; a fill "
                "saturated enough to hurt the text is not acceptable at any warning level."
                % (body_rgb, tinted_rgb, text_ratio, arm, WCAG_AA_NORMAL_TEXT),
            )

            # The placeholder is dimmed by core's `::placeholder { opacity }` and does not clear AA
            # on the plain composer either (~2.4:1); the rule asserted is non-degradation against
            # the same placeholder on the untinted surface, with the opacity read from the bundle.
            placeholder_alpha = self._composer_placeholder_opacity(css, bundle_name)
            tinted_placeholder = _composite(body_rgb, tinted_rgb, placeholder_alpha)
            plain_placeholder = _composite(body_rgb, untinted_rgb, placeholder_alpha)
            tinted_ratio = _contrast_ratio(tinted_placeholder, tinted_rgb)
            plain_ratio = _contrast_ratio(plain_placeholder, untinted_rgb)
            self.assertGreaterEqual(
                tinted_ratio, plain_ratio * 0.95,
                "The composer placeholder reads %.2f:1 on the danger-tinted surface but %.2f:1 on "
                "the plain one in the %s bundle - the tint DEGRADED it. Lighten the wash: the cue "
                "is carried by the frame and the hue, not by saturation."
                % (tinted_ratio, plain_ratio, arm),
            )

    def test_send_message_button_renders_the_brand_purple_under_its_forced_white_glyph(self):
        """The real send button must be the brand purple, not core's lighter `lighten($primary, 7.5%)`.

        The active send button renders through the composer action list (btnClass
        "o-sendMessageActive o-text-white") under the white glyph core forces. This module's rule has
        the same specificity as core's and wins only on load order, so the assertion reads the last
        declaration."""
        css = self._compiled_css(BACKEND_BUNDLE)
        bodies = _bodies_matching(
            css,
            lambda selector: ".o-mail-Composer-actions" in selector
            and ".o-sendMessageActive" in selector,
            ANY_ANCESTORS,
        )
        self.assertTrue(
            bodies,
            "No compiled rule targets .o-mail-Composer-actions button.o-sendMessageActive in %s - "
            "the real send button is unstyled by this module." % BACKEND_BUNDLE,
        )

        backgrounds = _declared_hexes(bodies, _BACKGROUND_RE)
        self.assertTrue(backgrounds, "the active send button declares no background colour.")
        self.assertEqual(
            backgrounds[-1], BRAND_PURPLE,
            "The active send button must compile to the BRAND purple %s; compiled "
            "backgrounds were %r (core paints it lighten($primary, 7.5%%))."
            % (BRAND_PURPLE, backgrounds),
        )
        ratio = _contrast_ratio(WHITE_RGB, self._assert_rgb(backgrounds[-1], "send button background"))
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The send button glyph is forced white by core's `o-text-white`, but its background "
            "(%s) gives only %.2f:1 - WCAG AA needs >= %.1f:1."
            % (backgrounds[-1], ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_im_status_online_dot_is_legible_on_white(self):
        """The online/bot presence dot is the success green and clears the 3:1 non-text floor on white.

        mail.ImStatus stamps its colour class on the glyph element itself
        (`o-mail-ImStatus text-success`), and the glyph is painted on whatever sits behind it. It
        carries no colour of its own: it is core's `text-success`, which viin_brand points at the
        success green. The brand cyan is only 2.33:1 on white, and the brand purple is the colour of
        an action, not of a state.

        WOULD FAIL IF REVERTED: a rule that repaints the glyph with the brand purple or cyan, or a
        success text colour under 3:1 on white."""
        css = self._compiled_css(BACKEND_BUNDLE)
        element = {
            "classes": frozenset({"oi", "o-mail-ImStatus", "d-flex", "text-success"}),
            "ancestors": IM_STATUS_ANCESTORS,
        }
        # core's `text-success` compiles to `RGBA(r, g, b, var(--text-opacity, 1))`: read the channels.
        value = self._resolve(css, [element], ("color",), ".o-mail-ImStatus.text-success")
        channels = _RGB_FUNCTIONAL_RE.match(value.strip())
        self.assertIsNotNone(channels, "%r is not an rgb() colour." % value)
        rgb = tuple(int(channels.group(index)) for index in (1, 2, 3))
        self.assertEqual(
            rgb, _to_rgb(SUCCESS_GREEN),
            "The online/bot presence dot resolves to %s, not the success green %s." % (value, SUCCESS_GREEN),
        )
        for brand_colour in (BRAND_PURPLE, FLAT_BRAND_CYAN):
            self.assertNotEqual(
                rgb, _to_rgb(brand_colour),
                "The online/bot presence dot is painted with the action colour %s." % brand_colour,
            )
        ratio = _contrast_ratio(rgb, WHITE_RGB)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NON_TEXT,
            ".o-mail-ImStatus presence dot (%s) on white is only %.2f:1 - a meaningful non-text "
            "indicator needs >= %.1f:1 (WCAG 1.4.11)." % (value, ratio, WCAG_AA_NON_TEXT),
        )

    def test_systray_unread_counters_are_the_identity_purple_with_a_readable_white_count(self):
        """The systray counters are the identity purple under a white count, in both schemes.

        They sit on the scheme-invariant chrome, so they read the navbar's own tokens, which
        viin_brand sets: `$o-navbar-badge-bg` (core navbar.variables.scss, read by
        `.o_main_navbar .o_menu_systray .badge`) is the identity purple and `$o-navbar-badge-color` is
        white. The content colour of the dark scheme is the cyan, so a counter that read it would
        change in dark; it reads the invariant purple instead. Every `.badge` of the systray follows,
        the two mail counters among them.

        The fill and the count colour are resolved on a modelled badge through core's own consumer,
        so a core rename of either token makes the branded value unreachable and the guard red."""
        # `badge` is what core's navbar consumer keys on: a rename would leave the models below
        # stale.
        self._assert_core_source_contains(
            "mail/static/src/core/web/messaging_menu_in_dropdown.xml",
            ("o-mail-MessagingMenuInDropdown-counter badge rounded-pill",),
            "The messaging systray counter does not render as a `.badge`, so core's "
            ".o_menu_systray .badge rule does not paint it and neither token applies.",
        )
        self._assert_core_source_contains(
            "mail/static/src/core/web/activity_menu.xml",
            ("o-mail-ActivityMenu-counter badge rounded-pill",),
            "The activity systray counter does not render as a `.badge`, so core's "
            ".o_menu_systray .badge rule does not paint it and neither token applies.",
        )
        for bundle in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle)
            for counter in (".o-mail-MessagingMenuInDropdown-counter", ".o-mail-ActivityMenu-counter"):
                with self.subTest(bundle=bundle, counter=counter):
                    element = {
                        "classes": SYSTRAY_COUNTER_CLASSES[counter], "ancestors": SYSTRAY_ANCESTORS,
                    }
                    background_value, background_rgb = self._resolve_colour(
                        css, [element], BACKGROUND_PROPS, "%s badge fill" % counter
                    )
                    foreground_value, foreground_rgb = self._resolve_colour(
                        css, [element], ("color",), "%s count text" % counter
                    )
                    self.assertEqual(
                        background_rgb, _to_rgb(IDENTITY_PURPLE),
                        "%s renders its badge fill %s in %s instead of the identity purple %s."
                        % (counter, background_value, bundle, IDENTITY_PURPLE),
                    )
                    ratio = _contrast_ratio(foreground_rgb, background_rgb)
                    self.assertGreaterEqual(
                        ratio, WCAG_AA_NORMAL_TEXT,
                        "%s renders its count %s on %s - only %.2f:1, and this 11px systray text "
                        "needs >= %.1f:1."
                        % (counter, foreground_value, background_value, ratio, WCAG_AA_NORMAL_TEXT),
                    )

    def test_chat_window_header_dropdown_toggle_stays_white_while_hovered_or_open(self):
        """Hovering or opening the chat-window title dropdown must keep its label white.

        Core paints the hovered/open `.o-mail-ChatWindow-moreActions` with
        `color: var(--mail-ChatWindow-moreActionsHoverColor, black) !important`; the working black
        fallback fails silently and looks deliberate on the teal chrome, whether this
        module's declaration is dropped or core renames the property.

        Resolved through core's own consumer on a modelled hovered toggle, the custom property looked
        up outwards along the chain, and the header's fill resolved the same way, so the ratio is
        measured between two computed values."""
        css = self._compiled_css(BACKEND_BUNDLE)
        header = {
            "classes": CHAT_WINDOW_HEADER_ELEMENT, "ancestors": CHAT_WINDOW_ANCESTORS,
        }
        hovered_toggle = {
            "classes": CHAT_WINDOW_MORE_ACTIONS_CLASSES,
            "ancestors": CHAT_WINDOW_HEADER_ANCESTORS,
            "states": frozenset({"hover"}),
        }

        glyph_value, glyph_rgb = self._resolve_colour(
            css, [hovered_toggle, header], ("color",), "hovered chat-window header dropdown toggle"
        )
        self.assertEqual(
            glyph_rgb, WHITE_RGB,
            "The hovered/open chat-window title dropdown resolves its label to %s. Core's own "
            "default for --mail-ChatWindow-moreActionsHoverColor is BLACK, which is unreadable on "
            "the purple header chrome, so this module must keep feeding that property white."
            % glyph_value,
        )

        header_value, header_rgb = self._resolve_colour(
            css, [header], BACKGROUND_PROPS, "chat-window header chrome"
        )
        ratio = _contrast_ratio(glyph_rgb, header_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The hovered chat-window title (%s) on the header chrome (%s) is only %.2f:1 - this is "
            "the thread name, normal text, and needs >= %.1f:1."
            % (glyph_value, header_value, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_discuss_unread_badges_render_the_identity_purple_with_a_white_count(self):
        """Every unread counter of the Discuss family is the identity purple under a white count, in
        both schemes, like the counters of the navbar.

        Core paints every `.o-discuss-badge` with
        `background-color: var(--o-discuss-badge-bg) !important` and keeps its own foreground
        (`color: white !important`); the property is declared from `$o-success` on the badge and on
        its `.o-innerBadge`, with no Sass variable. This module declares it again on the same two
        selectors from `$o-viin-brand-purple`, the scheme-invariant purple (the content colour of the
        dark scheme is the cyan, which must not reach a counter).

        Modelled on the sidebar counter and on the chat-window header counter, two sites of the
        family. The muted counter of core (`o-muted`) is declared by core at higher specificity and
        must keep its neutral tier: only the unread counters change."""
        self._assert_core_source_contains(
            "mail/static/src/core/public_web/notification_item.xml",
            ("o-mail-NotificationItem-badge o-discuss-badge",),
            "The Discuss unread counter does not carry `o-discuss-badge`, so neither "
            "core's consumer nor this module's token reaches it and the model below is stale.",
        )
        self._assert_core_source_contains(
            "mail/static/src/core/common/chat_window.xml",
            ("o-mail-ChatWindow-counter mx-1 badge rounded-pill fw-bold o-discuss-badge",),
            "The chat-window counter does not carry `o-discuss-badge`.",
        )
        sites = (
            ("sidebar counter", {
                "classes": DISCUSS_UNREAD_BADGE_CLASSES, "ancestors": DISCUSS_SIDEBAR_ANCESTORS,
            }),
            ("chat-window header counter", {
                "classes": CHAT_WINDOW_COUNTER_CLASSES, "ancestors": CHAT_WINDOW_HEADER_ANCESTORS,
            }),
        )
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            for label, badge in sites:
                with self.subTest(arm=arm, site=label):
                    fill_value, fill_rgb = self._resolve_colour(
                        css, [badge], BACKGROUND_PROPS, "Discuss %s fill (%s arm)" % (label, arm),
                    )
                    self.assertEqual(
                        fill_rgb, _to_rgb(IDENTITY_PURPLE),
                        "The Discuss %s must resolve to the identity purple %s in the %s bundle; "
                        "it resolved to %s." % (label, IDENTITY_PURPLE, arm, fill_value),
                    )
                    count_value, count_rgb = self._resolve_colour(
                        css, [badge], ("color",), "Discuss %s count (%s arm)" % (label, arm),
                    )
                    ratio = _contrast_ratio(count_rgb, fill_rgb)
                    self.assertGreaterEqual(
                        ratio, WCAG_AA_NORMAL_TEXT,
                        "The Discuss %s count (%s on %s, %s arm) is only %.2f:1 - this is small "
                        "bold text and needs >= %.1f:1."
                        % (label, count_value, fill_value, arm, ratio, WCAG_AA_NORMAL_TEXT),
                    )
            with self.subTest(arm=arm, site="muted counter"):
                muted = {
                    "classes": DISCUSS_UNREAD_BADGE_CLASSES - {"o-important"} | {"o-muted"},
                    "ancestors": DISCUSS_SIDEBAR_ANCESTORS,
                }
                _value, muted_rgb = self._resolve_colour(
                    css, [muted], BACKGROUND_PROPS, "Discuss muted counter fill (%s arm)" % arm,
                )
                self.assertNotEqual(
                    muted_rgb, _to_rgb(IDENTITY_PURPLE),
                    "A muted Discuss counter compiled the identity purple in the %s bundle: core "
                    "keeps a muted counter on its neutral tier, so it reads as already seen." % arm,
                )

    def test_seen_by_everyone_tick_clears_the_non_text_floor_as_composited(self):
        """The "seen by everyone" tick must stay legible as rendered: colour and opacity together.

        Core paints the tick `color: var(--mail-MessageSeenIndicator-hasEveryoneSeenColor,
        lighten($primary, 20%))` under `opacity-75`, so the pixel a user sees is the 75% composite
        over the message-list surface: a colour that measures well raw can fall under the
        floor composited, so a raw-colour assertion would pass a value that fails on screen. The rule is
        stated on the composited value against the WCAG 1.4.11 non-text floor, with the opacity read
        from the compiled bundle (Bootstrap's `.opacity-75`) so a core change to the dimming is
        caught too.

        The surface is modelled as white (the message list background, `$o-view-background-color`):
        stated rather than resolved, because the list background is painted by an ancestor chain
        the class-based resolver does not walk."""
        self._require_cascade_resolver()
        css = self._compiled_css(BACKEND_BUNDLE)
        # `o-hasEveryoneSeen` is what core's colour rule keys on and `opacity-75` makes the
        # composited value the real one; without them our custom property feeds nothing.
        self._assert_core_source_contains(
            "mail/static/src/discuss/core/common/message_seen_indicator.xml",
            ("o-hasEveryoneSeen opacity-75",),
            "Core does not mark the fully-seen tick with those classes, so this module's custom "
            "property is fed to an element that does not exist.",
        )
        indicator = {
            "classes": MESSAGE_SEEN_EVERYONE_CLASSES, "ancestors": MESSAGE_SEEN_ANCESTORS,
        }

        tick_value, tick_rgb = self._resolve_colour(
            css, [indicator], ("color",), "seen-by-everyone tick"
        )
        self.assertEqual(
            tick_rgb, _to_rgb(BRAND_PURPLE),
            "The seen-by-everyone tick resolves to %s; it must resolve to the BRAND purple "
            "%s fed through core's own --mail-MessageSeenIndicator-hasEveryoneSeenColor."
            % (tick_value, BRAND_PURPLE),
        )

        # Read the dimming core actually applies to this element instead of assuming 75%.
        dimming = _winning_declaration(css, indicator, ("opacity",))
        self.assertIsNotNone(
            dimming,
            "No compiled `opacity` declaration applies to the seen-by-everyone tick, but core "
            "stamps `opacity-75` on it. Either that utility is not generated or the class "
            "moved - re-ground this guard, because the composited ratio below depends on it.",
        )
        alpha = _to_alpha(dimming)
        self.assertIsNotNone(
            alpha,
            "The seen-by-everyone tick's opacity compiled to %r, which this guard cannot "
            "composite." % (dimming,),
        )

        composited = _composite(tick_rgb, WHITE_RGB, alpha)
        ratio = _contrast_ratio(composited, WHITE_RGB)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NON_TEXT,
            "The seen-by-everyone tick (%s at opacity %s) composites to rgb%r on the white message "
            "list, which is only %.2f:1 - a meaningful non-text indicator needs >= %.1f:1 (WCAG "
            "1.4.11). The flat brand cyan blends far lower here, which is exactly why the "
            "raw colour alone is not the rule."
            % (tick_value, dimming, composited, ratio, WCAG_AA_NON_TEXT),
        )

    def test_idle_presence_glyph_resolves_to_one_amber_at_all_three_render_sites(self):
        """Every idle/away glyph must resolve to the same amber, wherever it renders.

        Left to core's `.o-yellow { color: $yellow }` the glyph reads #ffc107, 1.63:1 on white. Two
        rules render the same state: the ImStatus dot (which ThreadIcon reuses as a nested
        <ImStatus>) and the "Away" swatch in the status picker, which must match the dot it
        produces. Production keeps them in step through one Sass variable; this test asserts the
        outcome by resolving both through the cascade and requiring one identical value, each rule
        pitted against core's `.o-yellow`, so a rule that stops matching is reported rather than
        assumed.

        The value is pinned: #b27400 is a literal design constant, never recomputed from
        `darken(#ffa500, 15%)`, which would compare the production expression against itself. The
        values it must not be are asserted explicitly, as both are plausible regressions: the flat
        #ffa500 and the lighter #cc8400."""
        css = self._compiled_css(BACKEND_BUNDLE)

        # The class contract these rules key on must still be the one core renders.
        self._assert_core_source_contains(
            "mail/static/src/core/common/im_status.js",
            ("return \"o-yellow\"", "o-mail-ImStatus d-flex ${this.colorClass}"),
            "Core does not render the idle glyph with that class on the glyph element, so this "
            "module's `.o-yellow` rules are inert and idle falls back to core's #ffc107.",
        )
        self._assert_core_source_contains(
            "mail/static/src/core/common/im_status_dropdown.xml",
            ("o-mail-ImStatusDropdown", "o-yellow"),
            "The status picker does not carry that menu class or that swatch class, so the "
            "picker swatch drifts away from the dot it selects.",
        )

        sites = (
            ("ImStatus presence dot", IDLE_GLYPH_CLASSES, IM_STATUS_ANCESTORS),
            ("ImStatusDropdown Away swatch", IDLE_SWATCH_CLASSES, IM_STATUS_DROPDOWN_ANCESTORS),
        )
        resolved = {}
        for label, classes, ancestors in sites:
            with self.subTest(site=label):
                element = {"classes": classes, "ancestors": ancestors}
                value, rgb = self._resolve_colour(css, [element], ("color",), label)
                resolved[label] = (value, rgb)
                self.assertNotEqual(
                    rgb, _to_rgb(CORE_YELLOW),
                    "The %s resolves to core's untouched .o-yellow %s (resolved: %s) - this "
                    "module's rule for that site is not matching." % (label, CORE_YELLOW, value),
                )
                self.assertNotEqual(
                    rgb, _to_rgb(FLAT_AWAY_ORANGE),
                    "The %s resolves to the flat orange %s, which is only 1.97:1 on the white "
                    "surface; idle is darkened for AA."
                    % (label, FLAT_AWAY_ORANGE),
                )
                self.assertNotEqual(
                    rgb, _to_rgb(LIGHTER_AWAY_AMBER),
                    "The %s resolves to the intermediate amber %s, which fails the "
                    "focused dropdown row. The shipped value is %s."
                    % (label, LIGHTER_AWAY_AMBER, AWAY_AMBER),
                )
                self.assertEqual(
                    rgb, _to_rgb(AWAY_AMBER),
                    "The %s must resolve to the branded idle amber %s; it resolved to %s."
                    % (label, AWAY_AMBER, value),
                )

        # The desync check is only meaningful once every site produced a value; when one did not,
        # its own sub-test above already carries the signal and this states why it is skipped.
        self.assertEqual(
            set(resolved), {label for label, _classes, _ancestors in sites},
            "At least one idle render site produced no colour at all, so the three sites cannot be "
            "compared - see the sub-test failure above for which rule stopped matching.",
        )
        distinct = {rgb for _value, rgb in resolved.values()}
        self.assertEqual(
            len(distinct), 1,
            "The idle glyph resolves to MORE THAN ONE colour across its render sites (%r). "
            "The status picker would not match the dot it produces - which is precisely the "
            "desync the single $o-viin-status-away variable exists to prevent."
            % ({label: value for label, (value, _rgb) in resolved.items()},),
        )

    def test_idle_presence_amber_clears_the_non_text_floor_on_every_surface_it_sits_on(self):
        """The idle amber must clear 3:1 against each real background it renders against.

        A meaningful status indicator is non-text content (WCAG 1.4.11: 3:1), and the glyph renders
        on three surfaces, the darkest being the binding constraint: plain white (the list and the
        view surface), the status-picker menu (`$dropdown-bg` ->
        `$body-bg` -> `$o-gray-100` = #f8f9fa) and the focused picker row (`$dropdown-link-hover-bg`
        = `rgba($black, 0.08)` over that menu = #e4e5e6).

        The amber is the pinned design constant (tied to production by the resolution test above);
        the ratios come from the W3C formula, an external standard. The surfaces are modelled
        values, so their provenance is re-asserted against core's own source first: a core re-theme
        turns this red and the surfaces get re-grounded."""
        # Provenance of the two dropdown surfaces, re-read from core rather than trusted.
        self._assert_core_source_contains(
            "web/static/src/scss/primary_variables.scss",
            ("$o-gray-100: #f8f9fa",),
            "The backend grey ramp moved, so the status-picker menu is not %s."
            % DROPDOWN_MENU_SURFACE,
        )
        self._assert_core_source_contains(
            "web/static/src/scss/secondary_variables.scss",
            ("$o-webclient-background-color: $o-gray-100",),
            "The webclient background does not resolve to the grey ramp, so $body-bg - and with "
            "it the dropdown menu surface - has moved.",
        )
        self._assert_core_source_contains(
            "web/static/src/scss/bootstrap_overridden.scss",
            ("$body-bg: $o-webclient-background-color", "$dropdown-link-hover-bg: rgba($black, 0.08)"),
            "The dropdown hover wash or the body background changed, so the focused picker row is "
            "not %s." % DROPDOWN_ROW_FOCUS_SURFACE,
        )
        amber_rgb = _to_rgb(AWAY_AMBER)
        self.assertIsNotNone(amber_rgb, "AWAY_AMBER must be a plain hex colour.")
        surfaces = (
            ("white view surface", WHITE_SURFACE),
            ("status-picker menu", DROPDOWN_MENU_SURFACE),
            ("focused status-picker row", DROPDOWN_ROW_FOCUS_SURFACE),
        )
        for label, surface in surfaces:
            with self.subTest(surface=label):
                ratio = _contrast_ratio(amber_rgb, self._assert_rgb(surface, label))
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NON_TEXT,
                    "The idle amber %s on the %s (%s) is only %.2f:1 - a meaningful non-text status "
                    "indicator needs >= %.1f:1 (WCAG 1.4.11)."
                    % (AWAY_AMBER, label, surface, ratio, WCAG_AA_NON_TEXT),
                )

        # Idle must stay distinguishable from online: `text-success` paints online/bot green.
        self.assertNotEqual(
            amber_rgb, _to_rgb(SUCCESS_GREEN),
            "The idle glyph resolves to the same %s as the online/bot glyph - the two presence "
            "states would be indistinguishable." % SUCCESS_GREEN,
        )

    def test_module_scss_compiles_without_errors_in_every_bundle_it_is_served_in(self):
        """Every bundle that compiles this module's SCSS must build with zero errors.

        An undefined variable, a banned Sass function or a dangling `after` anchor makes
        AssetsBundle fill css_errors and ship a "css error" stylesheet, leaving the backend
        unstyled. Both symptoms are asserted, because `.css()` returns a cached attachment without
        repopulating css_errors.

        The livechat embed is checked through its compiled parent bundle."""
        bundle_names = [BACKEND_BUNDLE, "mail.assets_public"]
        livechat = self.env["ir.module.module"].search([("name", "=", "im_livechat")], limit=1)
        if livechat.state == "installed":
            # `im_livechat.assets_embed_core` cannot compile on its own (it declares no SASS
            # helpers); `assets_embed_external` includes it with the helpers and is what the embed
            # serves.
            bundle_names.append("im_livechat.assets_embed_external")

        for bundle_name in bundle_names:
            with self.subTest(bundle=bundle_name):
                bundle, css = self._compile(bundle_name)
                self.assertFalse(
                    bundle.css_errors,
                    "%s compiled with CSS errors (expected none): %s" % (bundle_name, bundle.css_errors),
                )
                self.assertTrue(
                    css.strip(), "%s compiled to empty CSS." % bundle_name,
                )
                self.assertNotIn(
                    "css_error_message", css,
                    "%s served the AssetsBundle fallback stylesheet, i.e. a previous compile of "
                    "this bundle failed and its error payload is still cached." % bundle_name,
                )

    # Dark mode: viin_brand's dark palette recompiles every surface that reads an overridable Sass
    # variable dark-correct. The guards below cover mail-owned surfaces it cannot reach (core
    # sculpts them from literals), asserted on the compiled dark bundle against the fixed AA
    # threshold, never a hex snapshot.

    def test_dark_chatter_message_date_muted_timestamp_clears_aa_on_the_dark_thread(self):
        """The chatter message timestamp must stay a readable muted grey on the dark thread.

        Core's `.o-mail-Message-date { color: $text-muted }` compiles in the dark bundle to the dark
        scheme's muted tier (`$body-secondary-color`). The last compiled colour of the subject among
        the rules reaching a Discuss thread message is measured against the dark thread surface at
        the fixed AA threshold."""
        css = self._compiled_css(DARK_BUNDLE)
        bodies = _bodies_matching(
            css,
            lambda selector: _selector_subject(selector) == ".o-mail-Message-date",
            frozenset().union(*DISCUSS_MESSAGE_LAYERS),
        )
        self.assertTrue(
            bodies,
            "No compiled rule styles the .o-mail-Message-date element in %s - core's own message.scss "
            "is included via web.assets_web, so an empty match means the dark bundle did not build."
            % DARK_BUNDLE,
        )
        colors = _declared_values(bodies, _COLOR_RE)
        self.assertTrue(
            colors, "The .o-mail-Message-date element declares no colour in %s." % DARK_BUNDLE,
        )
        date_value, date_rgb = self._resolve_dark_colour(
            css, colors[-1], "dark chatter message-date text"
        )
        surface_value = self._dark_root_token(css, "body-bg", "dark chatter thread surface")
        surface_rgb = self._assert_rgb(surface_value, "dark chatter thread surface")
        ratio = _contrast_ratio(date_rgb, surface_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The dark chatter message timestamp (%s) on the dark thread (%s) is only %.2f:1 - this "
            "is normal muted text and needs >= %.1f:1."
            % (date_value, surface_value, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_discuss_messaging_menu_surfaces_are_readable_dark_surfaces(self):
        """The messaging menu, in the Discuss sidebar and in the systray dropdown, is a dark surface.

        Core fills the sidebar menu with `$o-view-background-color` and the dropdown panel from
        `var(--mail-MessagingMenu-bg, ...)`, which its dark file sets to `$gray-100`. Each fill is
        resolved through the compiled dark bundle and measured against the text of the menu
        ($body-color) at the fixed AA threshold."""
        css = self._compiled_css(DARK_BUNDLE)
        text_rgb = self._dark_body_color_rgb(css, "dark messaging-menu text")
        surfaces = (
            ("Discuss sidebar menu", ".o-mail-MessagingMenu", _BACKGROUND_RE),
            (
                "systray dropdown panel", ".o-mail-MessagingMenuInDropdown",
                _custom_property_re("mail-MessagingMenu-bg"),
            ),
        )
        for label, selector, pattern in surfaces:
            with self.subTest(surface=label):
                bodies = _bodies_matching(
                    css, lambda token, selector=selector: _selector_subject(token) == selector,
                    ANY_ANCESTORS,
                )
                fills = _declared_values(bodies, pattern)
                self.assertTrue(
                    fills,
                    "No compiled fill on %s (%s) in %s - core's own messaging menu styles are in "
                    "the bundle, so an empty match means the dark bundle did not build."
                    % (selector, label, DARK_BUNDLE),
                )
                fill_value, fill_rgb = self._resolve_dark_colour(css, fills[-1], label)
                ratio = _contrast_ratio(text_rgb, fill_rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "The messaging-menu text (dark $body-color) on the %s fill (%s) is only %.2f:1 - "
                    "WCAG AA normal text needs >= %.1f:1."
                    % (label, fill_value, ratio, WCAG_AA_NORMAL_TEXT),
                )

    def test_dark_discuss_thread_message_body_clears_aa_on_the_dark_thread(self):
        """A Discuss thread message body must stay readable on the dark thread and on every bubble.

        The body inherits the dark $body-color; the surface is whatever the Discuss thread chain
        paints (the Discuss root and the content panel), resolved through the cascade, and each
        bubble the body can sit on."""
        self._assert_readable_on_every_message_surface(
            DARK_BUNDLE,
            _element_chain(
                MESSAGE_BODY_CLASSES, (MESSAGE_TEXT_BODY_CLASSES,) + DISCUSS_MESSAGE_LAYERS,
            ),
            "Discuss message body",
            "The message text is the plain body colour of the scheme.",
            panel_label="the Discuss thread canvas",
        )

    def test_dark_discuss_panel_seams_recede_instead_of_glaring(self):
        """Every Discuss panel edge must be a quiet dark divider, not a bright light-mode hairline.

        Each panel carries Bootstrap's bare `.border` utility, which reads `--border-color`; the
        dark gray ramp makes that token the dark border rung.

        Asserted as a band against the fill of the panel rather than a hex: perceptible
        (`>= DISCUSS_SEAM_MIN_RATIO`) so the line exists, receding (`<= DISCUSS_SEAM_MAX_RATIO`) so
        it never glares. Border and fill are both resolved through the compiled dark bundle."""
        css = self._compiled_css(DARK_BUNDLE)
        border_rgb = self._assert_rgb(
            self._dark_root_token(css, "border-color", "dark Discuss panel border"),
            "dark Discuss panel border",
        )
        for seam in DISCUSS_DARK_SEAMS:
            with self.subTest(seam=seam.label):
                self._assert_core_source_contains(
                    seam.source, (seam.element_class.lstrip("."), "border"),
                    "The panel is not drawn with the `.border` utility any more, so the seam this "
                    "guard measures is not the one that renders.",
                )
                bodies = _bodies_matching(
                    css, lambda token, seam=seam: _selector_subject(token) == seam.element_class,
                    ANY_ANCESTORS,
                )
                fills = _declared_values(bodies, _BACKGROUND_RE)
                self.assertTrue(
                    fills,
                    "No compiled background on %s (%s) in %s - core's own stylesheet is in the "
                    "bundle, so an empty match means the dark bundle did not build."
                    % (seam.element_class, seam.label, DARK_BUNDLE),
                )
                _fill_value, fill_rgb = self._resolve_dark_colour(css, fills[-1], seam.label)
                ratio = _contrast_ratio(border_rgb, fill_rgb)
                self.assertGreaterEqual(
                    ratio, DISCUSS_SEAM_MIN_RATIO,
                    "%s border resolved to rgb%r, only %.2f:1 against its panel - it has faded "
                    "into the background instead of staying a perceptible divider (needs >= %.1f:1)."
                    % (seam.label, border_rgb, ratio, DISCUSS_SEAM_MIN_RATIO),
                )
                self.assertLessEqual(
                    ratio, DISCUSS_SEAM_MAX_RATIO,
                    "%s border resolved to rgb%r, %.2f:1 against its panel - that is a glaring "
                    "light-mode hairline, not a receding dark divider (needs <= %.1f:1)."
                    % (seam.label, border_rgb, ratio, DISCUSS_SEAM_MAX_RATIO),
                )

    def test_dark_discuss_navbar_is_the_webclients_own_not_a_discuss_only_repaint(self):
        """Opening Discuss must not repaint the navbar into a surface no other app wears.

        Core mail marks the body `o_mail_discuss` while Discuss is open. A rule keyed on that class
        that repainted the navbar would render a bar and entries unlike every other app under the
        bar's own `border-bottom`, which core web paints from `$o-navbar-border-bottom`; since
        entries are the full border-box height (see :data:`NAVBAR_CHROME_SURFACES`), each would
        paint its own fill across the 1px border row and chop the rule into dashes.

        The bar and a menu entry are each resolved twice from the same compiled dark bundle, under
        the Discuss body and under a plain webclient body, and the two must agree; nothing pins what
        the colour is, so a navbar re-tune moves both sides together. Inside Discuss the entry fill
        must also equal the bar fill, so the border row reads as in every other app."""
        css = self._compiled_css(DARK_BUNDLE)
        # The class core's Discuss-only rules key on is part of the contract: a rename would leave
        # the models stale and the guard comparing two identical plain-webclient chains.
        self._assert_core_source_contains(
            "mail/static/src/core/public_web/discuss_app/discuss_app.js",
            ("o_mail_discuss",),
            "Core mail does not mark the body with `o_mail_discuss` while Discuss is open, so "
            "the two contexts this guard compares are not the two contexts that render.",
        )
        painted = {}
        for label, element_classes, inner_layers in NAVBAR_CHROME_SURFACES:
            with self.subTest(surface=label):
                resolved = {}
                for where, body in (
                    ("with Discuss open", DISCUSS_WEBCLIENT_BODY),
                    ("in every other app", WEBCLIENT_BODY),
                ):
                    chain = _element_chain(element_classes, list(inner_layers) + [body])
                    resolved[where] = self._resolve_colour(
                        css, chain, BACKGROUND_PROPS, "%s %s" % (label, where),
                    )
                painted[label] = resolved["with Discuss open"]
                discuss_value, discuss_rgb = resolved["with Discuss open"]
                other_value, other_rgb = resolved["in every other app"]
                self.assertEqual(
                    discuss_rgb, other_rgb,
                    "%s resolves to %s (rgb%r) with Discuss open but to %s (rgb%r) in every other "
                    "app. The webclient navbar is app-independent chrome: one app repainting it "
                    "leaves that app looking like a different product, and leaves the bar's own "
                    "border rule - painted from $o-navbar-border-bottom, which no Discuss rule "
                    "follows - sitting on a surface it was never derived from."
                    % (label, discuss_value, discuss_rgb, other_value, other_rgb),
                )
        entry_value, entry_rgb = painted["a navbar menu entry"]
        bar_value, bar_rgb = painted["the navbar itself"]
        self.assertEqual(
            entry_rgb, bar_rgb,
            "With Discuss open a navbar menu entry fills %s (rgb%r) while the bar behind it fills "
            "%s (rgb%r). The entry is the full border-box height of the bar, so it paints that "
            "difference straight across the bar's 1px bottom rule and the rule renders as dashes."
            % (entry_value, entry_rgb, bar_value, bar_rgb),
        )

    def _dark_body_color_rgb(self, css, label):
        """The near-white dark body text ($body-color -> #EDF4F5), resolved through core's :root."""
        return self._assert_rgb(self._dark_root_token(css, "body-color", label), label)

    def test_dark_chat_window_body_is_a_dark_surface_under_its_message_text(self):
        """The chat-window body must be a dark surface its message text can be read on.

        The window root carries the `bg-100` utility, emitted as
        `background-color: $o-gray-100 !important`: the dark raised rung under the dark gray ramp.
        The surface it paints is resolved through the cascade and measured against the dark
        $body-color at the fixed AA threshold."""
        css = self._compiled_css(DARK_BUNDLE)
        chain = _element_chain(CHAT_WINDOW_ROOT_CLASSES, (frozenset({"o_web_client"}),))
        surface = self._rendered_backdrop(css, chain, DARK_BUNDLE, "dark chat-window body")
        text_rgb = self._dark_body_color_rgb(css, "dark chat-window message text")
        ratio = _contrast_ratio(text_rgb, surface.rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The chat-window message text (dark $body-color) on its body surface (%s, painted by %s) "
            "is only %.2f:1 - WCAG AA normal text needs >= %.1f:1."
            % (surface.value, surface.painter, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_message_bubbles_are_dark_tinted_surfaces_per_category(self):
        """Each message bubble (blue/green/orange) must be a dark tinted surface under its body text.

        Core paints each bubble from `var(--o-bubble-bg)`, which message.dark.scss and core.dark.scss
        declare per category from the dark gray ramp; the orange variant reads too bright for the
        muted tier, so this module re-points it to a dark tint of its own category colour. The last
        `--o-bubble-bg` of each `.o-mail-Message-bubble.o-#{type}` is read among the rules that
        reach this bubble (MESSAGE_BUBBLE_ANCESTORS) and measured against the dark body text at the
        fixed AA threshold."""
        self._require_scope_filter()
        css = self._compiled_css(DARK_BUNDLE)
        text_rgb = self._dark_body_color_rgb(css, "dark message bubble body text")
        for variant in ("o-blue", "o-green", "o-orange"):
            with self.subTest(bubble=variant):
                subject = ".o-mail-Message-bubble.%s" % variant
                bodies = _bodies_matching(
                    css,
                    lambda selector, subject=subject: _selector_subject(selector) == subject,
                    MESSAGE_BUBBLE_ANCESTORS,
                )
                self.assertTrue(
                    bodies,
                    "No compiled rule styles the %s bubble in %s - core's own message.scss /"
                    " message.dark.scss are in the bundle, so an empty match means the dark bundle "
                    "did not build." % (subject, DARK_BUNDLE),
                )
                fills = _declared_values(bodies, _custom_property_re("o-bubble-bg"))
                self.assertTrue(
                    fills,
                    "The %s bubble declares no --o-bubble-bg in %s." % (subject, DARK_BUNDLE),
                )
                bubble_value, bubble_rgb = self._resolve_dark_colour(
                    css, fills[-1], "%s bubble" % variant
                )
                ratio = _contrast_ratio(text_rgb, bubble_rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "The %s message bubble body text (dark $body-color) on its bubble fill (%s) is "
                    "only %.2f:1 - WCAG AA normal text needs >= %.1f:1."
                    % (variant, bubble_value, ratio, WCAG_AA_NORMAL_TEXT),
                )

    def _last_rgb(self, css, selector, pattern, label):
        """Return the opaque colour the last rule of exactly ``selector`` declares for ``pattern``."""
        bodies = _bodies_matching(css, lambda token: token == selector, ANY_ANCESTORS)
        values = _declared_values(bodies, pattern)
        self.assertTrue(values, "no compiled rule of %r declares %s" % (selector, label))
        return self._assert_rgb(values[-1], "%s (%s)" % (label, selector))

    def test_dark_activity_view_status_cells_and_counter_stay_readable(self):
        """In the dark lazy bundle the count label of a `.today` / `.planned` / `.overdue` activity
        cell reads at least 3:1 (large bold text) on its status fill, a `.done` cell label at least
        3:1 on its fill, and the cell counter label at least 4.5:1 on its `.bg-light` badge.

        The lazy bundle holds no media chrome, so `$light` / `$dark` follow the dark ramp there
        (dark label on a bright status fill); the scheme-invariant pins live in the non-lazy
        bundle only."""
        css = self._compiled_css(LAZY_DARK_BUNDLE)
        cell = ".o_activity_view .o_activity_summary_cell"
        for state in ("today", "planned", "overdue"):
            selector = "%s.%s" % (cell, state)
            fill = self._last_rgb(css, selector, _BACKGROUND_RE, "%s fill" % state)
            label = self._last_rgb(css, selector, _COLOR_RE, "%s label" % state)
            self.assertGreaterEqual(
                round(_contrast_ratio(label, fill), 2), WCAG_AA_LARGE_TEXT,
                "%s cell: rgb%r on rgb%r" % (state, label, fill),
            )
        done_fill = self._last_rgb(css, cell + ".done", _BACKGROUND_RE, "done fill")
        done_label = self._last_rgb(css, cell + ".done a", _COLOR_RE, "done label")
        self.assertGreaterEqual(
            round(_contrast_ratio(done_label, done_fill), 2), WCAG_AA_LARGE_TEXT,
            "done cell: rgb%r on rgb%r" % (done_label, done_fill),
        )
        counter = self._last_rgb(
            css, cell + " .o-mail-ActivityCell-counter", _COLOR_RE, "counter label",
        )
        dark_css = self._compiled_css(DARK_BUNDLE)
        badge_bodies = _bodies_matching(dark_css, lambda token: token == ".bg-light", ANY_ANCESTORS)
        badge_values = _declared_values(badge_bodies, _custom_property_re("background-color"))
        self.assertTrue(badge_values, "no `--background-color` declared on .bg-light")
        badge = self._resolve_dark_colour(dark_css, badge_values[-1], "activity counter badge")[1]
        self.assertGreaterEqual(
            round(_contrast_ratio(counter, badge), 2), WCAG_AA_NORMAL_TEXT,
            "activity counter: rgb%r on rgb%r" % (counter, badge),
        )

    def test_dark_followers_button_of_a_followed_record_clears_aa_on_the_chatter_panel(self):
        """The followers button of a followed record must clear AA on the dark chatter.

        The button paints its pressed state through core's
        `button.text-action.active { --color: ...; color: var(--color) !important }`, which resolves
        the brand teal, a dark tone on the dark chatter. The colour is resolved through the cascade
        over the real chain, so the custom property the rule reads is followed, and measured against
        the surface the chatter paints at the fixed AA threshold."""
        css = self._compiled_css(DARK_BUNDLE)
        chain = _element_chain(FOLLOWERS_BUTTON_CLASSES, FOLLOWERS_BUTTON_LAYERS, tag="button")
        value = self._resolve(css, chain, ("color",), "followers button")
        rgb = _opaque_rgb(value)
        self.assertIsNotNone(rgb, "The followers button resolves the colour %r, not an opaque one." % value)
        surface = self._rendered_backdrop(css, chain, DARK_BUNDLE, "followers button")
        ratio = _contrast_ratio(rgb, surface.rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The followers button renders %s on %s (%s) - only %.2f:1, where WCAG AA normal text "
            "needs >= %.1f:1." % (value, surface.value, surface.painter, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_read_notification_item_name_and_preview_clear_aa(self):
        """A read conversation's name and preview in the messaging-menu list must clear WCAG AA.

        A read (non-interesting, non-hard-muted) conversation is dimmed by core as a whole and again
        on its preview (`o-muted`); this module moves the de-emphasis onto the muted colour of the
        scheme and lifts both opacities to 1. Each node's colour and opacity, the row's included,
        are resolved through the cascade over the real row chain and composited onto the list
        surface."""
        for subject, classes in (
            ("read conversation name", NOTIFICATION_ITEM_NAME_CLASSES),
            ("read conversation preview", NOTIFICATION_ITEM_TEXT_CLASSES),
        ):
            with self.subTest(element=subject):
                self._assert_readable_on_every_message_surface(
                    DARK_BUNDLE,
                    _element_chain(classes, NOTIFICATION_ITEM_LAYERS),
                    subject,
                    "The read row's muted tier must clear AA at the opacity it is rendered with.",
                    panel_label="the messaging-menu list",
                    dimmed_by_ancestors=True,
                )

    def test_notice_rows_of_the_messaging_menu_are_readable_on_their_wash_in_both_schemes(self):
        """The name and the text of a notice row (`bg-info`, `bg-warning`) must clear AA on its wash.

        Core thins the fill of such a row to `--bg-opacity` (a 20% wash of the semantic colour over
        the menu), while the `bg-*` utility keeps the label colour it picked for a solid fill: white
        on the Viindoo info blue. The label is resolved through the cascade over the row chain, the
        wash is composited over the surface the menu paints, and the pair is measured at the fixed
        AA threshold."""
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            for variant, rgb_token in (("bg-info", "info-rgb"), ("bg-warning", "warning-rgb")):
                with self.subTest(arm=arm, variant=variant):
                    chain = _element_chain(
                        NOTIFICATION_ITEM_CLASSES | {variant, "o-important", "o-interest"},
                        NOTIFICATION_ITEM_LAYERS[2:],
                    )
                    label_value, label_rgb = self._inherited_colour(
                        css, chain, bundle_name, "%s row label" % variant,
                    )
                    row_bodies = _bodies_matching(
                        css,
                        lambda selector, variant=variant: selector == ".o-mail-NotificationItem.%s" % variant,
                        ANY_ANCESTORS,
                    )
                    opacities = _declared_values(row_bodies, _custom_property_re("bg-opacity"))
                    self.assertTrue(opacities, "no --bg-opacity declared on a %s row" % variant)
                    wash_rgb = self._assert_rgb(
                        "rgb(%s)" % self._root_token(css, rgb_token, bundle_name, "%s wash" % variant),
                        "%s wash" % variant,
                    )
                    menu = self._rendered_backdrop(css, chain[1:], bundle_name, "%s row menu" % variant)
                    painted = _composite(wash_rgb, menu.rgb, _to_alpha(opacities[-1]))
                    ratio = _contrast_ratio(label_rgb, painted)
                    self.assertGreaterEqual(
                        ratio, WCAG_AA_NORMAL_TEXT,
                        "The label of a %s row (%s) on its wash rgb%r is only %.2f:1 in the %s "
                        "bundle - WCAG AA normal text needs >= %.1f:1."
                        % (variant, label_value, painted, ratio, arm, WCAG_AA_NORMAL_TEXT),
                    )

    def test_dark_mention_suggestion_rows_clear_aa_when_active_or_hovered(self):
        """Every label of the active and of the hovered suggestion row clears AA on that row.

        Core's dark file mixes the action colour into white for both rows: a light fill under the
        scheme's light labels. The rows are read through core's own consumers: the active row's fill
        is `.o-mail-NavigableList-active`, the hovered row's is `.o-mail-NavigableList-item:hover`,
        each taking the custom property declared on the list. The labels are the link tone (the
        name) and the muted tone (the address)."""
        css = self._compiled_css(DARK_BUNDLE)
        row_chain = _element_chain(
            NAVIGABLE_LIST_ROW_CLASSES | {"o-mail-NavigableList-active"}, NAVIGABLE_LIST_LAYERS,
        )
        hover_chain = _element_chain(NAVIGABLE_LIST_ITEM_CLASSES, NAVIGABLE_LIST_LAYERS[1:])
        hover_chain[0]["states"] = frozenset({"hover"})
        muted = self._dark_root_token(css, "secondary-color", "mention row muted tier")
        rows = (
            ("active", row_chain, "link-color"),
            ("hovered", hover_chain, "link-hover-color"),
        )
        for state, chain, link_token in rows:
            with self.subTest(row=state):
                fill_value = self._resolve(css, chain, BACKGROUND_PROPS, "%s suggestion row" % state)
                fill_rgb = _opaque_rgb(fill_value)
                self.assertIsNotNone(fill_rgb, "The %s row fill %r is not opaque." % (state, fill_value))
                for label, token_value in (
                    ("name", self._dark_root_token(css, link_token, "mention row link tier")),
                    ("address", muted),
                ):
                    _value, label_rgb = self._resolve_dark_colour(
                        css, token_value, "%s row %s" % (state, label),
                    )
                    ratio = _contrast_ratio(label_rgb, fill_rgb)
                    self.assertGreaterEqual(
                        ratio, WCAG_AA_NORMAL_TEXT,
                        "The %s suggestion row paints %s and its %s reads %s: only %.2f:1, where "
                        "WCAG AA normal text needs >= %.1f:1."
                        % (state, fill_value, label, token_value, ratio, WCAG_AA_NORMAL_TEXT),
                    )

    def test_dark_date_divider_label_clears_aa_in_every_container(self):
        """The thread's day divider ("Today") must be readable on every dark thread surface.

        The label stacks `text-muted` on `opacity-50`, so the muted tier is halved again; the rule
        that cancels the utility leaves the de-emphasis with the muted colour."""
        for container, panel_label, message_layers in DARK_MESSAGE_CONTAINERS:
            with self.subTest(container=container):
                thread_layers = message_layers[len(MESSAGE_SUBTREE_TO_THREAD_LAYERS) - 1:]
                self._assert_readable_on_every_message_surface(
                    DARK_BUNDLE,
                    _element_chain(
                        DATE_SECTION_LABEL_CLASSES, (DATE_SECTION_CLASSES,) + thread_layers,
                        tag="span",
                    ),
                    "day divider label (%s)" % container,
                    "The divider's `opacity-50` halves the muted tier; "
                    "cancel the utility rather than lowering the floor.",
                    panel_label=panel_label,
                )

    def test_dark_member_list_section_header_clears_aa_on_the_sidebar_surface(self):
        """The "Online" / "Offline" section headers of the Discuss members panel must clear AA.

        The header stacks `text-muted` on `opacity-75`, so the muted tier is dimmed again on the
        raised sidebar surface; the utility is important, so only an important rule cancels it."""
        self._assert_readable_on_every_message_surface(
            DARK_BUNDLE,
            _element_chain(
                MEMBER_LIST_HEADER_CLASSES, MEMBER_LIST_PANEL_LAYERS, tag="h6",
            ),
            "members panel section header",
            "The header's `opacity-75` dims the muted tier a second "
            "time; cancel the utility rather than lowering the floor.",
            panel_label="the members panel",
        )

    def test_dark_read_notification_item_timestamp_clears_aa(self):
        """The timestamp of a read conversation in the messaging menu must clear AA.

        The read row is dimmed as a whole and its timestamp is dimmed again (`o-muted`), so the
        opacity is multiplied twice; only a rule on the row and on the timestamp cancels both."""
        self._assert_readable_on_every_message_surface(
            DARK_BUNDLE,
            _element_chain(
                NOTIFICATION_ITEM_DATE_CLASSES,
                NOTIFICATION_ITEM_LAYERS,
                tag="small",
            ),
            "read conversation timestamp",
            "The read row's opacities dim the muted tier a second "
            "time; cancel them rather than lowering the floor.",
            panel_label="the messaging-menu list",
            dimmed_by_ancestors=True,
        )

    def test_dark_active_messaging_menu_tab_label_and_icon_are_readable(self):
        """The active bottom-navigation tab keeps a readable label and a visible icon.

        The tab reads its label from `--btn-active-color` and paints its icon with the same accent,
        on the component-active tint; the enterprise teal of the light scheme is too dark for both
        grounds."""
        css = self._compiled_css(DARK_BUNDLE)
        label_chain = _element_chain(MESSAGING_MENU_TAB_LABEL_CLASSES, MESSAGING_MENU_LAYERS)
        label_value, label_rgb = self._inherited_colour(
            css, label_chain, DARK_BUNDLE, "active tab label"
        )
        label_surface = self._rendered_backdrop(css, label_chain, DARK_BUNDLE, "active tab label")
        label_ratio = _contrast_ratio(label_rgb, label_surface.rgb)
        self.assertGreaterEqual(
            label_ratio, WCAG_AA_NORMAL_TEXT,
            "The active tab label %s on %s reads only %.2f:1, where WCAG AA normal text needs >= "
            "%.1f:1." % (label_value, label_surface.value, label_ratio, WCAG_AA_NORMAL_TEXT),
        )
        icon_chain = _element_chain(MESSAGING_MENU_TAB_ICON_CLASSES, MESSAGING_MENU_LAYERS)
        icon_value, icon_rgb = self._inherited_colour(
            css, icon_chain, DARK_BUNDLE, "active tab icon"
        )
        icon_surface = self._rendered_backdrop(css, icon_chain, DARK_BUNDLE, "active tab icon")
        icon_ratio = _contrast_ratio(icon_rgb, icon_surface.rgb)
        self.assertGreaterEqual(
            icon_ratio, WCAG_AA_NON_TEXT,
            "The active tab icon %s on %s reads only %.2f:1, where WCAG 1.4.11 needs >= %.1f:1."
            % (icon_value, icon_surface.value, icon_ratio, WCAG_AA_NON_TEXT),
        )

    def test_dark_composer_input_fill_clears_aa_under_its_text(self):
        """The composer field must be a dark fill its input text can be read on.

        The field is `.o-mail-Composer-bg { background-color: var(--mail-Composer-bg,
        $o-view-background-color) }` with a transparent input over it, and core's dark file sets
        `--mail-Composer-bg` on `.o-mail-Composer` to a raised dark tone. The last-declared value
        among the rules that reach this composer (COMPOSER_ANCESTORS) is measured against the dark
        body text at the fixed AA threshold."""
        self._require_scope_filter()
        css = self._compiled_css(DARK_BUNDLE)
        bodies = _bodies_matching(
            css, lambda selector: _selector_subject(selector) == ".o-mail-Composer",
            COMPOSER_ANCESTORS,
        )
        fills = _declared_values(bodies, _custom_property_re("mail-Composer-bg"))
        self.assertTrue(
            fills,
            "No compiled --mail-Composer-bg on .o-mail-Composer in %s - core's own composer.dark.scss "
            "is in the bundle, so an empty match means the dark bundle did not build." % DARK_BUNDLE,
        )
        fill_value, fill_rgb = self._resolve_dark_colour(css, fills[-1], "dark composer field")
        text_rgb = self._dark_body_color_rgb(css, "dark composer input text")
        ratio = _contrast_ratio(text_rgb, fill_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The composer input text (dark $body-color) on the composer field (%s) is only %.2f:1 - "
            "WCAG AA normal text needs >= %.1f:1."
            % (fill_value, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_message_bubble_is_composited_only_for_elements_inside_the_text_body_wrapper(self):
        """A full-bleed sibling must be the surface for what it covers, and for nothing else.

        Every contrast assertion here is only as true as the surface it measures against, and a
        guard that composites the wrong layer reports a confident, precise, wrong number.
        `.o-mail-Message-bubble` is `position-absolute top-0 start-0 w-100 h-100` inside
        `.o-discuss-text-body`, so it is the surface for the glyphs inside that wrapper and for no
        others: it is a sibling of the body, not an ancestor, and not in the timestamp's subtree at
        all (the timestamp sits in `.o-mail-Message-header`, outside the content container).

        Asserted without pinning the bubble's or the panel's colour: declaring the bubble changes
        the resolved surface for the message body and does not change it for the timestamp. An
        ancestor-only resolver fails the first half; a resolver handing the bubble to every element
        in the message subtree fails the second. Both bundles are checked: the rule is a DOM fact,
        independent of the scheme."""
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.xml",
            ("o-mail-Message-bubble position-absolute top-0 start-0 w-100 h-100",
             "d-inline-block o-discuss-text-body",
             'class="o-mail-Message-date o-xsmaller"'),
            "The bubble is not a full-bleed element inside `.o-discuss-text-body`, or the "
            "timestamp is not outside it, so the containment rule this guard pins is keyed on "
            "markup core does not render - re-transcribe it from message.xml.",
        )
        body_chain = _element_chain(MESSAGE_BODY_CLASSES, CHATTER_TEXT_BODY_LAYERS)
        date_chain = _element_chain(MESSAGE_DATE_CLASSES, CHATTER_MESSAGE_HEADER_LAYERS)
        composer_chain = _element_chain(
            COMPOSER_INPUT_CLASSES, COMPOSER_INPUT_CHATTER_LAYERS + CHATTER_PANEL_LAYERS
        )

        for sibling in MESSAGE_BUBBLE_SIBLINGS:
            with self.subTest(bubble=sibling.label, containment="inside the wrapper"):
                self.assertIsNotNone(
                    _painted_sibling_chain(body_chain, sibling),
                    "`.o-mail-Message-body` is a sibling of the %s inside `.o-discuss-text-body`, so "
                    "the bubble IS the surface under its glyphs. Resolving no chain for it means "
                    "the surface model composites ancestors only."
                    % sibling.label,
                )
            with self.subTest(bubble=sibling.label, containment="outside the wrapper"):
                self.assertIsNone(
                    _painted_sibling_chain(date_chain, sibling),
                    "`.o-mail-Message-date` renders in `.o-mail-Message-header`, a sibling of the "
                    "content container - the %s is several layers further in and is never painted "
                    "behind a timestamp. Resolving a chain for it credits the timestamp with a "
                    "surface it does not render on."
                    % sibling.label,
                )
            with self.subTest(bubble=sibling.label, containment="the wrapper itself"):
                self.assertIsNone(
                    _painted_sibling_chain(composer_chain, sibling),
                    "The composer textarea carries `o-discuss-text-body` on its OWN element, so it "
                    "CONTAINS that wrapper rather than sitting next to a bubble inside one - and no "
                    "message bubble is in its subtree at all. Matching the subject's own classes "
                    "instead of a strict ancestor is what puts a message surface under a composer "
                    "field.",
                )

        for bundle_name in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle_name)
            plain_body = self._rendered_backdrop(
                css, body_chain, bundle_name, "message body surface, no bubble declared"
            )
            plain_date = self._rendered_backdrop(
                css, date_chain, bundle_name, "message timestamp surface"
            )
            for sibling in MESSAGE_BUBBLE_SIBLINGS:
                bubbled_body = self._rendered_backdrop(
                    css, body_chain, bundle_name, "message body surface",
                    siblings=(sibling,),
                )
                bubbled_date = self._rendered_backdrop(
                    css, date_chain, bundle_name, "message timestamp surface",
                    siblings=(sibling,),
                )
                with self.subTest(bundle=bundle_name, bubble=sibling.label, guard="not vacuous"):
                    self.assertNotEqual(
                        bubbled_body.rgb, plain_body.rgb,
                        "In %s the %s resolves the same colour as the panel behind it (%s, rgb%r), "
                        "so this guard cannot tell an ancestor-only surface model from a correct "
                        "one and every bubble assertion in this file measures nothing. Re-ground it "
                        "rather than leaving it green."
                        % (bundle_name, sibling.label, plain_body.value, plain_body.rgb),
                    )
                with self.subTest(bundle=bundle_name, bubble=sibling.label, direction="applied"):
                    self.assertEqual(
                        bubbled_body.painter, sibling.label,
                        "In %s the message body resolves its surface from %s even with the %s "
                        "declared behind it. The bubble fills `.o-discuss-text-body` edge to edge "
                        "so it - not the layer behind it - is what the body text is read on."
                        % (bundle_name, bubbled_body.painter, sibling.label),
                    )
                with self.subTest(bundle=bundle_name, bubble=sibling.label, direction="not applied"):
                    self.assertEqual(
                        (bubbled_date.painter, bubbled_date.rgb),
                        (plain_date.painter, plain_date.rgb),
                        "In %s declaring the %s CHANGED the surface the message timestamp is "
                        "measured against - from %s (rgb%r) to %s (rgb%r). The timestamp renders in "
                        "`.o-mail-Message-header`, outside "
                        "`.o-discuss-text-body` entirely, so no bubble is ever painted behind it "
                        "and the ancestor walk IS its surface. Applying an overlay to every element "
                        "in the message subtree measures the timestamp against a colour it never "
                        "renders on."
                        % (bundle_name, sibling.label, plain_date.painter, plain_date.rgb,
                           bubbled_date.painter, bubbled_date.rgb),
                    )

    # Light mode: the muted and dimmed tiers of an ordinary form-view chatter in
    # `web.assets_backend`. Each is an already-translucent ink (`$text-muted` is
    # `rgba($o-gray-700, .76)`), optionally dimmed by an `opacity` utility, composited onto the
    # surface the message renders on: the light panel, or a bubble. A tier tuned against the panel
    # alone is not enough, hence the painted-sibling model.

    def test_light_message_timestamp_muted_tier_clears_aa_on_the_chatter_panel(self):
        """The message timestamp must be readable in an ordinary light-mode chatter.

        `.o-mail-Message-date { color: $text-muted }` with
        `$text-muted = rgba($o-gray-700, $o-opacity-muted)` is a 76%-alpha wash of #495057, a sub-AA
        grey on the light panel; and the panel is not white: `.o-mail-Form-chatter` paints
        `$o-webclient-background-color` = `$o-gray-100`, one step darker. The surface is resolved,
        not assumed white: the timestamp is the one subject here that never sits on a bubble (it
        lives in `.o-mail-Message-header`, outside `.o-discuss-text-body`), so its surface is
        whatever the ancestor walk lands on."""
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.scss",
            (".o-mail-Message-date {", "color: $text-muted;"),
            "The timestamp does not take `$text-muted`, so this guard measures a tier core does "
            "not apply to it.",
        )
        self._assert_readable_on_every_message_surface(
            BACKEND_BUNDLE,
            _element_chain(MESSAGE_DATE_CLASSES, CHATTER_MESSAGE_HEADER_LAYERS),
            "message timestamp",
            "This is the muted secondary tier every form-view chatter reads its dates in, so it "
            "has to clear AA on the panel it actually renders on - not on the white it is easy to "
            "assume. Re-point `$text-muted` or the timestamp's own rule; do not lower the floor.",
        )

    def test_light_empty_message_placeholder_clears_aa_on_every_surface_it_lands_on(self):
        """The placeholder shown for a contentless message must be readable, panel or bubble.

        Core renders `<i class="text-muted opacity-75">` in place of a body, stacking two dimmings
        chosen alone: the muted tier is already a 76%-alpha wash and `.opacity-75` composites the
        element again, so the glyphs paint at an effective 57%. The placeholder is a child of
        `.o-mail-Message-body`, so a bubbled message paints its bubble behind it: the same surface
        split as the message body, resolved through the same declared overlay.

        Asserted as compiled contrast, never a hex or an opacity literal: both the tier alpha and
        the utility opacity are read from the bundle, so dropping `opacity-75`, darkening the tier or
        re-tuning the bubbles all satisfy it."""
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.xml",
            ('t-if="this.message.isEmpty" class="text-muted opacity-75"',),
            "The empty-message placeholder does not carry those classes, so the element model "
            "below is keyed on markup core does not render.",
        )
        self._assert_readable_on_every_message_surface(
            BACKEND_BUNDLE,
            _element_chain(MESSAGE_EMPTY_PLACEHOLDER_CLASSES, CHATTER_BODY_MUTED_LAYERS,
                           tag=MESSAGE_EMPTY_PLACEHOLDER_TAG),
            "empty-message placeholder",
            "`text-muted opacity-75` dims an already-translucent tier a second "
            "time, and the two dimmings were chosen independently. This is the ONLY text a "
            "contentless message shows, so it cannot be the least readable thing on the screen.",
        )

    def test_light_edited_marker_clears_aa_on_every_surface_it_lands_on(self):
        """The `(edited)` marker must stay readable, not merely present.

        Core renders `<span class="o-xsmaller opacity-50"> (edited)</span>` into the
        `.o-mail-Message-edited` marker the server writes into the body HTML. It declares no colour,
        so it inherits the body tier (core's bare-class `!important` on `.o-discuss-text-body`) and
        then halves it, turning a comfortable body tier into a sub-AA marker that carries real
        information about the message's history. It renders inside `.o-mail-Message-body`, so a
        bubbled message paints its bubble behind it as behind the body text."""
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.xml",
            ('<t t-name="mail.Message.edited">', 'class="o-xsmaller opacity-50"'),
            "The `(edited)` marker does not carry those classes, so the element model below is "
            "keyed on markup core does not render.",
        )
        self._assert_readable_on_every_message_surface(
            BACKEND_BUNDLE,
            _element_chain(MESSAGE_EDITED_MARKER_CLASSES, CHATTER_EDITED_MARKER_LAYERS,
                           tag=MESSAGE_EDITED_MARKER_TAG),
            "(edited) marker",
            "`opacity-50` halves the body tier this marker inherits. It tells a "
            "reader the message was changed after posting, so it has to be legible; re-point the "
            "marker or drop the dimming rather than lowering the floor.",
        )

    # Dark mode: the same two dimmed nodes. In dark the ink is light and the ground dark, so the
    # dimming pulls them toward the surface from the other side and from a different starting tier:
    # the placeholder's `.text-muted` is re-pointed by dark_palette.scss onto
    # `$body-secondary-color`, and the marker inherits core's dark `.o-discuss-text-body`
    # `!important` rather than the light one. They are separate guards, not a bundle argument on
    # the light ones.
    #
    # `Thread` renders the identical subtree in three containers that paint different panels: the
    # form-view chatter takes `$o-webclient-background-color`, Discuss and the chat window take the
    # view surface, a lighter dark. The chatter panel is the darkest and so the most forgiving;
    # measuring it alone measures the best case. The markup transcription is pinned once, by the
    # light guards.
    def _assert_dark_node_readable_in_every_container(self, subject_layers, element, tag, subject,
                                                      why):
        """Assert one dimmed body node clears AA on every dark surface, in every container.

        The three container panels are two distinct darks, so a rule tuned against the chatter
        alone leaves Discuss and the chat window short.

        :param subject_layers: maps a container's message layers to the node's ancestor layers
        :param element: the node's classes
        :param tag: the node's HTML tag
        :param subject: the node's name in failure messages
        :param why: the remedy stated in a failure message
        """
        for container, panel_label, message_layers in DARK_MESSAGE_CONTAINERS:
            with self.subTest(container=container):
                self._assert_readable_on_every_message_surface(
                    DARK_BUNDLE,
                    _element_chain(element, subject_layers(message_layers), tag=tag),
                    "%s (%s)" % (subject, container),
                    why,
                    panel_label=panel_label,
                )

    def test_dark_empty_message_placeholder_clears_aa_in_every_container_it_renders_in(self):
        """The placeholder shown for a contentless message must be readable on the dark palette.

        On the dark palette `.text-muted` is re-pointed by dark_palette onto
        `$body-secondary-color`, an opaque mid grey that is a deliberate dark muted tier, and
        `.opacity-75` then composites the whole element down onto whatever is behind it: the product
        of the two was chosen by nobody. The darkest panel (the form-view chatter) clears the floor
        most easily, so every surface is its own subTest: an average over them is above the floor,
        and a reader never sees an average.

        Asserted as compiled contrast, never a hex or an opacity literal. The placeholder is a
        direct child of `.o-mail-Message-body`, so a bubbled message paints its bubble behind it;
        both halves of the selector core styles it through are modelled (the `<i>` tag and the child
        relation), so a `.o-mail-Message-body > i.text-muted.opacity-75` fix is exercised rather
        than routed around."""
        self._assert_dark_node_readable_in_every_container(
            _body_muted_layers,
            MESSAGE_EMPTY_PLACEHOLDER_CLASSES,
            MESSAGE_EMPTY_PLACEHOLDER_TAG,
            "empty-message placeholder",
            "`text-muted opacity-75` dims the dark muted tier a second time, and "
            "the two dimmings were chosen independently. This is the ONLY text a contentless "
            "message shows, so it cannot be the least readable thing on the screen - and a fix has "
            "to hold on every panel and every bubble, not on the darkest panel alone.",
        )

    def test_dark_edited_marker_clears_aa_in_every_container_it_renders_in(self):
        """The `(edited)` marker must stay readable on the dark palette, not merely present.

        `<span class="o-xsmaller opacity-50">` declares no colour, so it inherits the dark body tier
        core forces on `.o-discuss-text-body` as a bare-class `!important` and then halves it;
        halving a near-white ink on a dark ground walks it toward the surface, so the dimming is the
        whole defect. Every panel clears the floor; only the bubbles can fall short, because each
        bubble is a lighter dark than the panel behind it. A guard modelling the panel only would be
        green in all three containers while every bubbled message showed a sub-AA marker, which is
        why the painted-sibling overlay is a declared input.

        The marker tells a reader the message was changed after posting, so it has to be legible;
        the remedy belongs on the dimming or the bubbles, never on the floor."""
        self._assert_dark_node_readable_in_every_container(
            _edited_marker_layers,
            MESSAGE_EDITED_MARKER_CLASSES,
            MESSAGE_EDITED_MARKER_TAG,
            "(edited) marker",
            "`opacity-50` halves the dark body tier this marker inherits, and on "
            "a dark ground halving walks the ink toward the surface. Every bubble is a lighter dark "
            "than the panel behind it, so a marker tuned against the panel cannot clear AA on one.",
        )

    # Compiling `web.assets_web_dark` through this registry's installed modules is silent about an
    # install-topology hazard: mail_dark.scss reads a bare Sass variable (`color: $text-muted;`, no
    # `!default`) and any module compiled into the same bundle may assign it first. `hr_skills` does:
    # its `report_employee_cv.scss` writes `$text-muted: #3b4757;` and its manifest globs that
    # directory into `web.assets_backend`, which `web.assets_web_dark` includes. A DB without
    # hr_skills never sees it.
    #
    # `TransactionCase` forbids the `cr.commit()` a real install needs, so the bundle's real SCSS
    # sources are recompiled through Odoo's own entry point (`AssetsBundle.compile_css` ->
    # `ScssStylesheetAsset.compile`) with one extra line spliced in ahead of this module's own
    # `mail_dark.scss`. The splice point need not match hr_skills' real position: `$text-muted` is a
    # global variable with no `!default`, so the last assignment before the read wins, and nothing
    # can assign it between the splice and the read.
    def _compiled_css_with_text_muted_clobbered(self, bundle_name):
        """Recompile ``bundle_name`` with one extra, unprotected `$text-muted` write spliced in.

        :return: real compiled CSS from Odoo's own compiler, read like `self._compiled_css`'s output
        """
        self.assertIsNotNone(
            ScssStylesheetAsset,
            "odoo.addons.base.models.assetsbundle must expose ScssStylesheetAsset - every web/mail "
            "SCSS source compiles through it, and this guard needs it to isolate the SCSS assets "
            "(not the JS ones) inside the bundle it re-derives.",
        )
        bundle = self.env["ir.qweb"]._get_asset_bundle(bundle_name, css=True, js=False)
        scss_assets = [
            asset for asset in bundle.stylesheets if isinstance(asset, ScssStylesheetAsset)
        ]
        self.assertTrue(
            scss_assets,
            "%s carries no compiled SCSS asset at all, so there is no real Odoo SCSS compile to "
            "splice a probe into." % bundle_name,
        )
        marker_index = next(
            (index for index, asset in enumerate(scss_assets)
             if asset.url and asset.url.endswith("/" + os.path.basename(DARK_SURFACE_SOURCE))),
            None,
        )
        self.assertIsNotNone(
            marker_index,
            "%s does not inject %s as its own SCSS asset, so there is no place to splice "
            "an external `$text-muted` write immediately ahead of THIS module's own read of it."
            % (bundle_name, DARK_SURFACE_SOURCE),
        )
        sources = [asset.get_source() for asset in scss_assets]
        clobber = (
            "/* test-injected stand-in for hr_skills' unprotected global Sass variable write */\n"
            "$text-muted: #3b4757;\n"
        )
        spliced_source = "\n".join(sources[:marker_index] + [clobber] + sources[marker_index:])
        css = bundle.compile_css(scss_assets[0].compile, spliced_source)
        self.assertTrue(
            css.strip(),
            "%s compiled to empty CSS once an unprotected $text-muted write was spliced ahead of "
            "%s - either the splice broke the real Sass compile outright, or this guard's own "
            "harness is wrong; either way no marker colour can be measured against it."
            % (bundle_name, DARK_SURFACE_SOURCE),
        )
        return css

    def _assert_readable_on_every_message_surface_in(
        self, css, bundle_name, chain, subject, why, panel_label="the chatter panel",
    ):
        """The ``css``-parameterised twin of :meth:`_assert_readable_on_every_message_surface`.

        ``css`` is handed in rather than fetched by bundle name through the per-class cache, because
        the css under test is a one-off recompile that this DB's registry never serves."""
        ink_value, ink_rgb, alpha = self._rendered_ink(css, chain, bundle_name, subject)
        surfaces = [(panel_label, ())]
        surfaces += [(sibling.label, (sibling,)) for sibling in MESSAGE_BUBBLE_SIBLINGS
                     if _painted_sibling_chain(chain, sibling) is not None]
        for label, siblings in surfaces:
            with self.subTest(surface=label):
                backdrop = self._rendered_backdrop(
                    css, chain, bundle_name, "%s surface" % subject, siblings=siblings,
                )
                painted = _composite(ink_rgb, backdrop.rgb, alpha)
                ratio = _contrast_ratio(painted, backdrop.rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "In %s the %s renders %s at an effective alpha of %.4f - painting rgb%r - on "
                    "%s (%s, rgb%r), only %.2f:1 where WCAG AA normal text needs >= %.1f:1. %s"
                    % (bundle_name, subject, ink_value, alpha, painted, label, backdrop.value,
                       backdrop.rgb, ratio, WCAG_AA_NORMAL_TEXT, why),
                )

    def test_dark_edited_marker_stays_readable_when_another_module_hijacks_text_muted(self):
        """The `(edited)` marker's dark colour must not depend on `$text-muted` staying unassigned.

        mail_dark.scss reads `color: $text-muted;`, a bare Sass variable, so whichever module's SCSS
        assigns it last before that rule wins. `hr_skills` assigns it with no `!default` and reaches
        `web.assets_web_dark` whenever it is installed alongside this module, which the other dark
        guards (reading this registry's actual install) cannot observe on a DB without it.

        Asserted as the compiled contrast of the marker against every dark surface it renders on,
        recompiled with hr_skills' literal spliced one line ahead of this module's own contribution
        (see `_compiled_css_with_text_muted_clobbered`). Any fix that stops reading `$text-muted`
        (a Bootstrap-emitted custom property, a private Sass variable) clears it; a fix that still
        reads `$text-muted` under another name does not."""
        css = self._compiled_css_with_text_muted_clobbered(DARK_BUNDLE)
        for container, panel_label, message_layers in DARK_MESSAGE_CONTAINERS:
            with self.subTest(container=container):
                self._assert_readable_on_every_message_surface_in(
                    css, DARK_BUNDLE,
                    _element_chain(MESSAGE_EDITED_MARKER_CLASSES, _edited_marker_layers(message_layers),
                                   tag=MESSAGE_EDITED_MARKER_TAG),
                    "(edited) marker (%s) under a hijacked $text-muted" % container,
                    "hr_skills - or any other module sharing this compile - can reassign "
                    "`$text-muted` with no `!default` before mail_dark.scss's own rule reads it. "
                    "The marker has to clear AA regardless of what else shares the bundle, not only "
                    "on a DB where hr_skills happens to be absent.",
                    panel_label=panel_label,
                )
