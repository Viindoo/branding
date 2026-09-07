# Compiled-render contrast guards for the viin_brand_mail chrome (ODOO-AI-ETHOS #8).
#
# WHAT IS PROTECTED. The 19.0 port of this module lost the 18.0 heritage `$brand-primary` (TEAL)
# and substituted the brand PURPLE `$o-brand-secondary` on several chat/composer/presence
# surfaces, and left every foreground on those surfaces at its core default. The result was a set
# of surfaces that RENDER unreadable - measured live by the ui-debugger:
#   * chat-window header               purple #6C386F instead of brand teal
#   * chat-window header action icons  #212529 at 50% opacity = 1.79:1 (composited 2.30:1 white)
#   * chatter active send/log toggle   dark-teal #002428 label on the purple fill = 1.07:1
#   * composer send button             core `lighten($primary, 7.5%)` under a forced white glyph
#   * im_status presence dot           purple, and the flat brand teal is only 2.33:1 on white
#   * systray unread counters          $o-success #00B365 + white = 2.75:1 on the navbar
# The design SSOT (.odoo-ai/designs/cluster-semantic-restore-2026-07-24.md, section
# "MODULE viin_brand_mail") restores each surface on the AA-pushed ladder, so the BUSINESS RULE
# these tests protect is a CONTRAST rule, not a hex snapshot: every glyph/label must clear the
# WCAG threshold against the surface it actually renders on. Each test therefore measures the
# WCAG 2.x contrast ratio of the COMPILED colours (the W3C formula is an external standard, not a
# re-implementation of any production logic) instead of only comparing literals - a hex-only test
# would go green again the moment someone swapped in a different, equally unreadable shade.
#
# WHY A COMPILED-CSS GUARD AND NOT A BROWSER TOUR. These surfaces are produced by SASS at asset
# COMPILE time from variables that live three modules away (`$o-navbar-background`,
# `$o-brand-secondary`, `$o-success` in viin_brand_web/static/src/scss/brand_variables.scss),
# so the observable output is the compiled bundle. Asserting it needs no browser, is
# deterministic, and runs inside this module's own suite. Same mechanism as the established
# in-repo guards viin_brand_web/tests/test_brand_color_compile.py and
# viin_brand_html_editor/tests/test_asset_upgrade.py.
#
# WHY THE EXPECTED HEXES ARE ASSERTED THE WAY THEY ARE. Two different shapes on purpose:
#   * where the design SSOT names a TOKEN (CHROME-BASE teal #007F8E, brand secondary #7F4282) the
#     token is asserted as a fixed, hand-chosen design constant - the same discipline as
#     viin_brand_web's VIINDOO_NAVBAR_BACKGROUND_COLOR, and never by re-deriving the Sass
#     expression inside the test (which would compare production logic against itself);
#   * where the value is DERIVED with no named token (the systray badge green, `mix(black,
#     $o-success, 28%)`) only the RULE is asserted - still a green, no longer the unreadable
#     $o-success, and AA against its own foreground - so a later re-tune of the mix percentage
#     that still satisfies the rule is not a false alarm.
#
# CASCADE SEMANTICS, AND THE ANCESTOR CONTEXT THAT QUALIFIES THEM. This module's SCSS is injected
# `after` the core file it overrides, so among the rules that REACH a given element the LAST
# declaration at equal specificity is what renders. Every assertion below therefore reads the LAST
# matching declaration, exactly as a browser would resolve it: if this module's rule went missing,
# the last writer would be core's and the assertion fails.
#
# "Reach the element" is the load-bearing half, and it is NOT a property of the subject alone. A
# rule scoped to an ancestor - `.o-spreadsheet .o-mail-Chatter .o-mail-Chatter-sendMessage.active`,
# say - has the very SUBJECT a guard keys on while applying to an element in a different context
# entirely; a browser never paints it on the chatter in a form view, so a guard that read it as the
# last writer would report a colour that renders nowhere near the surface it names. That is a
# systemic hazard, not a property of any one module: any addon in the bundle may scope a rule under
# its own root at any time. So every guard that reads raw declarations passes the ANCESTOR POOL of
# the element it measures, and `_bodies_matching` / `_rules_in_scope` drop any rule demanding an
# ancestor class that element does not have - through the cluster's single ancestor model
# (`_selector_scope_applies`, imported from viin_brand_web, ODOO-AI-ETHOS #11 SSOT). Guards whose
# ancestor chain has not been transcribed yet pass the explicit `ANY_ANCESTORS` sentinel, which
# makes each one a locatable one-line upgrade instead of a silent assumption.
#
# WHY THE CUSTOM-PROPERTY GUARDS RESOLVE THROUGH CORE'S OWN CONSUMER (finding R-7)
# -------------------------------------------------------------------------------------------------
# Several surfaces here are restored by DECLARING a CSS custom property that CORE reads
# (--btn-active-color, --o-navbar-badge-bg, --o-discuss-badge-bg,
# --mail-ChatWindow-moreActionsHoverColor, --mail-MessageSeenIndicator-hasEveryoneSeenColor).
# Reading OUR OWN declaration back out of the compiled bundle and measuring it against itself is
# NOT a behaviour assertion: if core renames the property, our declaration is orphaned, the surface
# silently reverts to the Odoo colour (the systray badge back to 2.75:1, the chatter toggle label
# to 1.07:1) and a self-referential test stays GREEN through the whole regression.
#
# So wherever the resolution is expressible, the value is resolved THROUGH THE CORE RULE THAT READS
# IT - the browser's own path - using the cluster's single cascade resolver, which lives in
# viin_brand_web/tests/test_brand_cascade_compile.py and is IMPORTED here rather than copied
# (ODOO-AI-ETHOS #11 SSOT). A core rename then makes the resolution fail and the guard goes RED,
# which is the entire point. Two properties cannot be resolved that way and carry a cheap
# NAME-EXISTENCE guard on core's own source instead; each says so, and why, in its own docstring.
#
# ELEMENT MODELS. The resolver answers "what does the cascade compute for THIS element", so each
# surface is modelled as the classes a real element carries plus the union of its ancestors'
# classes, transcribed from the CORE template that renders it (file + line cited at each model).
# Pools are deliberately generous: an extra ancestor can only ADD a competitor rule and make a
# guard fail loudly, never hide the override that broke the surface.
import ast
import collections
import os
import re

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.misc import file_open

try:
    # The flat brand-identity teal, read from the module cluster's single Python SSOT (never
    # hardcoded-and-compared-to-itself). Imported defensively so a missing constant yields a crisp
    # per-test failure rather than breaking collection of the whole tests package.
    from odoo.addons.viin_brand_web.controllers.webmanifest import VIINDOO_THEME_COLOR
except ImportError:
    VIINDOO_THEME_COLOR = None

try:
    # The cluster's ONE cascade resolver, declared by viin_brand_web (ODOO-AI-ETHOS #11 SSOT) and
    # imported rather than re-implemented here. `_computed_value(css, chain, prop_names)` returns
    # what the CSS cascade computes for prop_names on chain[0] - `!important` first, then
    # specificity, then source order - and follows `var()` outwards through the ancestor chain
    # exactly as a browser resolves an inherited custom property. `_winning_declaration` is the same
    # machinery without the var() hop, used where the value is a plain number (an opacity).
    # Only these two private helpers are imported: pulling in a TestCase class would make this
    # module re-run viin_brand_web's suite under viin_brand_mail.
    # `_selector_scope_applies(selector, ancestors)` is the same module's ANCESTOR model, used by
    # the raw-declaration guards below: it answers "can this rule reach an element whose styling
    # ancestors carry these classes", which is what makes a last-writer read honest in a bundle
    # that contains scoped rules. Imported for the same reason as the resolver - one ancestor model
    # for the whole cluster, never a second copy that can drift from it.
    from odoo.addons.viin_brand_web.tests.test_brand_cascade_compile import (
        _computed_value,
        _selector_scope_applies,
        _winning_declaration,
    )
except ImportError:
    _computed_value = _winning_declaration = _selector_scope_applies = None

try:
    # The STOCK neutral button, modelled once by viin_brand_web (the core web pager arrow) and
    # imported rather than re-transcribed. Owner revision 2026-08-03 makes the OPEN "Log note" toggle
    # render the DEFAULT `.btn-secondary`, and the honest way to assert "the default" is to resolve a
    # real stock `.btn-secondary` in the SAME bundle and compare - which needs that module's element
    # model, not a hex copied into this file (ODOO-AI-ETHOS #11 SSOT).
    from odoo.addons.viin_brand_web.tests.test_brand_cascade_compile import (
        PAGER_ANCESTORS,
        PAGER_PREVIOUS_CLASSES,
    )
except ImportError:
    PAGER_ANCESTORS = PAGER_PREVIOUS_CLASSES = None

try:
    # `ScssStylesheetAsset` is the class every web/mail SCSS source compiles through
    # (odoo.addons.base.models.assetsbundle). The install-topology guard below re-derives a bundle
    # to splice one extra line into its SCSS source, and needs this class to pick the SCSS assets
    # out of `AssetsBundle.stylesheets` (which also holds plain CSS/JS entries) and to reach
    # Odoo's OWN `.compile` method - the real libsass entry point production calls - rather than
    # re-implementing the Sass compile. Imported defensively, same reason as the imports above: a
    # missing class fails the one guard that needs it, not collection of the whole file.
    from odoo.addons.base.models.assetsbundle import ScssStylesheetAsset
except ImportError:
    ScssStylesheetAsset = None

# CHROME-BASE AA teal - the cluster SSOT token `$o-navbar-background` declared in
# viin_brand_web/static/src/scss/brand_variables.scss. 4.74:1 against white, clearing the WCAG
# AA normal-text threshold; every chrome/interactive/glyph surface restored by the 2026-07-24
# design decision resolves to this one shade rather than a per-file literal.
CHROME_BASE_TEAL = "#007f8e"

# DEEP rung of the same ladder - `$o-viin-chrome-deep`, same SSOT file. It is the cluster's
# established "pressed / open" tone (navbar entry states, search-facet hover/active), 7.5:1 against
# white. The chatter's OPEN "Send message" toggle lands here rather than on the chrome base, because
# the base is already that button's RESTING .btn-primary fill - reusing it would make an open
# composer indistinguishable from a closed one.
CHROME_DEEP_TEAL = "#005e68"

# The RETIRED dark arm of the brand secondary. It was #B589B8, and under core's forced white label it
# measured 2.90:1 - an AA failure that shipped on both the chatter toggle and the Discuss unread badge.
# OWNER REVISION 2026-08-03 removed it outright: the purple accent is LIGHT-MODE ONLY, so nothing in
# web.assets_web_dark may resolve to this value any more. It is kept here purely as the REGRESSION
# SIGNATURE the dark arms below assert against - re-introducing a dark purple brings the 2.90:1 back.
RETIRED_DARK_PURPLE = "#b589b8"
DARK_PANEL = "#111b1e"
# The dark MUTED tier ($body-secondary-color in dark_palette.scss) that $o-brand-secondary now
# collapses onto in the dark bundle, so core's own three consumers of the token carry no purple.
# Under core's forced-white badge label it is only 2.59:1, which is WHY the Discuss badge needs its
# own dark arm rather than being allowed to follow the token.
DARK_MUTED_TIER = "#8ea5a8"

# Brand SECONDARY purple - `$o-brand-secondary`, same SSOT file. The chatter active toggle was
# ALREADY this colour in 18.0 (`$o-enterprise-primary-color` #7f4282), so purple -> purple is a
# FAITHFUL port there and must stay: only its foreground was wrong. Asserted positively below so
# a well-meant "fix" that repaints it teal is caught.
BRAND_SECONDARY_PURPLE = "#7f4282"

# The mis-ported chat-window header fill the restore removed: `mix(black, $o-brand-secondary, 15%)`.
MIS_PORTED_HEADER_PURPLE = "#6c386f"

# `$o-success`, which core's `$o-navbar-badge-bg` defaults to. White systray-counter text on it is
# only 2.75:1 - the pre-fix state this module's badge override exists to end.
CORE_SUCCESS_GREEN = "#00b365"

# The IDLE / "away" presence amber, `$o-viin-mail-status-away-color` in
# static/src/core/common/im_status.scss. A fixed, hand-chosen design constant asserted as a LITERAL
# - deliberately NOT re-derived by recomputing darken(#ffa500, 15%) inside the test, which would
# re-implement the production expression and compare it against itself. Three separate rules feed
# from that one Sass variable precisely so the picker swatch can never drift from the dot it
# selects, so "all three sites resolve to THIS value" is the behaviour under test.
AWAY_AMBER = "#b27400"
# The two values idle must NOT regress to, both asserted negatively so a well-meant "restore"
# is caught: 18.0's flat orange (1.97:1 on white - the reason the AA pass happened at all) and the
# intermediate darken(#ffa500, 10%) shade that was superseded because it failed the focused
# dropdown row.
LEGACY_AWAY_ORANGE = "#ffa500"
SUPERSEDED_AWAY_AMBER = "#cc8400"
# Core's untouched `.o-yellow { color: $yellow }` (mail/static/src/core/common/core.scss), i.e. what
# renders when this module's three rules stop matching: 1.63:1 on the white puck.
CORE_YELLOW = "#ffc107"

# The three REAL surfaces the idle glyph renders on, each pinned as a MODELLED surface whose
# provenance is re-asserted against core's own source by the guard that uses them:
#   * the ImStatus puck - core stamps `bg-white bg-opacity-100` on the ImStatus root
#     (mail/static/src/core/common/im_status.xml:5), so the dot always sits on pure white;
#   * the dropdown menu - Bootstrap paints `.dropdown-menu` with `$dropdown-bg`, which is
#     `var(--body-bg)`; the backend sets `$body-bg: $o-webclient-background-color`
#     (web/static/src/scss/bootstrap_overridden.scss) = `$o-gray-100` = #f8f9fa
#     (web/static/src/scss/secondary_variables.scss, primary_variables.scss). The brand cluster
#     does NOT re-point any of the three, so the menu is #f8f9fa;
#   * the focused/hovered dropdown row - the backend sets `$dropdown-link-hover-bg: rgba($black,
#     0.08)` (bootstrap_overridden.scss), a TRANSLUCENT wash rather than an opaque colour, so the
#     row the glyph actually sits on is that 8% black composited over the #f8f9fa menu:
#     248*0.92 = 228.16, 249*0.92 = 229.08, 250*0.92 = 230 -> #e4e5e6.
IM_STATUS_PUCK_SURFACE = "#ffffff"
DROPDOWN_MENU_SURFACE = "#f8f9fa"
DROPDOWN_ROW_FOCUS_SURFACE = "#e4e5e6"

# WCAG 2.x thresholds. Normal text (the header/composer/chatter labels and the 11px systray
# counters) needs >= 4.5:1; a meaningful non-text indicator (the im_status presence dot) needs
# >= 3:1 per WCAG 1.4.11.
WCAG_AA_NORMAL_TEXT = 4.5
WCAG_AA_NON_TEXT = 3.0

# `background` and `background-color` are resolved as ONE property family: the `background`
# shorthand resets background-color, and core uses both spellings across these surfaces.
BACKGROUND_PROPS = ("background-color", "background")

# The bundles this module's SCSS is injected into (viin_brand_mail/__manifest__.py).
BACKEND_BUNDLE = "web.assets_backend"
MAIL_PUBLIC_BUNDLE = "mail.assets_public"
LIVECHAT_EMBED_CORE_BUNDLE = "im_livechat.assets_embed_core"
# ... and the bundle that actually COMPILES the livechat embed. im_livechat.assets_embed_core is
# never built on its own: it declares no SASS helpers/variables, and the CORE mail sources inside
# it already reference $zindex-sticky / $spacers / $o-mail-ChatWindow-width, so compiling it
# standalone errors for reasons that have nothing to do with this module - a permanently-red,
# non-diagnostic oracle. im_livechat.assets_embed_external is the real compiled unit: it includes
# web._assets_helpers + web._assets_backend_helpers and then
# ('include', 'im_livechat.assets_embed_core'), so it contains this module's three shared files
# and is what the embed actually serves (im_livechat/__manifest__.py, 19.0).
LIVECHAT_EMBED_COMPILED_BUNDLE = "im_livechat.assets_embed_external"

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(_HERE)
MANIFEST = os.path.join(MODULE_DIR, "__manifest__.py")

# The de-brand sources shared by all three bundles, and the backend-only systray source.
SHARED_DEBRAND_SOURCES = (
    "viin_brand_mail/static/src/core/common/chat_window.scss",
    "viin_brand_mail/static/src/core/common/im_status.scss",
    "viin_brand_mail/static/src/core/common/composer.scss",
)
SYSTRAY_DEBRAND_SOURCE = "viin_brand_mail/static/src/core/web/messaging_menu.scss"

# The independent DARK recompile. viin_brand_web's dark_palette.scss (C-2) redefines the surface /
# text / border Sass vars to dark values here, so every mail surface reading an OVERRIDABLE Sass var
# recompiles dark-correct for free. web.assets_web_dark = ('include', 'web.assets_web') + a
# 'web/static/src/**/*.dark.scss' tail (web/__manifest__.py), so core mail's rotting_mixin.scss and
# message.scss compile inside it and this module's mail_dark.scss - anchored after its own
# message.scss - is the later same-specificity writer for the two literal-sculpted surfaces below.
DARK_BUNDLE = "web.assets_web_dark"
# The mail-owned dark residue this item (M-1) adds. Reaches the dark bundle ONLY through the explicit
# manifest entry (core's dark glob is web/mail-only), so its wiring is guarded structurally.
DARK_SURFACE_SOURCE = "viin_brand_mail/static/src/scss/mail_dark.scss"
# A translucent-alpha wash in a compiled `rgba(r, g, b, a)` value (a < 1). The dark rotting-card
# defect is exactly this: core's `rgba(255, 201, 201, .3)` literal composites to a muddy near-neutral
# over the dark card and loses the danger read, so the fix must paint a SOLID tint instead.
_RGBA_ALPHA_RE = re.compile(r"rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*([0-9.]+%?)\s*\)")
# A `var(--token[, fallback])` reference, so a compiled colour that is a custom-property lookup can be
# resolved through core's own :root emission of that token.
_VAR_REF_RE = re.compile(r"var\(\s*--([\w-]+)\s*(?:,[^)]*)?\)")

# A single "selectors { body }" rule in the compiled CSS. [^{}] keeps each match to one non-nested
# rule, so rules wrapped in @media are still captured individually.
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
# A CSS comment block. odoo/addons/base/models/assetsbundle.py's StylesheetAsset.minify() strips
# every comment and then with_header() re-prepends a "/* <source-file-url> */" banner in front of
# each per-source-file fragment. When a source file's FIRST rule follows that banner, _RULE_RE has
# no comment awareness and captures the banner glued to the selectors group - stripped here before
# selector matching so the real selector is still recognised.
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
# `background` / `background-color` declaration values (never background-image/-position: the
# optional group must be followed immediately by the colon).
_BACKGROUND_RE = re.compile(r"background(?:-color)?\s*:\s*([^;]+)", re.IGNORECASE)
# A plain `color` declaration. The lookbehind keeps it from matching `background-color`,
# `border-color`, `--btn-color` and friends.
_COLOR_RE = re.compile(r"(?<![\w-])color\s*:\s*([^;]+)", re.IGNORECASE)
# A `border-color` or per-side `border-<side>-color` declaration (the Discuss sidebar divider is
# `border-right-color`). Kept separate from _COLOR_RE, whose lookbehind deliberately excludes it.
_BORDER_COLOR_RE = re.compile(
    r"border(?:-(?:top|right|bottom|left))?-color\s*:\s*([^;]+)", re.IGNORECASE
)
_HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}")


def _custom_property_re(name):
    """Return a regex matching the value of the CSS custom property ``--<name>``.

    The ``\\s*:`` guard means ``--btn-color`` never accidentally matches
    ``--btn-color-rgb``, and ``--o-mail-ActionList-Button-opacity`` never matches its
    ``--o-mail-ActionList-Button-opacity--hover`` sibling."""
    return re.compile(r"--%s\s*:\s*([^;}]+)" % re.escape(name))


def _normalize_value(value):
    """Lower-case a declaration value, drop `!important` and collapse whitespace.

    Only VALUES are normalised - selectors keep their original case, because CSS class selectors
    are case-sensitive and a mis-cased selector must fail the match, not be silently repaired."""
    return re.sub(r"\s+", " ", value.replace("!important", "")).strip().lower()


def _iter_rules(css):
    """Yield ``(selector_tokens, body)`` for every compiled rule, in document order."""
    for selectors, body in _RULE_RE.findall(css):
        tokens = [
            re.sub(r"\s+", " ", token).strip()
            for token in _COMMENT_RE.sub("", selectors).split(",")
        ]
        yield [token for token in tokens if token], body


# The ancestor pool a caller passes when the element's real chain has NOT been transcribed. It
# says "no ancestor context is claimed", so every rule whose subject matches is returned - the
# pre-ancestor behaviour, kept only where a guard's predicate pins the whole selector (an exact
# `selector == "..."`, or a `^`-anchored regex) and the scope check is a no-op by construction, or
# where the chain has simply not been modelled yet. It is deliberately a named argument every call
# site must pass rather than a default: a scoped rule from ANY module can start colliding with ANY
# subject at any time, and the fix is then a one-line swap at a site the reader can already see,
# not the discovery that a silent default existed.
ANY_ANCESTORS = None


def _rules_in_scope(css, ancestors):
    """Yield ``(selector_tokens, body)`` for the compiled rules that can REACH the element.

    Each rule's tokens are reduced to the selectors whose ancestor context ``ancestors`` satisfies,
    and a rule left with no reachable selector is dropped entirely - so a caller reading the LAST
    declaration reads the last one a browser would actually apply. ``ancestors`` is a set of the
    class names on the element's real ancestor chain (see the ancestor pools below), or
    ``ANY_ANCESTORS`` to claim no context at all."""
    for tokens, body in _iter_rules(css):
        if ancestors is ANY_ANCESTORS:
            yield tokens, body
            continue
        in_scope = [token for token in tokens if _selector_scope_applies(token, ancestors)]
        if in_scope:
            yield in_scope, body


def _bodies_matching(css, selector_matches, ancestors):
    """Return, in document order, the bodies of IN-SCOPE rules with a selector satisfying the
    predicate. ``ancestors`` is the element's ancestor pool, or ``ANY_ANCESTORS``."""
    return [
        body for tokens, body in _rules_in_scope(css, ancestors)
        if any(map(selector_matches, tokens))
    ]


def _selector_subject(selector):
    """The compound a rule actually STYLES: the rightmost compound of ``selector`` after stripping
    any functional-pseudo argument (``:has()``/``:is()``/``:where()``/``:not()``).

    A rule styles ``.o-mail-Chatter-sendMessage`` only when that class is in this SUBJECT - not when
    it merely appears inside a ``:has()`` condition on an ancestor. web_responsive ships
    ``.o-mail-Chatter-top:has(.o-mail-Chatter-sendMessage.active) .o-mail-Composer { background-color:
    lighten($o-brand-primary, 35%) }`` (~#82f3ff) which washes the COMPOSER while composing - a
    different element - and must NOT be read as the send button's own fill. Matching on the subject
    (not a raw substring) keeps this guard protecting the button's de-brand, not a bundle snapshot."""
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
        for hex_literal in _HEX_RE.findall(value)
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
    """Squared Euclidean distance between two sRGB triplets.

    Used only to state "this surface is CLOSER to $danger than that one" - a relational claim about
    a tint that stays true through any re-tune of the wash percentage, unlike a pinned hex. Squared
    (no sqrt) because only the ordering is ever compared."""
    return sum((first - second) ** 2 for first, second in zip(first_rgb, second_rgb))


def _root_custom_property(css, name):
    """Last value declared for ``--<name>`` on a ``:root`` rule, or None.

    Bootstrap emits the theme tokens (--danger, --body-color, ...) on :root from their Sass
    variables, and the cluster's class-based cascade resolver deliberately does not model :root (it
    requires a positive class). Reading them here anchors an assertion on CORE'S OWN emission rather
    than on a hex this module chose. Last declaration wins, exactly as the cascade resolves it."""
    values = []
    pattern = _custom_property_re(name)
    for tokens, body in _iter_rules(css):
        if not any(token == ":root" or token.startswith(":root") for token in tokens):
            continue
        for match in pattern.finditer(body):
            values.append(_normalize_value(match.group(1)))
    return values[-1] if values else None


# Core dims the composer placeholder with its own `::placeholder { opacity }` rules
# (mail/static/src/core/common/composer.scss). Read, never assumed: the composited placeholder is
# what a user actually sees, and core owns the dimming.
_OPACITY_RE = re.compile(r"(?<![\w-])opacity\s*:\s*([^;]+)", re.IGNORECASE)
_COMPOSER_PLACEHOLDER_SELECTOR = "o-mail-Composer-input::placeholder"


def _composite(foreground_rgb, background_rgb, alpha):
    """Return the opaque colour a foreground at ``alpha`` opacity paints over a background.

    Source-over compositing, the model a browser applies to an element carrying `opacity`: this is
    what makes the opacity token part of the CONTRAST rule rather than a cosmetic detail."""
    return tuple(
        round(foreground * alpha + background * (1 - alpha))
        for foreground, background in zip(foreground_rgb, background_rgb)
    )


def _injected_sources(assets, bundle_name):
    """Return every asset SOURCE path a manifest bundle injects, flattening both the bare-string
    and the ``(directive, anchor, source)`` / ``(directive, source)`` operation forms."""
    sources = set()
    for operation in assets.get(bundle_name, []):
        if isinstance(operation, str):
            sources.add(operation)
        elif isinstance(operation, (tuple, list)) and operation:
            sources.add(operation[-1])
    return sources


WHITE_RGB = (255, 255, 255)


# ==================================================================================================
# Element models - transcribed from the CORE templates that render each surface
# ==================================================================================================
# `classes` is what the element itself carries; `ancestors` is the UNION of the classes on its real
# ancestor chain, which is how the resolver decides whether a scoped core rule applies. Every model
# cites the core file and line it was read off, so a template change is a locatable re-grounding
# job rather than a silent false pass.

# chatter.xml:12-25 - the ACTIVE toggle is `btn-primary active` (sendMessage when composerType is
# 'message', logNote when it is 'note'); the resting one is `btn-secondary` and is not under test.
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
# The two toggles are each other's immediate siblings (chatter.xml lines 12 and 20) and neither is a
# `.btn-check`. Modelling the sibling is load-bearing: Bootstrap's pressed-state rule group ships
# `.btn-check:checked + .btn` (_buttons.scss:81-86), whose SUBJECT carries no state pseudo-class at
# all - without a real previous sibling to rule it out that (0,3,0) selector outranks `.btn.active`
# and would hand this query the CHECKED value instead of the pressed one.
CHATTER_TOGGLE_PREV_SIBLING = frozenset({
    "o-mail-Chatter-sendMessage", "o-mail-Chatter-logNote", "btn", "text-nowrap", "me-1",
})

# `.o-mail-Composer` renders in three places and the guards below measure the SAME token on it in
# all of them, so the pool is the union of the three real chains: the chatter (chatter.xml:5-7 plus
# chatter.xml:66, which puts the Composer inside `.o-mail-Chatter-top` - the ancestor core's own
# `:has()` danger-cue selector keys on), Discuss (discuss.xml:5 -> discuss_content.xml:6,65,67,70)
# and the chat window (chat_window.xml:6 -> :73). Being a union makes it GENEROUS on purpose, which
# is the safe direction: an ancestor the element does not really have can only ADD a competitor
# rule and make a guard fail loudly, never hide the override that broke the surface.
COMPOSER_ANCESTORS = CHATTER_ANCESTORS | frozenset({
    "o_action_manager",
    "o-mail-Discuss", "o-mail-DiscussContent", "o-mail-DiscussContent-main",
    "o-mail-DiscussContent-core", "o-mail-ChatWindow",
    "h-100", "w-100", "flex-grow-1", "flex-shrink-0", "o-min-width-0", "fixed-bottom", "shadow",
    "bg-100", "overflow-auto", "overflow-hidden", "o-scrollbar-thin",
})

# message.xml:7,22,63-65,89 - `.o-mail-Message-bubble` is the absolutely-positioned wash behind a
# message's text, so its chain is Message > Message-core sibling wrapper > Message-contentContainer
# > Message-content > Message-textContent > the `.o-discuss-text-body` box that carries the bubble.
# The thread above it is thread.xml:5, reached either from Discuss (discuss.xml:5 ->
# discuss_content.xml:6,65,67) or from a form view's chatter (chatter.xml:5,69). Union of both, for
# the same reason COMPOSER_ANCESTORS is one.
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

# messaging_menu_patch.xml:9 and activity_menu.xml:8 - `<span class="o-mail-*-counter badge
# rounded-pill">`. The `badge` class is what core's navbar consumer keys on, so it is load-bearing
# in the model, not decoration. Ancestors: navbar.xml renders the systray inside
# .o_main_navbar > .o_menu_systray.
SYSTRAY_ANCESTORS = frozenset({
    "o_web_client", "o_main_navbar", "o_menu_systray", "dropdown", "dropdown-toggle",
    "o-mail-MessagingMenu", "o-mail-ActivityMenu",
})
SYSTRAY_COUNTER_CLASSES = {
    ".o-mail-MessagingMenu-counter": frozenset({
        "o-mail-MessagingMenu-counter", "badge", "rounded-pill",
    }),
    ".o-mail-ActivityMenu-counter": frozenset({
        "o-mail-ActivityMenu-counter", "badge", "rounded-pill",
    }),
}

# chat_window.xml:6-17 - .o-mail-ChatWindow > .o-mail-ChatWindow-header > a bg-inherit wrapper >
# the Dropdown toggle `<button class="o-mail-ChatWindow-moreActions btn ...">`.
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

# discuss_sidebar_categories.xml:137 - the unread counter of a Discuss sidebar channel. Chosen over
# the other .o-discuss-badge render sites because core DELIBERATELY overrides two of them at higher
# specificity and those overrides must keep winning: a NotificationItem badge that is not
# `.o-important` is pinned to $gray-500 (notification_item.scss:29-30, (0,3,0)) and the messaging
# menu's tab-unread dot to transparent (messaging_menu.scss:31-32, (0,2,0)). `o-muted` is likewise
# absent from the model on purpose - core keeps a muted counter $gray-400 (core.scss:41-42).
DISCUSS_SIDEBAR_ANCESTORS = frozenset({
    "o_web_client", "o-mail-Discuss", "o-mail-DiscussSidebar", "o-mail-DiscussSidebar-item",
    "o-mail-DiscussSidebarChannel",
})
DISCUSS_UNREAD_BADGE_CLASSES = frozenset({
    "o-mail-DiscussSidebar-badge", "o-discuss-badge", "badge", "rounded-pill", "shadow-sm",
    "fw-bold", "mx-1",
})

# message_seen_indicator.xml:4 - `<span class="o-mail-MessageSeenIndicator position-relative">` with
# `o-hasEveryoneSeen opacity-75` added exactly when every member has seen the message. BOTH of those
# conditional classes are in the model: `o-hasEveryoneSeen` is what core's colour rule keys on, and
# `opacity-75` is what dims the glyph - the reason this surface is asserted on its COMPOSITED value.
# message_patch.xml:5-11 puts the component inside `.o-mail-Message-seenContainer.position-absolute`,
# itself inside `.o-mail-Message` in the `.o-mail-Thread` list.
MESSAGE_SEEN_ANCESTORS = frozenset({
    "o_web_client", "o-mail-Thread", "o-mail-Message", "o-mail-Message-seenContainer",
    "position-absolute",
})
MESSAGE_SEEN_EVERYONE_CLASSES = frozenset({
    "o-mail-MessageSeenIndicator", "position-relative", "o-hasEveryoneSeen", "opacity-75",
})

# im_status.xml:5-19 - the ImStatus root carries `bg-white bg-opacity-100` (this is WHY the puck is
# white) and the idle glyph is `<i class="fa fa-circle o-yellow">` two levels down.
IM_STATUS_ANCESTORS = frozenset({
    "o_web_client", "o-mail-ImStatus", "d-flex", "justify-content-center", "flex-shrink-0",
    "align-items-center", "bg-white", "bg-opacity-100", "rounded-circle", "flex-column", "smaller",
})
# thread_icon.xml:14 - ThreadIcon renders the idle glyph through a NESTED <ImStatus>, so the glyph
# is inside BOTH components and BOTH `.o-mail-*  .o-yellow` rules match it at equal specificity.
# That is exactly the desync this model exists to measure.
THREAD_ICON_ANCESTORS = IM_STATUS_ANCESTORS | {"o-mail-ThreadIcon"}
# im_status_dropdown.xml:4+9 - `menuClass="'o-mail-ImStatusDropdown'"` lands the literal class on the
# menu element (web/static/src/core/dropdown/dropdown.js), and the Away swatch is a plain
# `<i class="fa fa-circle o-yellow me-1">` inside a DropdownItem, which core renders as
# `o-dropdown-item dropdown-item o-navigable` (web/static/src/core/dropdown/dropdown_item.xml:7).
# `o-mail-ImStatus` is deliberately ABSENT: the swatch is NOT inside an ImStatus (only the dropdown
# TOGGLE is), so site 1's rule must not be credited for it.
IM_STATUS_DROPDOWN_ANCESTORS = frozenset({
    "o_web_client", "o-mail-ImStatusDropdown", "o-dropdown--menu", "dropdown-menu", "show",
    "o-dropdown-item", "dropdown-item", "o-navigable",
})
IDLE_GLYPH_CLASSES = frozenset({"fa", "fa-circle", "o-yellow"})
IDLE_SWATCH_CLASSES = IDLE_GLYPH_CLASSES | {"me-1"}


# ==================================================================================================
# The spreadsheet LIGHT ISLAND - where a dark-app Chatter renders on light-forced chrome
# ==================================================================================================
# Odoo 19 keeps the spreadsheet editor a LIGHT ISLAND inside a dark app on purpose: the core file
# below opens `.o-spreadsheet { color-scheme: light; ... }` and repaints the editor's chrome with
# light literals, among them `.o-spreadsheet .btn { color: <light-island label> }`. That selector is
# (0,2,0) with no `!important`, so it outranks Bootstrap's own `.btn { color: var(--btn-color) }`
# (0,1,0) and repaints the label of EVERY button rendered inside the editor - including the mail
# Chatter this cluster embeds in the comments side panel.
#
# It repaints the label ONLY. Backgrounds inside the island keep resolving through the app-wide dark
# ladder (viin_brand_web/static/src/scss/dark_buttons.scss maps `.btn-secondary` onto
# $o-viin-dark-control-bg, brand_variables.scss keys `.btn-primary` off the chrome teal), so the two
# halves of every button come from two different schemes and collide. Measured live on a dark 19.0
# webclient at 1440px, alpha-composited. The two panel-surface rows were taken while the comments
# panel still carried a `bg-view` utility, which `viin_spreadsheet` 3c6dcc617 has since removed -
# they are recorded as the observation that motivated these guards, NOT as the current surface:
#     Log note      light-island label on the dark control tier  1.19:1
#     Activity      light-island label on the dark control tier  1.19:1
#     Send message  light-island label on the chrome teal        2.17:1
#     side-panel controls (cell address, Resolve), then on `bg-view`   1.70:1
#     message body  dark $body-color, then on `bg-view`               15.72:1
# The BUSINESS RULE the two guards below protect is the island contract itself: inside
# `.o-spreadsheet` the embedded Chatter must render as a LIGHT surface carrying DARK text and clear
# WCAG AA - it must not serve one half of each pair from the app-wide dark palette. Both guards
# measure the ratio of the COMPILED dark-bundle colours against the FIXED AA threshold, so a later
# re-tune that still clears AA is not a false alarm, and neither can be satisfied by a
# different-but-equally-unreadable shade.
#
# WHY NO HOOT/JS TEST AND NO MODULE DEPENDENCY. Hoot loads only the LIGHT bundle, so the collision
# is invisible to it. And nothing here needs `spreadsheet` or `viin_spreadsheet` INSTALLED: the
# assertions read OUR compiled `web.assets_web_dark`, where the ancestor chain is only a list of
# class strings handed to the cluster's cascade resolver, and the one core value that is read comes
# off the addons path with `file_open` (which resolves a source file, not an installed module) - the
# same name-existence discipline `_assert_core_source_contains` already uses in this file.
CORE_SPREADSHEET_DARK_SCSS = "spreadsheet/static/src/o_spreadsheet/o_spreadsheet_extended.dark.scss"

# The `.btn` block nested inside that file's `.o-spreadsheet { ... }` wrapper. Anchored at the start
# of a line so the `.badge` / `.o_input` blocks around it can never be read instead, and capturing
# the VALUE rather than asserting one: the light-island label is core's design decision, and if core
# re-tunes it the contrast arithmetic below changes with it instead of going stale.
_ISLAND_BUTTON_COLOUR_RE = re.compile(
    r"^\s*\.btn\s*\{[^{}]*?(?<![\w-])color\s*:\s*([^;}]+)", re.MULTILINE | re.DOTALL
)

# A compiled `rgb()`/`rgba()` value with its alpha slot captured whole. Odoo's own
# `o-print-color` mixin (web/static/src/scss/functions.scss:48-51) is what emits the `bg-*`
# utilities, and it writes `RGBA(<r>, <g>, <b>, var(--bg-opacity, 1))` - a form the plain colour
# parser above cannot read. Every `bg-*` utility any modelled layer may carry takes this form, so
# the surface walk needs it to tell an opaque layer from a translucent one.
_RGB_FUNCTIONAL_RE = re.compile(
    r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(.+?)\s*)?\)", re.IGNORECASE
)

# Values that paint nothing at all, so the element shows whatever its ancestors paint.
_NON_PAINTING_VALUES = frozenset({
    "transparent", "inherit", "initial", "unset", "revert", "none", "currentcolor",
})


def _alpha_slot(text):
    """Parse the alpha slot of a compiled ``rgb()``/``rgba()`` value into a float, or None.

    Handles the bare number Sass emits and the ``var(--<token>, <fallback>)`` form Odoo's
    ``o-print-color`` emits, which resolves to its fallback for any element that carries no
    ``.bg-opacity-*`` utility. A slot that cannot be resolved returns None and is treated by
    :func:`_opaque_rgb` as NOT provably opaque - the conservative direction, since it only makes the
    surface walk look further out rather than crediting a translucent layer as the backdrop."""
    text = text.strip().lower()
    var_fallback = re.fullmatch(r"var\(\s*--[\w-]+\s*,\s*([^()]+)\)", text)
    if var_fallback:
        text = var_fallback.group(1).strip()
    return _to_alpha(text)


def _opaque_rgb(value):
    """Return ``(r, g, b)`` when ``value`` paints a FULLY OPAQUE colour, else None.

    Distinct from :func:`_to_rgb`, which reads the channels of an ``rgba()`` and ignores its alpha:
    the surface walk needs to know whether a layer actually HIDES what is behind it, so anything
    translucent, unresolvable or non-painting has to read as "keep looking outwards"."""
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


# --- Element models, transcribed from the templates that render the embedded comments Chatter -----
# `.o-spreadsheet` and `.o-sidePanel` are the o_spreadsheet engine's own chrome; the three
# `o_viin_spreadsheet_all_comments*` layers are viin_spreadsheet's comments panel
# (static/src/bundle/comments/all_comments_panel.xml), whose item wraps the thread wrapper which
# renders `<Chatter/>`. The Chatter's own three layers are core's
# mail/static/src/chatter/web/chatter.xml:5-8. None of those modules is imported or depended on -
# the resolver only ever sees these class strings.
WEBCLIENT_ANCESTORS = frozenset({"o_web_client", "o_action_manager"})
SPREADSHEET_ISLAND_ROOT = frozenset({"o-spreadsheet"}) | WEBCLIENT_ANCESTORS
SPREADSHEET_SIDE_PANEL = frozenset({"o-sidePanel"})
# The panel root carries NO background utility. `viin_spreadsheet` 3c6dcc617 removed the `bg-view`
# a prior change had added here: measured on a live dark instance it left the composer contrast
# unchanged while regressing six other side-panel elements, because the o-spreadsheet engine
# hardcodes a light-mode text colour on its own side panel that Odoo's dark recompile cannot reach.
# So this layer paints nothing and the engine's `.o-sidePanel` shows through - which is also why
# this module now declares no rule naming a `viin_spreadsheet` class at all.
SPREADSHEET_COMMENTS_PANEL = frozenset({"o_viin_spreadsheet_all_comments", "p-3"})
SPREADSHEET_COMMENTS_ITEM = frozenset({
    "o_viin_spreadsheet_all_comments_item", "border-bottom", "pb-2", "mb-2",
})
SPREADSHEET_COMMENTS_THREAD = frozenset({"o_viin_spreadsheet_all_comments_thread", "mt-2"})
CHATTER_ROOT_CLASSES = frozenset({
    "o-mail-Chatter", "w-100", "h-100", "flex-grow-1", "d-flex", "flex-column", "bg-inherit",
})
CHATTER_TOP_CLASSES = frozenset({"o-mail-Chatter-top", "d-print-none", "position-sticky", "top-0"})
CHATTER_TOPBAR_CLASSES = frozenset({
    "o-mail-Chatter-topbar", "d-flex", "flex-shrink-0", "flex-grow-0", "overflow-x-auto",
})

# Outwards from the Chatter root: the layers every embedded-Chatter element shares.
ISLAND_PANEL_LAYERS = (
    SPREADSHEET_COMMENTS_THREAD, SPREADSHEET_COMMENTS_ITEM, SPREADSHEET_COMMENTS_PANEL,
    SPREADSHEET_SIDE_PANEL, SPREADSHEET_ISLAND_ROOT,
)
ISLAND_TOPBAR_LAYERS = (
    CHATTER_TOPBAR_CLASSES, CHATTER_TOP_CLASSES, CHATTER_ROOT_CLASSES,
) + ISLAND_PANEL_LAYERS

# chatter.xml:13-30. The RESTING state of a CLOSED composer - the state the collision was measured
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

# --- The message subtree, and the two layers that decide where its text is read -------------------
# Transcribed from mail/static/src/core/common/message.xml. Outwards from the rendered glyphs:
# message.xml:99 `.o-mail-Message-body` > :82 `.o-discuss-text-body` > :66 `.o-mail-Message-textContent`
# > :65 `.o-mail-Message-content` > :64 `.o-mail-Message-contentContainer` > :21 `.o-mail-Message-core`
# > :7 `.o-mail-Message` > thread.xml:5 `.o-mail-Thread` > chatter.xml:69 `.o-mail-Chatter-content`.
#
# TWO OF THOSE LAYERS CARRY THE WHOLE MEASUREMENT, and a model that stops at the Chatter root sees
# neither of them:
#
# 1. WHERE THE COLOUR COMES FROM. `.o-discuss-text-body` (message.xml:82) is the wrapper that
#    CONTAINS `.o-mail-Message-body`, and it is the element the message's colour is declared on.
#    core.scss:99-101 and core.dark.scss:13-15 both style it as a BARE class - specificity (0,1,0) -
#    with `!important`, the dark file winning on source order. An `!important` declaration outranks
#    every normal one at ANY specificity, so re-pointing `.o-mail-Chatter { color }` inside the
#    island (0,2,0, normal) does not reach this text at all: `.o-mail-Message-body` declares no
#    colour of its own (message.scss:45-58) and inherits from this wrapper, never from the Chatter.
#    Resolving `color` on the Chatter root therefore answers a question about a DIFFERENT element
#    and reports a value the message body never renders in.
#
# 2. WHAT IT IS READ ON. `.o-mail-Message-bubble` (message.xml:89) is `position-absolute top-0
#    start-0 w-100 h-100` INSIDE that same wrapper: a preceding SIBLING of `.o-mail-Message-body`,
#    painted behind it and filling it edge to edge - never an ANCESTOR of it. Compositing only
#    ancestor backgrounds walks straight past the bubble and reports the panel behind it, so a
#    bubbled message gets measured against a surface no reader ever sees through the bubble. It is
#    resolved as its OWN element below and handed to the arithmetic as the surface.
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
# message.xml:99-108, the RESTING state the collision is measured in: a posted, non-note,
# non-squashed, non-editing message with text to show.
MESSAGE_BODY_CLASSES = frozenset({
    "o-mail-Message-body", "position-relative", "text-break", "mb-0", "py-2", "align-self-start",
    "o-rounded-end-bubble", "o-rounded-bottom-bubble",
})
# message.xml:89-96, same resting state. The variant class is what each bubble map keys on.
_ISLAND_BUBBLE_BASE = frozenset({
    "o-mail-Message-bubble", "position-absolute", "top-0", "start-0", "w-100", "h-100", "border",
    "o-rounded-bottom-bubble", "o-rounded-end-bubble",
})
ISLAND_BUBBLE_CLASSES = {
    variant: _ISLAND_BUBBLE_BASE | {variant} for variant in ("o-blue", "o-green", "o-orange")
}

# The message subtree as far OUT as the thread list, which is the deepest layer every container
# below shares: message.xml:66 -> :65 -> :64 -> :21 -> :7, then thread.xml:5. Everything past it is
# what tells a form-view chatter from Discuss from a chat window, so the shared part is declared
# ONCE here and each container appends its own tail (ODOO-AI-ETHOS #11 SSOT). Splitting it is not
# cosmetic: the three containers paint three DIFFERENT panels under the same glyphs, and a stack
# re-transcribed per container is exactly how two of them end up silently modelling the same one.
#
# thread.xml:7 - the `d-flex flex-column position-relative flex-grow-1 bg-inherit` wrapper between
# the thread list and the first message - is deliberately NOT a layer here, the reading every guard
# in this file already used. It declares no colour and its `bg-inherit` paints nothing, so it is
# inert for both walks; adding it would change no resolution and would fork the shared stack from
# the one the light guards are green on.
MESSAGE_SUBTREE_TO_THREAD_LAYERS = (
    MESSAGE_TEXT_CONTENT_CLASSES, MESSAGE_CONTENT_CLASSES, MESSAGE_CONTENT_CONTAINER_CLASSES,
    MESSAGE_CORE_CLASSES, MESSAGE_ROOT_CLASSES, THREAD_CLASSES,
)
# chatter.xml:69 and :5 - the two Chatter layers between the thread and whatever the Chatter is
# dropped into. Shared by the spreadsheet island and the form view, which differ only OUTSIDE them.
CHATTER_THREAD_HOST_LAYERS = (CHATTER_CONTENT_CLASSES, CHATTER_ROOT_CLASSES)

# From the Chatter root down to `.o-discuss-text-body`, then out through the panel. Both the body
# and the bubble hang off the text-body wrapper, so both are modelled with these same ancestors -
# which is exactly what makes them siblings rather than one an ancestor of the other.
ISLAND_MESSAGE_LAYERS = (
    MESSAGE_SUBTREE_TO_THREAD_LAYERS + CHATTER_THREAD_HOST_LAYERS + ISLAND_PANEL_LAYERS
)
ISLAND_TEXT_BODY_LAYERS = (MESSAGE_TEXT_BODY_CLASSES,) + ISLAND_MESSAGE_LAYERS

# --- The MUTED secondary tier, and the two places it is read on DIFFERENT surfaces ----------------
# One tier, two render sites, and they do not share a surface - which is why it needs its own model
# rather than reusing the body chain above.
#
# 1. A TIMESTAMP IS NEVER READ ON A BUBBLE. `.o-mail-Message-date` (message.xml:44) sits inside
#    `.o-mail-Message-header` (:38), a SIBLING of `.o-mail-Message-contentContainer` (:64) - both are
#    children of the `w-100 o-min-width-0` wrapper at :36. The bubble is painted inside
#    `.o-discuss-text-body` (:82-89), several layers further in, so nothing is ever painted between a
#    timestamp and the panel. Its squashed twin (:31) lives in `.o-mail-Message-sidebar`, also
#    outside that wrapper. For both, the ancestor walk IS the correct surface model.
# 2. THE SAME TIER IS READ ON THE BUBBLE TOO. Core renders four `.text-muted` markers INSIDE
#    `.o-mail-Message-body`: the empty-message placeholder (:110), the `Subject:` line (:113) and the
#    two translation notes (:117, :120). Those are inside `.o-discuss-text-body`, so on a bubbled
#    message the bubble is the surface under them exactly as it is under the body text. They are
#    modelled by the `Subject:` line - the one of the four carrying no `opacity` of its own, so the
#    tier is measured undimmed; all four take their colour from the same rule on the same ancestors.
MESSAGE_DATE_CLASSES = frozenset({"o-mail-Message-date", "o-xsmaller"})
MESSAGE_HEADER_CLASSES = frozenset({
    "o-mail-Message-header", "d-flex", "flex-wrap", "align-items-baseline", "lh-1", "mb-1",
})
_MESSAGE_CONTENT_WRAPPER = frozenset({"w-100", "o-min-width-0"})
ISLAND_MESSAGE_HEADER_LAYERS = (
    MESSAGE_HEADER_CLASSES, _MESSAGE_CONTENT_WRAPPER, MESSAGE_CORE_CLASSES, MESSAGE_ROOT_CLASSES,
    THREAD_CLASSES, CHATTER_CONTENT_CLASSES, CHATTER_ROOT_CLASSES,
) + ISLAND_PANEL_LAYERS
MESSAGE_BODY_MUTED_CLASSES = frozenset({"d-block", "text-muted", "smaller"})
ISLAND_MESSAGE_BODY_MUTED_LAYERS = (MESSAGE_BODY_CLASSES,) + ISLAND_TEXT_BODY_LAYERS

# composer.xml:77 plus the unconditional half of the `inputClasses` dict at :69-74 (the three
# conditional entries are mobile / action-count / restored-draft states, none of them the resting
# field). The textarea the user types into carries `o-discuss-text-body` ITSELF, so it takes the
# same bare-class `!important` colour as the message body - and it paints its own fill through
# `.o-mail-Composer-bg` (composer.scss:103-105, `var(--mail-Composer-bg, ...)`), which makes it a
# second, independent place the same pairing can go incoherent.
ISLAND_COMPOSER_INPUT_CLASSES = frozenset({
    "o-mail-Composer-input", "o-mail-Composer-bg", "shadow-none", "overflow-auto",
    "o-scrollbar-thin", "o-discuss-text-body", "user-select-auto", "o-mail-Composer-inputStyle",
    "form-control", "border-0", "o-rounded-bubble",
})
# composer.xml:68 wrapper, :12 the Composer root, then chatter.xml:66 puts the Composer inside
# `.o-mail-Chatter-top`.
_COMPOSER_INPUT_WRAPPER = frozenset({"position-relative", "flex-grow-1"})
_COMPOSER_ROOT_CLASSES = frozenset({
    "o-mail-Composer", "d-grid", "flex-shrink-0", "pt-0", "position-relative",
})
ISLAND_COMPOSER_INPUT_LAYERS = (
    _COMPOSER_INPUT_WRAPPER, _COMPOSER_ROOT_CLASSES, CHATTER_TOP_CLASSES, CHATTER_ROOT_CLASSES,
) + ISLAND_PANEL_LAYERS


def _element_chain(element_classes, ancestor_layers, prev_sibling=frozenset(), tag=None):
    """Return the cascade-resolver chain for one modelled element and its styling ancestors.

    Innermost first - the element, then each styling ancestor - with every entry's ``ancestors``
    being the union of the classes OUTSIDE it, which is what
    ``viin_brand_web``'s resolver uses to decide whether a scoped rule applies. Only the element
    itself carries a previous sibling; an ancestor modelled with one would let a sibling-gated rule
    match a position the transcription never claimed.

    Scheme- and container-agnostic: the same builder serves the spreadsheet island's dark chains,
    the form-view chatter's light ones, and the sibling chains :func:`_painted_sibling_chain`
    derives from them.

    ``parent`` IS POPULATED FOR EVERY ENTRY, from the layer immediately outside it. Consecutive
    layers in the message-subtree transcriptions are a true parent relation - each cited template
    line is the direct parent of the previous one - so the resolver can decide a CHILD combinator
    (`>`) exactly instead of reading it as a plain descendant. A transcription that ever skips an
    intermediate element makes a `>` rule stop matching and the guard fail loudly, which is the
    safe direction for a wrong model.

    ONE LAYER KIND IS DELIBERATELY NOT A SINGLE ELEMENT: the outer chrome pools
    (``WEBCLIENT_ANCESTORS``, ``SPREADSHEET_ISLAND_ROOT``) fold several real DOM levels into one
    set, because nothing asserted here depends on telling them apart. For an element whose parent
    is such a pool the parent set is a SUPERSET of the true parent, so the subset check stays
    permissive exactly where it cannot decide - it can fail to reject a rule, never wrongly reject
    one. That is the pre-existing reading, so those layers are no less correct than before; the
    tightening is real only where the parent is a single transcribed element.

    ``tag`` is the element's own HTML tag, and only the ELEMENT carries one - an ancestor modelled
    with a tag would let a type-gated rule match a position the transcription never claimed, the
    same reasoning as ``prev_sibling``. Declare it whenever core styles the subject through its
    tag; leaving it None keeps the resolver's conservative "type selectors do not match" reading."""
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


# --- WHICH PAINTED SIBLING SITS BEHIND THIS ELEMENT ==============================================
# THE RULE THIS SECTION IS THE SSOT FOR. The surface an element is READ ON is not always one of its
# ancestors. An absolutely-positioned, full-bleed element paints behind every LATER sibling in its
# own containing block, so for those siblings IT is the surface and no ancestor of theirs is. A
# resolver that composites only ancestor backgrounds cannot see such a layer at all: it walks
# straight past it and reports whatever the containing block paints, which is a colour no reader
# ever sees through the overlay.
#
# WHY THIS IS ITS OWN MODEL AND NOT A CONDITION INSIDE ONE GUARD. The rule is wrong in TWO
# directions and both directions were shipped as live defects while measuring this cluster:
#   * ANCESTOR-ONLY (the miss). The 1.11:1 message-body defect stayed green precisely because the
#     instrument composited ancestors only. `.o-mail-Message-bubble` (message.xml:89) is
#     `position-absolute top-0 start-0 w-100 h-100` INSIDE `.o-discuss-text-body` (:82) and a
#     PRECEDING SIBLING of `.o-mail-Message-body` (:99) - never an ancestor of it. Measured against
#     the panel behind the bubble every bubbled message looked fine; measured against the bubble it
#     was unreadable.
#   * UNCONDITIONAL (the over-apply). Handing the bubble to every element in the message subtree is
#     equally wrong and equally invisible: `.o-mail-Message-date` (:44) lives in
#     `.o-mail-Message-header` (:38), a SIBLING of `.o-mail-Message-contentContainer` (:64). The
#     bubble is several layers further in, so nothing is ever painted between a timestamp and the
#     panel, and crediting it with a bubble reports a surface the timestamp never renders on.
# One guard carrying an `if` for its own subject cannot be wrong in the second direction, so it
# never has to get the second direction right. Modelling the overlay as a DECLARED INPUT - and
# deciding applicability from DOM containment rather than from which test is asking - is what makes
# both directions answerable, reusable, and testable. `test_message_bubble_is_composited_only_for_
# elements_inside_the_text_body_wrapper` pins both.
#
# THE CONTAINMENT TEST, AND WHY IT IS STRICTLY AN ANCESTOR. The overlay is behind an element iff the
# overlay's own PARENT is a STRICT ANCESTOR of that element - siblings share a parent, so an element
# that carries the container class ITSELF is the container, not a sibling of anything inside it.
# That distinction is load-bearing rather than pedantic: the composer textarea (composer.xml:77)
# carries `o-discuss-text-body` on its own element, and a containment test that accepted the subject
# would hand it a message bubble that is not in its subtree at all.
#
# The overlay's own resolver chain is DERIVED from the subject's chain rather than transcribed a
# second time, so the two can never drift apart: it is the overlay's classes on the sub-chain that
# starts at the container.
PaintedSibling = collections.namedtuple("PaintedSibling", "label classes container_class")

# The three bubble variants core paints, declared once for every guard that measures a glyph which
# may or may not sit on one. `container_class` is the wrapper the bubble is a child of.
MESSAGE_BUBBLE_SIBLING_BY_VARIANT = {
    variant: PaintedSibling(
        label="%s message bubble" % variant,
        classes=ISLAND_BUBBLE_CLASSES[variant],
        container_class="o-discuss-text-body",
    )
    for variant in ISLAND_BUBBLE_CLASSES
}
MESSAGE_BUBBLE_SIBLINGS = tuple(
    MESSAGE_BUBBLE_SIBLING_BY_VARIANT[variant] for variant in sorted(ISLAND_BUBBLE_CLASSES)
)


def _painted_sibling_chain(chain, sibling):
    """Return ``sibling``'s own resolver chain when it really paints behind ``chain[0]``, else None.

    ``None`` is the answer for an element the overlay is not behind, and it is as load-bearing as
    the chain: it is what keeps the timestamp on the panel. The walk starts at index 1 because a
    sibling shares its subject's PARENT - an element carrying the container class itself contains
    the overlay rather than sitting next to it (see the section header)."""
    for depth in range(1, len(chain)):
        if sibling.container_class in chain[depth]["classes"]:
            return _element_chain(sibling.classes, [entry["classes"] for entry in chain[depth:]])
    return None


# --- The SAME message subtree in an ordinary form-view chatter (LIGHT bundle) ---------------------
# The island models above stop at the spreadsheet side panel; these stop at the form view's own
# chatter container, and everything between the Chatter root and the glyphs is shared - one
# transcription of message.xml, two places it renders. `.o-mail-Form-chatter` is the div the form
# compiler emits (mail/static/src/chatter/web/form_compiler.js:27) and the outermost layer in this
# stack that actually PAINTS: form_renderer.scss:5-6 fills it with `$o-webclient-background-color`,
# while every layer inside it down to `.o-mail-Message` is `bg-inherit`. That makes the light
# chatter panel a resolved value rather than an assumed white, which matters - it is `$o-gray-100`,
# a shade DARKER than white, so a tier tuned against white is already optimistic here.
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

# message.xml:110 - the placeholder core renders INSTEAD of a body when a message has no content.
# It is a direct child of `.o-mail-Message-body`, so it is inside `.o-discuss-text-body` and a
# bubbled message paints its bubble behind it.
#
# ITS TAG IS LOAD-BEARING, not decoration. Core styles this element through
# `.o-mail-Message-body > i.text-muted.opacity-75`, so a class-only model skips that rule entirely
# and measures the placeholder at the dimmed opacity the rule exists to cancel. Both halves of that
# selector have to be modelled: the `<i>` tag and the DIRECT-CHILD relation to the body.
MESSAGE_EMPTY_PLACEHOLDER_TAG = "i"
MESSAGE_EMPTY_PLACEHOLDER_CLASSES = frozenset({"text-muted", "opacity-75"})

# message.xml:151-153 rendered into the `<span class="o-mail-Message-edited"/>` marker the server
# writes into the body HTML (`_message_update_content`), which message.js:449-450 finds inside the
# body ref and fills. The span therefore renders inside the rich-body div, itself inside
# `.o-mail-Message-body` - so this marker is inside `.o-discuss-text-body` too.
MESSAGE_EDITED_MARKER_TAG = "span"
MESSAGE_EDITED_MARKER_CLASSES = frozenset({"o-xsmaller", "opacity-50"})
_MESSAGE_EDITED_SPAN = frozenset({"o-mail-Message-edited"})
_MESSAGE_RICH_BODY_CLASSES = frozenset({"o-mail-Message-richBody", "overflow-x-auto"})


def _body_muted_layers(message_layers):
    """Ancestor layers of a muted marker core renders DIRECTLY inside `.o-mail-Message-body`.

    The empty-message placeholder (message.xml:110), the `Subject:` line (:113) and the two
    translation notes (:117, :120) all hang off the same two wrappers, so the only thing that varies
    between render sites is ``message_layers`` - the container the message list is dropped into."""
    return (MESSAGE_BODY_CLASSES, MESSAGE_TEXT_BODY_CLASSES) + message_layers


def _edited_marker_layers(message_layers):
    """Ancestor layers of the `(edited)` span, two wrappers deeper than a direct body marker.

    The server writes `.o-mail-Message-edited` into the body HTML and core's JS fills it, so the
    span sits inside that marker inside the rich-body div - and only then reaches the body wrapper
    the muted markers start from."""
    return (
        _MESSAGE_EDITED_SPAN, _MESSAGE_RICH_BODY_CLASSES,
    ) + _body_muted_layers(message_layers)


CHATTER_EDITED_MARKER_LAYERS = _edited_marker_layers(CHATTER_MESSAGE_LAYERS)

# --- The SAME message subtree in the OTHER two containers it renders in --------------------------
# The two nodes below are not chatter-only: `Thread` renders the identical message subtree in the
# Discuss app and in a chat window, and each of the three containers paints a DIFFERENT panel under
# it. That is the whole reason they are modelled separately rather than measured once - a fix tuned
# against one panel is not a fix for the other two, and in the dark bundle the three panels are two
# distinct greys.

# discuss_content.xml:67 the `bg-inherit` column that holds the thread, :65 the scrolling core,
# :63 the main row, :6 the DiscussContent root, then discuss.xml:5 the Discuss root. The CORE layer
# is the one that paints: `.o-mail-DiscussContent-core { background-color: $body-bg }`
# (discuss_content.scss:7-9), which the dark recompile drives to the dark view surface.
DISCUSS_THREAD_COLUMN_CLASSES = frozenset({
    "d-flex", "flex-column", "flex-grow-1", "bg-inherit", "o-min-width-0",
})
DISCUSS_CONTENT_CORE_CLASSES = frozenset({
    "o-mail-DiscussContent-core", "overflow-auto", "o-scrollbar-thin", "d-flex", "flex-grow-1",
    "w-100",
})
DISCUSS_CONTENT_MAIN_CLASSES = frozenset({
    "o-mail-DiscussContent-main", "d-flex", "overflow-hidden", "flex-grow-1",
})
DISCUSS_CONTENT_CLASSES = frozenset({
    "o-mail-DiscussContent", "d-flex", "flex-column", "h-100", "w-100", "overflow-auto",
    "o-scrollbar-thin",
})
DISCUSS_ROOT_CLASSES = frozenset({"o-mail-Discuss", "d-flex", "h-100", "flex-grow-1"})
DISCUSS_PANEL_LAYERS = (
    DISCUSS_THREAD_COLUMN_CLASSES, DISCUSS_CONTENT_CORE_CLASSES, DISCUSS_CONTENT_MAIN_CLASSES,
    DISCUSS_CONTENT_CLASSES, DISCUSS_ROOT_CLASSES, WEBCLIENT_ANCESTORS,
)
DISCUSS_MESSAGE_LAYERS = MESSAGE_SUBTREE_TO_THREAD_LAYERS + DISCUSS_PANEL_LAYERS

# chat_window.xml:65 the `bg-inherit` content column, :6 the window root. The ROOT is the one that
# paints, and it paints through the `bg-100` utility - an `!important` (0,1,0) declaration that no
# normal rule can outrank at any specificity, which is why the dark de-light of this surface has to
# carry the flag too and why the window is modelled down to that layer rather than assumed dark.
# The window is `fixed-bottom` on the web client root, NOT inside the action manager, so its outer
# pool is the client alone.
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

# The three containers a message renders in OUTSIDE the spreadsheet island, each with the panel its
# own ancestor walk lands on. Declared as data rather than as three copied guards so a fourth
# container is one row, and so no subject can be measured in two of them and silently skip the
# third.
DARK_MESSAGE_CONTAINERS = (
    ("form-view chatter", "the form-view chatter panel", CHATTER_MESSAGE_LAYERS),
    ("Discuss", "the Discuss thread canvas", DISCUSS_MESSAGE_LAYERS),
    ("chat window", "the chat-window body", CHAT_WINDOW_MESSAGE_LAYERS),
)

# The same two nodes inside the spreadsheet island. The island's placeholder stack is already
# `ISLAND_MESSAGE_BODY_MUTED_LAYERS` (the `Subject:` line shares it); only the marker needs its own.
ISLAND_EDITED_MARKER_LAYERS = _edited_marker_layers(ISLAND_MESSAGE_LAYERS)


# The surface a resolution landed on, and WHO painted it. `painter` is what a failure message needs
# in order to be actionable: "the o-blue bubble" and "layer 9 of the chain" send a reader to
# different files.
Backdrop = collections.namedtuple("Backdrop", "painter depth value rgb")


@tagged("post_install", "-at_install")
class MailContrastCompileTest(TransactionCase):
    """Every branded mail surface must COMPILE to a colour pair its glyphs can be read on.

    Additive to the module's existing de-brand guards, none of which look at compiled CSS."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Memoised per class: the payload is derived purely from source files, so it is identical
        # for every test method and a recompile per assertion would dominate this class' runtime.
        # Deriving it from files (never from records written by a test) keeps every method
        # independent and order-insensitive.
        cls._compiled_css_cache = {}

    def _compile(self, bundle_name):
        """Compile ``bundle_name`` and return ``(bundle, css_text)``.

        Grounded 19.0 API: ``ir.qweb._get_asset_bundle(name, css=True, js=False)`` returns an
        AssetsBundle; ``.css()`` returns the compiled ``ir.attachment`` recordset and
        ``attachment.raw`` is its binary content. Join across the recordset so a split bundle is
        handled, and decode leniently so an assertion (not a decode error) reports any problem."""
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

    # ------------------------------------------------------------------------------------------
    # Cascade resolution - the R-7 hardening
    # ------------------------------------------------------------------------------------------
    def _require_cascade_resolver(self):
        """Fail crisply when the cluster's shared cascade resolver could not be imported."""
        self.assertIsNotNone(
            _computed_value,
            "viin_brand_web/tests/test_brand_cascade_compile.py must expose _computed_value and "
            "_winning_declaration: they are the cluster's SINGLE cascade resolver and every guard "
            "below resolves its value THROUGH core's own consumer with them, so a core rename goes "
            "RED instead of orphaning our declaration silently.",
        )

    def _require_scope_filter(self):
        """Fail crisply when the cluster's shared ANCESTOR model could not be imported.

        Every guard that reads raw declarations and takes the LAST one needs it: without the
        ancestor filter a rule scoped under some other module's root has the same SUBJECT and is
        the later writer, so the guard reports a colour that renders in a context it does not
        measure. Silently falling back to the unfiltered read would leave that hazard armed while
        the suite stayed green, which is the exact failure this check exists to prevent."""
        self.assertIsNotNone(
            _selector_scope_applies,
            "viin_brand_web/tests/test_brand_cascade_compile.py must expose "
            "_selector_scope_applies: it is the cluster's SINGLE ancestor model, and the guards "
            "that read the LAST declaration of a subject use it to drop rules scoped to a context "
            "their element is not in - a browser never applies those, so neither may a guard that "
            "claims to read what renders.",
        )

    def _resolve(self, css, chain, prop_names, surface):
        """Return the raw value the CSS cascade computes for ``prop_names`` on ``chain[0]``.

        ``chain`` is the element and its styling ancestors, innermost first. This is the whole
        point of the R-7 hardening: the answer comes from the CORE RULE THAT READS the property
        (Bootstrap's `.btn.active { color: var(--btn-active-color) }`, core's
        `.o_menu_systray .badge { background-color: var(--o-navbar-badge-bg, ...) }`, ...), with
        `var()` followed outwards through the chain exactly as a browser resolves an inherited
        custom property. If core renames the property, our declaration stops being reachable from
        that consumer and this fails - which a read-our-own-declaration-back check cannot do."""
        self._require_cascade_resolver()
        value = _computed_value(css, chain, prop_names)
        self.assertIsNotNone(
            value,
            "No compiled declaration of %s applies to %s. Either core moved the surface to a "
            "different lever, or the selector this module overrides no longer matches - in both "
            "cases the branded value is not reaching the pixel."
            % ("/".join(prop_names), surface),
        )
        return value

    def _resolve_colour(self, css, chain, prop_names, surface):
        """Resolve ``prop_names`` on ``chain[0]`` and return ``(raw_value, rgb)``.

        Colours are normalised through this file's own ``_to_rgb`` rather than the resolver
        module's ``_normalize_colour`` because several of this module's declarations are the
        keyword ``white``, which Sass emits verbatim inside a custom property and which a
        hex-only normaliser reads as "no colour at all"."""
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

    def _plain_composer_surface(self, css, bundle_name, all_rules, gated_rules):
        """Return the surface a composer NOT in send-message mode renders on, as ``(r, g, b)``.

        Resolved the way a browser would, which differs by bundle and is exactly why it is derived
        rather than pinned:
          * DARK - this module's own dark tail declares --mail-Composer-bg on `.o-mail-Composer`
            (a 6%-lifted panel), so an ungated declaration exists and the last one wins;
          * LIGHT - nothing declares the token at all, so every composer falls through to the
            FALLBACK inside core's own consumer, `background-color: var(--mail-Composer-bg, <x>)`.
        Reading the fallback out of that consumer keeps the comparison honest in both schemes; a
        hardcoded white would go stale the day core lifts the light composer too."""
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
        """Return the DIMMEST opacity core applies to the composer placeholder in ``css``.

        Core ships several (`40%` base, `50%` focused/unfocused variants), so the worst case - the
        lowest alpha, i.e. the faintest placeholder - is the honest one to composite. Read from the
        compiled bundle rather than hardcoded, so a core change to the dimming is caught."""
        alphas = []
        for tokens, body in _iter_rules(css):
            if not any(_COMPOSER_PLACEHOLDER_SELECTOR in token for token in tokens):
                continue
            for match in _OPACITY_RE.finditer(body):
                alpha = _to_alpha(_normalize_value(match.group(1)))
                if alpha is not None:
                    alphas.append(alpha)
        self.assertTrue(
            alphas,
            "No `%s` opacity rule found in %s - core stopped dimming the composer placeholder, so "
            "the composited value this guard measures can no longer be derived."
            % (_COMPOSER_PLACEHOLDER_SELECTOR, bundle_name),
        )
        return min(alphas)

    def _assert_core_source_contains(self, source, needles, why):
        """Assert core's OWN source still contains each needle - the name-existence fallback.

        Used only where the cascade resolution is genuinely inexpressible (see the two docstrings
        that call this). It is weaker than resolving the value, but it closes the exact hole R-7
        describes: a core RENAME of the property makes this RED instead of silently orphaning our
        declaration. ``file_open`` resolves the path against the addons path, so this works from
        any checkout layout (ODOO-AI-ETHOS #11 portability)."""
        with file_open(source, "r") as core_file:
            content = core_file.read()
        for needle in needles:
            self.assertIn(
                needle, content,
                "%s no longer contains %r. %s Re-ground this guard against the new lever rather "
                "than deleting it." % (source, needle, why),
            )

    # ------------------------------------------------------------------------------------------
    # 1. Chat-window header surface
    # ------------------------------------------------------------------------------------------
    def test_chat_window_header_renders_brand_teal_never_the_mis_ported_purple(self):
        """The chat-window header must be the brand teal chrome carrying readable white text.

        Pre-fix this compiled to `mix(black, $o-brand-secondary, 15%)` = #6C386F, the purple the
        19.0 port substituted for the lost 18.0 `$brand-primary-dark`, so this test was RED on the
        teal assertion and on the explicit purple guard. The `.o-mail-ChatWindow-header` ELEMENT
        is isolated from its descendants (`.o-mail-ChatWindow-header .o-mail-ActionList-group` and
        friends carry their own colours and are not the chrome under test)."""
        css = self._compiled_css(BACKEND_BUNDLE)
        header_element = re.compile(r"^\.o-mail-ChatWindow-header([:.]|$)")
        bodies = _bodies_matching(css, header_element.match, ANY_ANCESTORS)
        self.assertTrue(
            bodies,
            "No rule targets the .o-mail-ChatWindow-header element itself in compiled %s - the "
            "module's chat-window de-brand did not reach the bundle." % BACKEND_BUNDLE,
        )

        backgrounds = _declared_hexes(bodies, _BACKGROUND_RE)
        self.assertTrue(
            backgrounds,
            "The .o-mail-ChatWindow-header element declares no background colour in compiled %s; "
            "the branded header chrome cannot be verified." % BACKEND_BUNDLE,
        )
        self.assertNotIn(
            MIS_PORTED_HEADER_PURPLE, backgrounds,
            "Chat-window header regressed to the mis-ported PURPLE %s (backgrounds: %r). 18.0 "
            "painted this header in the darkened brand TEAL; the 19.0 port substituted "
            "mix(black, $o-brand-secondary, 15%%)." % (MIS_PORTED_HEADER_PURPLE, backgrounds),
        )
        self.assertNotIn(
            BRAND_SECONDARY_PURPLE, backgrounds,
            "Chat-window header compiled to the brand SECONDARY purple %s (backgrounds: %r). The "
            "header chrome belongs to the teal CHROME-BASE tier, not the secondary tier."
            % (BRAND_SECONDARY_PURPLE, backgrounds),
        )

        # Last writer wins at equal specificity - this is what actually renders.
        self.assertEqual(
            backgrounds[-1], CHROME_BASE_TEAL,
            "Chat-window header must render the CHROME-BASE AA teal %s (the $o-navbar-background "
            "SSOT token); compiled backgrounds were %r." % (CHROME_BASE_TEAL, backgrounds),
        )

        header_colors = _declared_values(bodies, _COLOR_RE)
        self.assertTrue(
            header_colors,
            "The .o-mail-ChatWindow-header element declares no text colour; white-on-teal is part "
            "of the restored 18.0 semantic and must be explicit.",
        )
        foreground = self._assert_rgb(header_colors[-1], "chat-window header text colour")
        background = self._assert_rgb(backgrounds[-1], "chat-window header background")
        ratio = _contrast_ratio(foreground, background)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "Chat-window header text (%s) on its background (%s) is only %.2f:1 - WCAG AA normal "
            "text needs >= %.1f:1." % (header_colors[-1], backgrounds[-1], ratio, WCAG_AA_NORMAL_TEXT),
        )

    # ------------------------------------------------------------------------------------------
    # 2. Chat-window header action icons
    # ------------------------------------------------------------------------------------------
    def test_chat_window_header_action_icons_are_readable_as_composited(self):
        """Header action glyphs must be readable AS RENDERED - colour AND opacity together.

        v19 moved Fold/Close into mail/static/src/core/common/action_list.*, so they render as
        `.o-mail-ActionList-button` (a .btn.btn-secondary) and the ported rules matched nothing:
        the glyphs kept the Bootstrap secondary foreground #212529 = 1.79:1 on the teal header.
        Repainting them white is NOT sufficient on its own - core dims idle header actions with
        `--o-mail-ActionList-Button-opacity: .5`, which composites even pure white down to 2.30:1,
        below the 3:1 non-text floor. Both levers are therefore asserted, and the pass/fail rule
        is stated on the COMPOSITED colour so neither lever can regress unnoticed.

        R-7 TREATMENT: NAME-EXISTENCE, not cascade resolution - and this is the one surface where
        that is a deliberate choice rather than a shortcut. BOTH sides of this rule are
        inexpressible for the cluster's class-based cascade resolver:
          * this module's own selector is `.o-mail-ChatWindow-header .o-mail-ActionList button` -
            its SUBJECT is the TYPE selector `button`, which the resolver does not model (nor does
            core's mirrored `... .o-mail-ActionList-group button:not(...)`), so neither rule would
            ever be seen as a candidate and the resolver would report "nothing paints this";
          * core's opacity consumer is
            `button.o-inline:where(:has(i:first-child:last-child)) { opacity: var(...) }`
            (mail/static/src/core/common/action_list.scss:18-20) - a `:has()` relational selector,
            which cannot be evaluated at all without a DOM.
        So the declarations are still read directly, and the RENAME hole R-7 describes is closed by
        asserting that core still READS each of those four properties in its own source. If
        Bootstrap renames --btn-color or core renames --o-mail-ActionList-Button-opacity, our
        declarations become orphans and these assertions - not a green test - report it."""
        css = self._compiled_css(BACKEND_BUNDLE)

        # The four properties this surface is restored through must still be the ones CORE reads.
        # Without this, every assertion below would keep passing on our own orphaned declarations.
        self._assert_core_source_contains(
            "web/static/lib/bootstrap/scss/_buttons.scss",
            (
                "--#{$prefix}btn-color", "color: var(--#{$prefix}btn-color)",
                "color: var(--#{$prefix}btn-hover-color)",
                "color: var(--#{$prefix}btn-active-color)",
            ),
            "Bootstrap no longer resolves a .btn's foreground through that custom property, so the "
            "white glyph this module pins on the chat-window header is an orphaned declaration and "
            "the header actions have silently reverted to the Bootstrap secondary foreground.",
        )
        self._assert_core_source_contains(
            "mail/static/src/core/common/action_list.scss",
            ("opacity: var(--o-mail-ActionList-Button-opacity)",),
            "Core no longer dims ActionList buttons through that custom property, so this module's "
            "`--o-mail-ActionList-Button-opacity: 1` no longer un-dims anything and the header "
            "glyphs are back below the non-text contrast floor.",
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

        # --- Glyph colour: idle, hover and active must all be white on the teal chrome ----------
        for token in ("btn-color", "btn-hover-color", "btn-active-color"):
            values = _declared_values(bodies, _custom_property_re(token))
            self.assertTrue(
                values,
                "The chat-window header's ActionList buttons declare no --%s. v19 resolves the "
                "button foreground through that token (core's own livechat patch drives the same "
                "one), so leaving it unset keeps the Bootstrap secondary glyph #212529 = 1.79:1 "
                "on the teal header." % token,
            )
            glyph_rgb = self._assert_rgb(values[-1], "chat-window header --%s" % token)
            self.assertEqual(
                glyph_rgb, WHITE_RGB,
                "Chat-window header --%s compiled to %r; the restored 18.0 semantic is a WHITE "
                "glyph on the teal chrome." % (token, values[-1]),
            )

        # --- Opacity: the idle dimming must be neutralised on this branded surface --------------
        opacity_values = _declared_values(bodies, _custom_property_re("o-mail-ActionList-Button-opacity"))
        self.assertTrue(
            opacity_values,
            "The chat-window header's ActionList buttons declare no "
            "--o-mail-ActionList-Button-opacity, so core's idle `.5` stands and even a white "
            "glyph composites to 2.30:1 on the teal header.",
        )
        effective_alpha = _to_alpha(opacity_values[-1])
        self.assertIsNotNone(
            effective_alpha,
            "--o-mail-ActionList-Button-opacity compiled to %r, which is not an opacity this "
            "contrast guard can composite." % (opacity_values[-1],),
        )

        # --- The rule itself: the glyph AS COMPOSITED must clear WCAG AA ------------------------
        composited = _composite(WHITE_RGB, header_rgb, effective_alpha)
        ratio = _contrast_ratio(composited, header_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "A white header action glyph at opacity %s composites to rgb%r on the header (%s), "
            "which is only %.2f:1. Restoring the 18.0 `opacity: 1` semantic is what takes it to "
            "AA - the glyph colour alone is not enough."
            % (opacity_values[-1], composited, header_backgrounds[-1], ratio),
        )

    # ------------------------------------------------------------------------------------------
    # 2b. Chat-window header muted breadcrumb glyph
    # ------------------------------------------------------------------------------------------
    def test_chat_window_header_muted_glyph_is_realigned_to_the_white_chrome(self):
        """A `.text-muted` glyph in the header must take the header's white, not Bootstrap grey.

        Core renders the parent-channel breadcrumb separator as
        `<i class="fa fa-chevron-right ... text-muted opacity-75"/>` inside the header
        (mail/static/src/core/common/chat_window.xml, the mail.ChatWindow.headerContent
        sub-template). Bootstrap's `.text-muted` is `color: var(--bs-secondary-color) !important`
        = grey #495057, so unlike the channel-name span beside it - which is white via the header
        `color` inherit (proven in test #1) - this glyph stays ~2.3:1 on the teal chrome, below the
        3:1 non-text floor. This module realigns it with `.o-mail-ChatWindow-header .text-muted {
        color: inherit !important }`, so it takes the header's white exactly like its sibling.

        The behaviour under test is "no muted glyph is left as Bootstrap grey on the teal header":
        asserted as the RULE (`color: inherit`, beating Bootstrap's own `!important`) rather than a
        hex, because the legible value is whatever the header foreground computes to - and test #1
        already proves that foreground is white at AA. Dropping the override hands the glyph back to
        Bootstrap's grey `!important` and this goes RED."""
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
            "parent-channel breadcrumb chevron on the teal header - ~2.3:1, below the 3:1 non-text "
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
            "test #1 pins - inherit keeps the two in lock-step." % colors,
        )

    # ------------------------------------------------------------------------------------------
    # 3. Chatter composer toggles - teal "Send message" vs the DEFAULT neutral "Log note"
    # ------------------------------------------------------------------------------------------
    def test_chatter_open_composer_toggles_are_teal_for_send_and_the_default_grey_for_log_note(self):
        """"Send message" and "Log note", while OPEN, must be DIFFERENT and both readable.

        THE SHIPPING BUG THIS STILL PROTECTS. One shared selector painted BOTH toggles the same
        purple, so the single most consequential distinction in the chatter - a Log note is INTERNAL,
        a Send message goes to the CUSTOMER - had no colour at all while composing. It also pinned the
        label to the literal `white`, which in the recompiled dark bundle measured 2.90:1 on the
        purple's (now retired) dark arm. Both halves are asserted below and neither may come back.

        >>> OWNER REVISION 2026-08-03: "Log note" IS NOT PURPLE - IT IS THE DEFAULT GREY. <<<
        The intermediate fix kept the purple on Log note as a faithful port of 18.0's
        `$o-enterprise-primary-color`. The owner reversed that. So a test asserting Log note is PURPLE
        is now WRONG, and so is one asserting it is TEAL: it must render the stock `.btn-secondary`.

        HOW "THE DEFAULT" IS ASSERTED, AND WHY NOT A HEX. The oracle is a REAL stock `.btn-secondary`
        resolved out of the SAME bundle - the core web pager arrow, whose element model
        viin_brand_web owns - and the claim is that the open Log note computes the SAME fill and
        the SAME label as it. That is the behaviour ("it renders the default neutral button"), it is
        automatically correct in both schemes (light #212529-on-#DEE2E6, dark #EDF4F5-on-#25383C via
        dark_buttons.scss), and it cannot be satisfied by a grey that merely looks right today.
        Left to core this button would NOT be that: it carries `btn-primary active`, so it would
        resolve the PRIMARY map's near-white active state (#E6F2F4 fill, #002428 label) - a near-white
        island on the dark canvas. That is why a rule is needed at all, and the "equals the stock
        neutral" assertion is what proves the rule landed on the right values.

        WHY SEND MESSAGE IS THE *DEEP* TEAL. The chrome base #007F8E is already this button's RESTING
        `.btn-primary` fill, so reusing it would make an open composer indistinguishable from a closed
        one; #005E68 is the ladder's established pressed/open rung (7.5:1 with white).

        R-7 TREATMENT: the labels are resolved from `color` through Bootstrap's own
        `.btn.active { color: var(--btn-active-color) }` consumer, never read back out of this
        module's own declaration - so a Bootstrap rename makes the value unresolvable and this RED.

        WOULD FAIL IF REVERTED: re-merging the two selectors makes the fills equal and trips the "must
        not be the same colour" assertion; re-painting Log note purple trips the explicit purple
        guards in BOTH arms; dropping the Log-note rule entirely leaves core's near-white #E6F2F4,
        which is not the stock neutral and trips the equality assertion; dropping the
        --btn-active-color re-point hands the label back to the primary map's #002428."""
        self._require_scope_filter()
        # The element models below are transcribed from this template; assert the transcription is
        # still true, or a class rename would leave them stale and the guard measuring an element
        # that no longer exists.
        self._assert_core_source_contains(
            "mail/static/src/chatter/web/chatter.xml",
            ("o-mail-Chatter-sendMessage btn", "'btn-primary active'"),
            "The chatter toggles no longer carry those classes, so both this module's override and "
            "the modelled active elements below are keyed on markup core stopped rendering.",
        )
        self.assertIsNotNone(
            PAGER_PREVIOUS_CLASSES,
            "viin_brand_web/tests/test_brand_cascade_compile.py must expose PAGER_ANCESTORS / "
            "PAGER_PREVIOUS_CLASSES: they model the stock `.btn-secondary` this guard compares the "
            "open Log-note toggle against, so 'the default neutral button' is measured rather than "
            "re-literalised here.",
        )

        for arm, bundle_name, surface_note in (
            ("light", BACKEND_BUNDLE, "the light chatter"),
            ("dark", DARK_BUNDLE, "the dark chatter (%s panel)" % DARK_PANEL),
        ):
            css = self._compiled_css(bundle_name)

            # The oracle: what a stock `.btn-secondary` computes in THIS bundle.
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
                    # Match ONLY rules that style the toggle ITSELF (the button is the selector
                    # SUBJECT), never rules where `<toggle>.active` sits inside a :has()/ancestor
                    # condition styling a DIFFERENT element - which is exactly the shape the
                    # send-message composer danger cue uses (test 3b). CHATTER_ANCESTORS is the
                    # same element model the cascade resolution below uses, so the raw read and the
                    # resolved read answer for ONE element: a rule scoped under another module's
                    # root shares this subject but never paints this button.
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

                    # NO PURPLE, either scheme, either toggle - the owner revision, asserted
                    # positively so a well-meant restore of either purple is caught.
                    self.assertNotIn(
                        BRAND_SECONDARY_PURPLE, backgrounds,
                        "The OPEN %s compiled the brand purple %s in the %s bundle. The owner "
                        "removed the purple from the chatter toggles on 2026-08-03: Send message is "
                        "teal, Log note is the default neutral."
                        % (toggle, BRAND_SECONDARY_PURPLE, arm),
                    )
                    self.assertNotIn(
                        RETIRED_DARK_PURPLE, backgrounds,
                        "The OPEN %s compiled the RETIRED dark purple %s in the %s bundle. That arm "
                        "of $o-brand-secondary was deleted because core's forced white label "
                        "measured only 2.90:1 on it - do not bring it back."
                        % (toggle, RETIRED_DARK_PURPLE, arm),
                    )

                    # The declaration must exist at all ...
                    label_values = _declared_values(bodies, _custom_property_re("btn-active-color"))
                    self.assertTrue(
                        label_values,
                        "Active %s declares no --btn-active-color, so v19's `.btn.active { color: "
                        "var(--btn-active-color) }` falls back to the primary-button map's dark "
                        "teal #002428 - a 1.07:1 label on the teal, and the wrong label on the "
                        "neutral." % toggle,
                    )

                    # ... and it must still be the token BOOTSTRAP resolves this element's `color`
                    # through. Reading our own declaration back and measuring it against itself
                    # would stay green after a Bootstrap rename, with the label unreadable on screen.
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
                        # THE OWNER'S RULE, stated as behaviour: this is the DEFAULT neutral button.
                        self.assertEqual(
                            fill_rgb, neutral_fill_rgb,
                            "The OPEN 'Log note' toggle compiled %s in the %s bundle, but a stock "
                            "`.btn-secondary` in the same bundle computes %s. The owner asked for "
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
                "customer-facing (TEAL = ACT) and 'Log note' is internal (the default neutral); one "
                "colour for both erases the distinction while composing - the exact bug this split "
                "fixes." % (send_fill, arm),
            )
            self.assertEqual(
                send_fill, CHROME_DEEP_TEAL,
                "The OPEN 'Send message' toggle compiled %s instead of the deep chrome rung %s in "
                "the %s bundle. Customer-facing = ACT = teal; the chrome base %s is this button's "
                "RESTING fill (open would look identical to closed) and core's untouched "
                "active-background is the near-white #E6F2F4."
                % (send_fill, CHROME_DEEP_TEAL, arm, CHROME_BASE_TEAL),
            )

    # ------------------------------------------------------------------------------------------
    # 3b. The chatter composer wears a DANGER cue while it is addressed to a CUSTOMER
    # ------------------------------------------------------------------------------------------
    def test_send_message_composer_carries_a_readable_danger_cue_log_note_does_not(self):
        """Composing to a CUSTOMER must look different - and dangerous - from logging a note.

        WHAT ODOO 19 CE DOES ON ITS OWN: NOTHING. Grounded, because the assumption that "core already
        tints the log-note composer" is what this guard exists to stop drifting back in.
        `mail/static/src/core/common/composer.js` reads `props.type` in exactly four places and none
        is visual chrome - the send-button label (:411), the placeholder (:567), the message subtype
        (:614) and the full-composer dialog title (:624). `composer.xml` puts no mode class on any
        element. The single theming hook, `--mail-Composer-bg`, is re-pointed only by
        `composer.dark.scss`, i.e. per SCHEME, never per mode. So without this rule an outbound,
        customer-visible message is composed on a surface identical to an internal note's.

        THE BEHAVIOUR UNDER TEST, in three parts:
          1. the cue EXISTS and is DANGER-derived - the send-message composer surface is measurably
             closer to $danger than the untinted composer fill it replaces (a real property of a
             tint, not a hex snapshot, so a re-tune of the wash percentage is not a false alarm);
          2. it is a TINT, not a fill - the composer text still clears WCAG AA on it, in BOTH
             schemes, and the (core-dimmed) placeholder is not made worse than it already is on the
             untinted surface;
          3. it is SCOPED to send-message mode - every rule carrying it is gated on
             `.o-mail-Chatter-sendMessage.active`, so the Log-note composer keeps the plain surface
             and the two modes are told apart by the surface the user types ON.

        R-7 TREATMENT: NAME-EXISTENCE, and here it is forced rather than chosen. The whole cue hangs
        off a `:has()` relational selector, which cannot be evaluated without a DOM - the cluster's
        class-based cascade resolver rejects any selector containing one (`_compound_matches` returns
        False for an unmodelled pseudo-class), exactly as it does for core's own
        `button.o-inline:where(:has(...))`. So the declarations are read directly, and the rename hole
        is closed by asserting that CORE still reads each lever in its own source: the
        `--mail-Composer-bg` consumer, the `border` utility's `--border-color`, and the
        `.o-mail-Chatter-sendMessage` + `active` markup the `:has()` keys on.

        THE $danger ANCHOR IS CORE'S OWN EMISSION, not our declaration: Bootstrap emits `--danger` on
        :root from `$danger`, so the border is compared against that rather than against a hex this
        module chose.

        WHY THE RULE POOL IS ANCESTOR-FILTERED. Both the tinted surface and the plain one are read as
        the LAST declaration of --mail-Composer-bg, so every rule in the pool has to be one that can
        reach THIS composer. COMPOSER_ANCESTORS models the three chains it really renders in
        (chatter, Discuss, chat window); a rule scoped under another module's root carries the same
        `.o-mail-Composer` subject and the same `:has()` gate, and would otherwise be read as both
        the last gated writer AND - since it is not gated on the toggle - an ungated declaration of
        the "plain" surface, corrupting both halves of the comparison at once.

        WOULD FAIL IF REVERTED: dropping the rules leaves the composer at its untinted fill and trips
        both the "cue exists" and the "closer to danger" assertions; a full red fill trips the AA
        assertion; removing the `:has()` gate (tinting every composer) trips the scoping assertion."""
        self._require_scope_filter()
        self._assert_core_source_contains(
            "mail/static/src/core/common/composer.scss",
            ("background-color: var(--mail-Composer-bg",),
            "Core no longer paints the composer surface through --mail-Composer-bg, so the danger "
            "tint is fed to a property nothing reads and the customer-facing composer silently looks "
            "identical to an internal note again.",
        )
        self._assert_core_source_contains(
            "mail/static/src/chatter/web/chatter.xml",
            ("o-mail-Chatter-sendMessage btn", "'active': state.composerType === 'message'"),
            "The chatter no longer marks the Send-message toggle `active` while the message composer "
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

            # --- 3. SCOPING. Every declaration of the composer surface token that is NOT core's own
            # must be gated on the send-message toggle being active; otherwise the "cue" is just a
            # restyle of every composer and says nothing about who the message is going to.
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

            # --- 1. THE CUE EXISTS AND IS DANGER-DERIVED.
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
                "the plain composer surface %s is, in the %s bundle. Whatever it was tinted with, it "
                "was not danger - and a cue the user cannot read as 'risky' is not the cue the owner "
                "asked for." % (tinted_rgb, danger_rgb, untinted_rgb, arm),
            )

            # ... and the FRAME. Bootstrap's `border` utility reads --border-color, which is also the
            # lever core itself drives for the composer's focus state, so feeding it is the whole fix.
            self._assert_core_source_contains(
                "mail/static/src/core/common/composer.scss",
                ("--border-color",),
                "Core no longer drives the composer container's border through --border-color, so "
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
                "the %s bundle. The brief forbids a new hex here - the frame IS the danger token."
                % (frame_rgb, danger_rgb, arm),
            )

            # --- 2. IT IS A TINT, NOT A FILL. The composer text is a `.form-control`, so it resolves
            # the body colour; measured against the tinted surface it must clear AA in both schemes.
            text_ratio = _contrast_ratio(body_rgb, tinted_rgb)
            self.assertGreaterEqual(
                text_ratio, WCAG_AA_NORMAL_TEXT,
                "Composer text %s on the danger-tinted surface %s is only %.2f:1 in the %s bundle - "
                "below the WCAG AA normal-text threshold of %.1f:1. The cue must stay a TINT; a fill "
                "saturated enough to hurt the text is not acceptable at any warning level."
                % (body_rgb, tinted_rgb, text_ratio, arm, WCAG_AA_NORMAL_TEXT),
            )

            # The PLACEHOLDER is core's, dimmed by core's own `::placeholder { opacity }`, and it
            # does NOT clear AA on the plain white composer either (~2.4:1) - a pre-existing core
            # condition this change neither causes nor can fix. What IS this change's responsibility
            # is not making it worse, so the rule asserted is non-degradation against the very same
            # placeholder on the untinted surface, with the opacity READ from the compiled bundle.
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

    # ------------------------------------------------------------------------------------------
    # 4. Composer send button
    # ------------------------------------------------------------------------------------------
    def test_send_message_button_renders_the_aa_teal_under_its_forced_white_glyph(self):
        """The real send button must be the AA teal, not core's lighter `lighten($primary, 7.5%)`.

        v19 renders the ACTIVE send button through the composer action list
        (composer_actions.js -> btnClass "o-sendMessageActive o-text-white"), NOT as the
        `.o-mail-Composer-send.btn-link` the port targeted - so the ported rule matched nothing in
        every bundle and core's `lighten($primary, 7.5%)` (~#00A1B4) stood under the white glyph
        core itself forces, at ~3.1:1. Because this module's rule has the SAME specificity as
        core's and wins only on load order, the assertion reads the LAST declaration: if the
        override is dropped, the last writer is core's lighter teal and this goes red."""
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
            "the real v19 send button is unstyled by this module." % BACKEND_BUNDLE,
        )

        backgrounds = _declared_hexes(bodies, _BACKGROUND_RE)
        self.assertTrue(backgrounds, "the active send button declares no background colour.")
        self.assertEqual(
            backgrounds[-1], CHROME_BASE_TEAL,
            "The active send button must compile to the CHROME-BASE AA teal %s; compiled "
            "backgrounds were %r (core paints it lighten($primary, 7.5%%) ~#00a1b4)."
            % (CHROME_BASE_TEAL, backgrounds),
        )
        ratio = _contrast_ratio(WHITE_RGB, self._assert_rgb(backgrounds[-1], "send button background"))
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The send button glyph is forced white by core's `o-text-white`, but its background "
            "(%s) gives only %.2f:1 - WCAG AA needs >= %.1f:1."
            % (backgrounds[-1], ratio, WCAG_AA_NORMAL_TEXT),
        )

    # ------------------------------------------------------------------------------------------
    # 5. Presence (im_status) dot
    # ------------------------------------------------------------------------------------------
    def test_im_status_online_dot_is_legible_on_its_white_puck(self):
        """The online/bot presence dot must be the AA teal - not purple, not the flat brand teal.

        Pre-fix the port had substituted `$o-brand-secondary` here, so this was RED on the purple
        guard. The flat brand teal is separately refused: mail.ImStatus always renders the glyph
        on a `bg-white bg-opacity-100` puck (mail/static/src/core/common/im_status.xml), including
        inside the teal chat-window header, and the flat teal is only 2.33:1 on white - below the
        3:1 WCAG non-text floor for a meaningful status indicator."""
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be importable from "
            "viin_brand_web/controllers/webmanifest.py (the single Python brand-hex SSOT).",
        )
        flat_brand_teal = VIINDOO_THEME_COLOR.lower()

        css = self._compiled_css(BACKEND_BUNDLE)
        for host in (".o-mail-ImStatus", ".o-mail-ThreadIcon"):
            with self.subTest(host=host):
                bodies = _bodies_matching(
                    css,
                    lambda selector: selector.startswith(host + " ")
                    and ".text-success" in selector,
                    ANY_ANCESTORS,
                )
                self.assertTrue(
                    bodies,
                    "No compiled rule repaints the success/presence glyph inside %s in %s - the "
                    "presence de-brand did not reach the bundle." % (host, BACKEND_BUNDLE),
                )

                dot_colors = _declared_hexes(bodies, _COLOR_RE)
                self.assertTrue(dot_colors, "%s presence glyph declares no colour." % host)
                self.assertNotIn(
                    BRAND_SECONDARY_PURPLE, dot_colors,
                    "%s presence dot compiled to the brand secondary PURPLE %s (%r); 18.0 painted "
                    "presence in the brand teal." % (host, BRAND_SECONDARY_PURPLE, dot_colors),
                )
                self.assertNotIn(
                    flat_brand_teal, dot_colors,
                    "%s presence dot compiled to the flat brand-identity teal %s (%r), which is "
                    "only 2.33:1 on the white puck the glyph always renders on - below the WCAG "
                    "3:1 non-text floor. It must use the darker CHROME-BASE teal %s."
                    % (host, flat_brand_teal, dot_colors, CHROME_BASE_TEAL),
                )
                self.assertEqual(
                    dot_colors[-1], CHROME_BASE_TEAL,
                    "%s presence dot must compile to the CHROME-BASE AA teal %s; compiled colours "
                    "were %r." % (host, CHROME_BASE_TEAL, dot_colors),
                )
                ratio = _contrast_ratio(
                    self._assert_rgb(dot_colors[-1], "%s presence dot" % host), WHITE_RGB
                )
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NON_TEXT,
                    "%s presence dot (%s) on its white puck is only %.2f:1 - a meaningful non-text "
                    "indicator needs >= %.1f:1 (WCAG 1.4.11)."
                    % (host, dot_colors[-1], ratio, WCAG_AA_NON_TEXT),
                )

    # ------------------------------------------------------------------------------------------
    # 6. Systray unread counters
    # ------------------------------------------------------------------------------------------
    def test_systray_unread_counters_are_readable_on_the_navbar(self):
        """The messaging/activity systray counters must carry an AA-readable count.

        Both badges render inside .o_main_navbar .o_menu_systray, which core paints
        `background-color: var(--o-navbar-badge-bg, #{$o-navbar-badge-bg})` with
        `color: var(--o-navbar-badge-color, ...)`. $o-navbar-badge-bg resolves to the cluster's
        $o-success #00B365, so the pre-fix 11px count rendered at 2.75:1 - RED on the ratio
        assertion below and on the explicit $o-success guard. Only the RULE is asserted for the
        replacement shade (still a green, no longer $o-success, AA against its own foreground):
        the production value is DERIVED - mix(black, $o-success, 28%) - with no named design
        token, so pinning the exact literal would turn a legitimate re-tune into a false alarm.

        R-7 TREATMENT: CONVERTED to cascade resolution. The fill and the count colour are resolved
        from background-color / color on a modelled badge element, through core's own
        `.o_main_navbar .o_menu_systray .badge` consumer, instead of being read back out of our two
        --o-navbar-badge-* declarations. WOULD FAIL IF REVERTED: removing this module's rule hands
        the badge back to $o-navbar-badge-bg ($o-success) and the 2.75:1 ratio assertion reports it;
        a core rename of either token makes the branded value unreachable from that consumer."""
        css = self._compiled_css(BACKEND_BUNDLE)
        # `badge` is what core's navbar consumer keys on, so it is part of the contract this guard
        # rests on - not decoration. A rename there would leave the models below stale.
        self._assert_core_source_contains(
            "mail/static/src/core/web/messaging_menu_patch.xml",
            ("o-mail-MessagingMenu-counter badge rounded-pill",),
            "The messaging systray counter no longer renders as a `.badge`, so core's "
            ".o_menu_systray .badge rule no longer paints it and neither token applies.",
        )
        self._assert_core_source_contains(
            "mail/static/src/core/web/activity_menu.xml",
            ("o-mail-ActivityMenu-counter badge rounded-pill",),
            "The activity systray counter no longer renders as a `.badge`, so core's "
            ".o_menu_systray .badge rule no longer paints it and neither token applies.",
        )
        for counter in (".o-mail-MessagingMenu-counter", ".o-mail-ActivityMenu-counter"):
            with self.subTest(counter=counter):
                bodies = _bodies_matching(css, lambda selector: selector == counter, ANY_ANCESTORS)
                self.assertTrue(
                    bodies,
                    "No compiled rule targets %s in %s - the systray counter a11y override did "
                    "not reach the bundle." % (counter, BACKEND_BUNDLE),
                )

                # The two declarations must exist at all ...
                badge_bgs = _declared_values(bodies, _custom_property_re("o-navbar-badge-bg"))
                badge_colors = _declared_values(bodies, _custom_property_re("o-navbar-badge-color"))
                self.assertTrue(
                    badge_bgs,
                    "%s declares no --o-navbar-badge-bg, so core's $o-navbar-badge-bg ($o-success "
                    "%s) stands and the count renders at 2.75:1." % (counter, CORE_SUCCESS_GREEN),
                )
                self.assertTrue(
                    badge_colors,
                    "%s declares no --o-navbar-badge-color, so the count inherits the navbar's "
                    "near-white entry colour with no contrast guarantee." % counter,
                )

                # ... and - the R-7 hardening - both must still be the tokens the NAVBAR reads.
                # These counters carry no colour of their own: they are painted entirely by
                # `.o_main_navbar .o_menu_systray .badge` (web/.../navbar/navbar.scss:234-240),
                # which is why the fix is a pair of custom properties in the first place. Resolving
                # background-color / color on the real badge element walks that consumer, so a core
                # rename of either token makes the branded value unreachable and this RED - whereas
                # reading our own two declarations back out would stay green with the badge visibly
                # back on $o-success.
                element = {
                    "classes": SYSTRAY_COUNTER_CLASSES[counter], "ancestors": SYSTRAY_ANCESTORS,
                }
                background_value, background_rgb = self._resolve_colour(
                    css, [element], BACKGROUND_PROPS, "%s badge fill" % counter
                )
                foreground_value, foreground_rgb = self._resolve_colour(
                    css, [element], ("color",), "%s count text" % counter
                )
                self.assertNotEqual(
                    background_rgb, _to_rgb(CORE_SUCCESS_GREEN),
                    "%s renders the unmodified $o-success %s (resolved: %s), which only reaches "
                    "2.75:1 under white 11px text."
                    % (counter, CORE_SUCCESS_GREEN, background_value),
                )
                # The badge stays a SUCCESS badge: darkening it must not change its meaning by
                # drifting into another hue (green channel still dominant).
                self.assertGreater(
                    background_rgb[1], max(background_rgb[0], background_rgb[2]),
                    "%s resolves its badge fill to %s, which is no longer a green - the counter is "
                    "a success badge and must keep its semantic hue while darkening."
                    % (counter, background_value),
                )
                ratio = _contrast_ratio(foreground_rgb, background_rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "%s renders its count %s on %s - only %.2f:1, and this 11px systray text needs "
                    ">= %.1f:1."
                    % (counter, foreground_value, background_value, ratio, WCAG_AA_NORMAL_TEXT),
                )

    # ------------------------------------------------------------------------------------------
    # 7. Chat-window header dropdown toggle, hovered / open
    # ------------------------------------------------------------------------------------------
    def test_chat_window_header_dropdown_toggle_stays_white_while_hovered_or_open(self):
        """Hovering or opening the chat-window title dropdown must keep its label white.

        PREVIOUSLY UNGUARDED. v19 renamed this lever: neither `.o-mail-ChatWindow-command` nor
        `--mail-ChatWindow-commandHoverColor` exists anywhere in v19, so the ported 18.0 rule was
        inert. The v19 toggle is `.o-mail-ChatWindow-moreActions` and core paints its hovered/open
        state `color: var(--mail-ChatWindow-moreActionsHoverColor, black) !important`
        (mail/static/src/core/common/chat_window.scss:18-22) - a BLACK default, which is what
        renders on the teal chrome when this module's declaration is missing or orphaned. That
        default is the reason this surface needs a guard at all: unlike an unresolved var(), a
        working fallback fails SILENTLY and looks deliberate.

        PROTECTS AGAINST: (a) dropping `--mail-ChatWindow-moreActionsHoverColor: white` from
        .o-mail-ChatWindow-header, which drops the label to black on teal = 2.14:1; (b) core
        renaming the property, which orphans our declaration and restores that same black.

        Resolved through core's own consumer: `color` is resolved on a modelled HOVERED toggle, and
        the custom property is then looked up outwards along the chain - the toggle itself, then the
        header that declares it - exactly as inheritance carries it in a browser. The header's own
        fill is resolved the same way, so the ratio is measured between two computed values rather
        than between two literals."""
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
            "the teal header chrome, so this module must keep feeding that property white."
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

    # ------------------------------------------------------------------------------------------
    # 8. Discuss unread badge
    # ------------------------------------------------------------------------------------------
    def test_discuss_unread_badge_renders_the_brand_purple_through_cores_own_consumer(self):
        """A Discuss unread counter must render the brand purple, not core's $o-success green.

        PREVIOUSLY UNGUARDED. Core paints every `.o-discuss-badge` with
        `background-color: var(--o-discuss-badge-bg) !important` and defaults that token to
        $o-success (mail/static/src/core/common/core.scss:33-37, with the comment "sync with
        --o-navbar-badge-bg"). This module re-points the token to the brand SECONDARY purple. The
        `!important` on core's consumer is why the fix has to be a custom property rather than a
        plain background-color declaration, and therefore why a rename of that property silently
        reverts the badge to green with our declaration still sitting in the bundle.

        PROTECTS AGAINST: (a) dropping this module's core.scss override - core's own (0,1,0)
        declaration is then the last writer and the badge goes green; (b) core renaming
        --o-discuss-badge-bg, which orphans ours and does the same thing invisibly.

        Core keeps its own foreground here (`color: white !important`, same rule), so the contrast
        assertion is the honest observable for the pair rather than a value this module chose.

        MODELLED ON THE SIDEBAR COUNTER ON PURPOSE. Two other `.o-discuss-badge` render sites are
        DELIBERATELY overridden by core at higher specificity and must keep winning - a
        NotificationItem badge that is not `.o-important` is pinned $gray-500, and the messaging
        menu's tab-unread dot is pinned transparent. A test that asserted purple for those would be
        WRONG; see DISCUSS_UNREAD_BADGE_CLASSES for the full exclusion list.

        >>> OWNER REVISION 2026-08-03: LIGHT keeps the purple, DARK MUST NOT HAVE IT. <<<
        The dark arm added here is RED-BEFORE-GREEN against a defect that was SHIPPING and unguarded:
        the previous pass gave $o-brand-secondary a dark arm (#B589B8) and this badge followed it, so
        core's forced `color: white !important` measured 2.90:1 in the dark bundle. Removing the
        purple from dark is not on its own enough either - letting the token simply recompile lands
        the badge on the neutral muted tier #8EA5A8, where white is 2.59:1, WORSE. So the dark arm has
        to be stated, and it is stated as the shade the cluster already uses for exactly this job:
        the AA-corrected $o-success the systray counters carry. The assertions are therefore
        scheme-split - purple in light, NOT purple and NOT the muted tier in dark - with the SAME
        measured-contrast rule applied to both, because that rule is the actual behaviour."""
        for arm, bundle_name in (("light", BACKEND_BUNDLE), ("dark", DARK_BUNDLE)):
            css = self._compiled_css(bundle_name)
            self._assert_core_source_contains(
                "mail/static/src/discuss/core/public_web/discuss_sidebar_categories.xml",
                ("badge rounded-pill o-discuss-badge fw-bold",),
                "The Discuss sidebar unread counter no longer carries `o-discuss-badge`, so neither "
                "core's consumer nor this module's token reaches it and the model below is stale.",
            )
            badge = {
                "classes": DISCUSS_UNREAD_BADGE_CLASSES, "ancestors": DISCUSS_SIDEBAR_ANCESTORS,
            }

            fill_value, fill_rgb = self._resolve_colour(
                css, [badge], BACKGROUND_PROPS,
                "Discuss sidebar unread badge fill (%s arm)" % arm,
            )
            if arm == "light":
                self.assertNotEqual(
                    fill_rgb, _to_rgb(CORE_SUCCESS_GREEN),
                    "The Discuss unread badge resolves to core's untouched $o-success %s (resolved: "
                    "%s) - the brand override on --o-discuss-badge-bg is not reaching it."
                    % (CORE_SUCCESS_GREEN, fill_value),
                )
                self.assertEqual(
                    fill_rgb, _to_rgb(BRAND_SECONDARY_PURPLE),
                    "The Discuss unread badge must resolve to the brand SECONDARY purple %s on the "
                    "LIGHT bundle; it resolved to %s." % (BRAND_SECONDARY_PURPLE, fill_value),
                )
            else:
                self.assertNotEqual(
                    fill_rgb, _to_rgb(BRAND_SECONDARY_PURPLE),
                    "The Discuss unread badge compiled the brand purple %s in the DARK bundle. The "
                    "purple accent is light-only from 2026-08-03." % BRAND_SECONDARY_PURPLE,
                )
                self.assertNotEqual(
                    fill_rgb, _to_rgb(RETIRED_DARK_PURPLE),
                    "The Discuss unread badge compiled the RETIRED dark purple %s. Core forces a "
                    "white label on this badge, which measures only 2.90:1 there - that is the exact "
                    "AA failure removing the dark arm was meant to end." % RETIRED_DARK_PURPLE,
                )
                self.assertNotEqual(
                    fill_rgb, _to_rgb(DARK_MUTED_TIER),
                    "The Discuss unread badge compiled the neutral muted tier %s in the dark bundle "
                    "- i.e. it was allowed to follow $o-brand-secondary's dark re-point instead of "
                    "getting its own arm. White on it is 2.59:1, and a grey unread counter reads as "
                    "'already read'." % DARK_MUTED_TIER,
                )

            count_value, count_rgb = self._resolve_colour(
                css, [badge], ("color",),
                "Discuss sidebar unread badge count (%s arm)" % arm,
            )
            ratio = _contrast_ratio(count_rgb, fill_rgb)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "The Discuss unread count (%s on %s, %s arm) is only %.2f:1 - this is small bold "
                "text and needs >= %.1f:1."
                % (count_value, fill_value, arm, ratio, WCAG_AA_NORMAL_TEXT),
            )

    # ------------------------------------------------------------------------------------------
    # 9. "Seen by everyone" tick
    # ------------------------------------------------------------------------------------------
    def test_seen_by_everyone_tick_clears_the_non_text_floor_as_composited(self):
        """The "seen by everyone" tick must stay legible AS RENDERED - colour AND opacity together.

        PREVIOUSLY UNGUARDED, and the whole 18.0 rule was inert on v19: it targeted
        `.o-all-seen.text-primary` and NEITHER class exists in v19. Core now renders
        `o-mail-MessageSeenIndicator ... o-hasEveryoneSeen opacity-75`
        (mail/static/src/discuss/core/common/message_seen_indicator.xml:4) and paints it
        `color: var(--mail-MessageSeenIndicator-hasEveryoneSeenColor, lighten($primary, 20%))`
        (mail/static/src/discuss/core/common/message_seen_indicator.scss:2-3), so the tick rendered
        100% core Odoo until this module started feeding that custom property.

        THE OPACITY IS PART OF THE RULE, NOT A DETAIL. Core stacks `opacity-75` on the same span, so
        the pixel a user sees is the 75%-composite over the message-list surface, not the declared
        colour: the AA teal #007F8E measures 4.74:1 raw but ~3.11:1 composited, and 18.0's flat
        #00BBCE would have blended to ~1.93:1 - i.e. a raw-colour assertion would have PASSED the
        very value that fails on screen. The rule is therefore stated on the composited value
        against the WCAG 1.4.11 non-text floor, and the opacity is READ from the compiled bundle
        (Bootstrap's `.opacity-75` utility) rather than hardcoded, so a core change to the dimming
        is caught too.

        PROTECTS AGAINST: (a) reverting the tick to the flat identity teal; (b) core renaming
        --mail-MessageSeenIndicator-hasEveryoneSeenColor, which orphans our declaration and restores
        core's `lighten($primary, 20%)`; (c) core deepening the dimming past the point where the
        branded teal still clears 3:1.

        SURFACE MODELLED AS WHITE. The tick renders inside the message list, whose background is
        $o-view-background-color (plain white). That is a modelled surface, stated here rather than
        resolved, because the message list's background is painted by an ancestor chain this
        class-based resolver does not walk."""
        self._require_cascade_resolver()
        css = self._compiled_css(BACKEND_BUNDLE)
        # Both conditional classes are the contract this guard rests on: `o-hasEveryoneSeen` is
        # what core's colour rule keys on, `opacity-75` is what makes the composited value the real
        # one. The 18.0 rule died exactly this way - it targeted classes v19 stopped rendering.
        self._assert_core_source_contains(
            "mail/static/src/discuss/core/common/message_seen_indicator.xml",
            ("o-hasEveryoneSeen opacity-75",),
            "Core no longer marks the fully-seen tick with those classes, so this module's custom "
            "property is fed to an element that no longer exists - the same failure mode that left "
            "the 18.0 `.o-all-seen.text-primary` rule silently inert on v19.",
        )
        indicator = {
            "classes": MESSAGE_SEEN_EVERYONE_CLASSES, "ancestors": MESSAGE_SEEN_ANCESTORS,
        }

        tick_value, tick_rgb = self._resolve_colour(
            css, [indicator], ("color",), "seen-by-everyone tick"
        )
        self.assertEqual(
            tick_rgb, _to_rgb(CHROME_BASE_TEAL),
            "The seen-by-everyone tick resolves to %s; it must resolve to the CHROME-BASE AA teal "
            "%s fed through core's own --mail-MessageSeenIndicator-hasEveryoneSeenColor."
            % (tick_value, CHROME_BASE_TEAL),
        )

        # Read the dimming core actually applies to this element instead of assuming 75%.
        dimming = _winning_declaration(css, indicator, ("opacity",))
        self.assertIsNotNone(
            dimming,
            "No compiled `opacity` declaration applies to the seen-by-everyone tick, but core "
            "stamps `opacity-75` on it. Either that utility is no longer generated or the class "
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
            "1.4.11). The flat identity teal blends to ~1.93:1 here, which is exactly why the "
            "raw colour alone is not the rule."
            % (tick_value, dimming, composited, ratio, WCAG_AA_NON_TEXT),
        )

    # ------------------------------------------------------------------------------------------
    # 10. Idle / away presence glyph - the three-site desync guard
    # ------------------------------------------------------------------------------------------
    def test_idle_presence_glyph_resolves_to_one_amber_at_all_three_render_sites(self):
        """Every idle/away glyph must resolve to the SAME amber, wherever v19 renders it.

        PREVIOUSLY UNGUARDED. v19 renamed the class - 18.0 rendered `fa fa-circle o-away`, v19
        renders `fa fa-circle o-yellow` (mail/static/src/core/common/im_status.xml:19) - so the
        forward-ported `.o-away` rule was inert and idle fell back to core's
        `.o-yellow { color: $yellow }` (#ffc107, 1.63:1 on the white puck).

        THE DESYNC IS THE BUG THIS TEST EXISTS FOR. THREE separate rules render the same state:
        the ImStatus dot, the same dot reached through ThreadIcon's nested <ImStatus> (which wins
        outright through a pre-existing `!important`, so leaving it behind silently defeats the fix
        everywhere a ThreadIcon is on screen), and the "Away" swatch in the status picker - a picker
        that must match the dot it produces. Production keeps them in step through ONE Sass
        variable; this test asserts the OUTCOME of that, by resolving all three through the cascade
        and requiring one identical value. Resolving also pits each rule against core's `.o-yellow`,
        so a rule that stops matching is reported rather than assumed.

        THE VALUE IS PINNED, NOT RE-DERIVED. #b27400 is asserted as a literal design constant; the
        test never recomputes darken(#ffa500, 15%), which would re-implement the production
        expression and compare it against itself. The two values it must NOT be are asserted
        explicitly, because both are plausible "restores" a future reader might attempt: 18.0's
        #ffa500 and the superseded intermediate #cc8400."""
        css = self._compiled_css(BACKEND_BUNDLE)

        # The class contract these three rules key on must still be the one core renders.
        self._assert_core_source_contains(
            "mail/static/src/core/common/im_status.xml",
            ("o-yellow",),
            "Core no longer renders the idle glyph with that class, so all three of this module's "
            "`.o-yellow` rules are inert and idle has fallen back to core's #ffc107.",
        )
        self._assert_core_source_contains(
            "mail/static/src/core/common/im_status_dropdown.xml",
            ("o-mail-ImStatusDropdown", "o-yellow"),
            "The status picker no longer carries that menu class or that swatch class, so the "
            "picker swatch has drifted away from the dot it selects.",
        )

        sites = (
            ("ImStatus presence dot", IDLE_GLYPH_CLASSES, IM_STATUS_ANCESTORS),
            ("ThreadIcon presence dot", IDLE_GLYPH_CLASSES, THREAD_ICON_ANCESTORS),
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
                    "module's rule for that site is not matching in v19." % (label, CORE_YELLOW, value),
                )
                self.assertNotEqual(
                    rgb, _to_rgb(LEGACY_AWAY_ORANGE),
                    "The %s resolves to 18.0's flat orange %s, which is only 1.97:1 on the white "
                    "puck. Idle was deliberately darkened for AA - do NOT restore the 18.0 value."
                    % (label, LEGACY_AWAY_ORANGE),
                )
                self.assertNotEqual(
                    rgb, _to_rgb(SUPERSEDED_AWAY_AMBER),
                    "The %s resolves to the superseded intermediate amber %s, which fails the "
                    "focused dropdown row. The shipped value is %s."
                    % (label, SUPERSEDED_AWAY_AMBER, AWAY_AMBER),
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
            "The idle glyph resolves to MORE THAN ONE colour across its three render sites (%r). "
            "The status picker would no longer match the dot it produces - which is precisely the "
            "desync the single $o-viin-mail-status-away-color variable exists to prevent."
            % ({label: value for label, (value, _rgb) in resolved.items()},),
        )

    def test_idle_presence_amber_clears_the_non_text_floor_on_every_surface_it_sits_on(self):
        """The idle amber must clear 3:1 against each real background it renders against.

        A meaningful status indicator is non-text content, so WCAG 1.4.11 sets the floor at 3:1.
        The glyph renders on THREE different surfaces and the darkest of them is the binding
        constraint - which is why the shipped value is darker than any single surface would demand:
          * the ImStatus puck, plain white - core stamps `bg-white bg-opacity-100` on the ImStatus
            root, so the dot sits on white even inside the teal chat-window header;
          * the status-picker menu, $dropdown-bg -> $body-bg -> $o-gray-100 = #f8f9fa;
          * the focused/hovered picker row, $dropdown-link-hover-bg = rgba($black, 0.08) - a
            TRANSLUCENT wash, so the row is that 8% black composited over the #f8f9fa menu = #e4e5e6.

        THE RATIOS ARE COMPUTED, THE COLOURS ARE PINNED. The amber is the literal design constant
        (its link to production is the resolution test above, which reads it out of the compiled
        bundle); the ratios come from the W3C WCAG 2.x formula, an EXTERNAL standard, so this can
        never degenerate into comparing production logic against itself. The three surfaces are
        MODELLED values, so their provenance is re-asserted against core's own source first: if core
        re-themes the webclient background or changes the hover wash, this goes RED and the surfaces
        get re-grounded instead of the guard quietly measuring against a background that no longer
        exists."""
        # Provenance of the two dropdown surfaces, re-read from core rather than trusted.
        self._assert_core_source_contains(
            "web/static/src/scss/primary_variables.scss",
            ("$o-gray-100: #f8f9fa",),
            "The backend grey ramp moved, so the status-picker menu is no longer %s."
            % DROPDOWN_MENU_SURFACE,
        )
        self._assert_core_source_contains(
            "web/static/src/scss/secondary_variables.scss",
            ("$o-webclient-background-color: $o-gray-100",),
            "The webclient background no longer resolves to the grey ramp, so $body-bg - and with "
            "it the dropdown menu surface - has moved.",
        )
        self._assert_core_source_contains(
            "web/static/src/scss/bootstrap_overridden.scss",
            ("$body-bg: $o-webclient-background-color", "$dropdown-link-hover-bg: rgba($black, 0.08)"),
            "The dropdown hover wash or the body background changed, so the focused picker row is "
            "no longer %s." % DROPDOWN_ROW_FOCUS_SURFACE,
        )
        self._assert_core_source_contains(
            "mail/static/src/core/common/im_status.xml",
            ("bg-white bg-opacity-100",),
            "The ImStatus root no longer forces a white puck, so the presence dot's background is "
            "whatever is behind it - including the teal chat-window header, against which this "
            "amber has never been measured.",
        )

        amber_rgb = _to_rgb(AWAY_AMBER)
        self.assertIsNotNone(amber_rgb, "AWAY_AMBER must be a plain hex colour.")
        surfaces = (
            ("ImStatus white puck", IM_STATUS_PUCK_SURFACE),
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

        # Idle must stay DISTINGUISHABLE from online: `text-success` paints online/bot in the
        # CHROME-BASE teal, so an idle glyph that drifted onto the teal ladder would make the two
        # presence states indistinguishable - a legibility fix that destroys the semantic.
        self.assertNotEqual(
            amber_rgb, _to_rgb(CHROME_BASE_TEAL),
            "The idle glyph resolves to the same %s as the online/bot glyph - the two presence "
            "states would be indistinguishable." % CHROME_BASE_TEAL,
        )

    # ------------------------------------------------------------------------------------------
    # 11. Bundle health
    # ------------------------------------------------------------------------------------------
    def test_module_scss_compiles_without_errors_in_every_bundle_it_is_served_in(self):
        """Every bundle that actually compiles this module's SCSS must build with ZERO errors.

        An undefined variable, a Sass function banned in this cluster, or a dangling `after`
        anchor makes AssetsBundle fill css_errors and ship a "css error" stylesheet instead of the
        real one - the whole backend then renders unstyled. Both symptoms are asserted, because
        `.css()` returns a CACHED attachment without repopulating css_errors: a bundle that failed
        on an earlier compile is caught by the error marker baked into that cached payload.

        im_livechat.assets_embed_core is checked through its compiled parent
        im_livechat.assets_embed_external - see the LIVECHAT_EMBED_* constants for why the core
        bundle has no standalone compile. Its wiring is asserted separately by the manifest guard,
        so the third bundle is protected without a permanently-red oracle."""
        bundle_names = [BACKEND_BUNDLE, MAIL_PUBLIC_BUNDLE]
        livechat = self.env["ir.module.module"].search([("name", "=", "im_livechat")], limit=1)
        if livechat.state == "installed":
            bundle_names.append(LIVECHAT_EMBED_COMPILED_BUNDLE)

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

    def test_debrand_scss_is_wired_into_every_bundle_the_branded_surfaces_render_in(self):
        """The de-brand sources must stay injected into every bundle the manifest declares them in.

        The chat-window, presence and composer overrides have to travel with mail wherever it
        renders - backend, the public discuss pages and the livechat embed - or the same surfaces
        go back to core purple/low-contrast outside the backend, where no compiled-CSS assertion
        above would see it. Read straight from the module's own __manifest__.py so the wiring is
        protected even when im_livechat is not installed on the test database."""
        with open(MANIFEST, "r", encoding="utf-8") as manifest_file:
            assets = ast.literal_eval(manifest_file.read()).get("assets", {})

        for bundle_name in (BACKEND_BUNDLE, MAIL_PUBLIC_BUNDLE, LIVECHAT_EMBED_CORE_BUNDLE):
            injected = _injected_sources(assets, bundle_name)
            for source in SHARED_DEBRAND_SOURCES:
                with self.subTest(bundle=bundle_name, source=source):
                    self.assertIn(
                        source, injected,
                        "%s is not injected into %s; the branded mail surfaces it restores would "
                        "render in core colours there." % (source, bundle_name),
                    )

        backend_injected = _injected_sources(assets, BACKEND_BUNDLE)
        self.assertIn(
            SYSTRAY_DEBRAND_SOURCE, backend_injected,
            "%s is not injected into %s; the systray counter contrast override only applies to "
            "backend navbar chrome and has nowhere else to live."
            % (SYSTRAY_DEBRAND_SOURCE, BACKEND_BUNDLE),
        )

    # ==============================================================================================
    # 12. Dark mode - mail-owned surfaces the recompiled dark palette (C-2) cannot reach (M-1)
    # ==============================================================================================
    # viin_brand_web/dark_palette.scss recompiles web.assets_web_dark with the surface / text /
    # border Sass vars redefined to dark values, so every mail surface that reads an OVERRIDABLE Sass
    # var (e.g. the chatter thread -> $o-view-background-color -> #111B1E) recompiles dark-correct for
    # free - NO rule is added here for those. The two surfaces below are the exception core `mail`
    # sculpts from LITERALS no overridable var reaches, so they do NOT flip and this module adds an
    # explicit dark residue. Each is asserted against the COMPILED dark bundle - the real observable -
    # against the FIXED WCAG AA threshold (>= 4.5:1), never the code's own computed output, and never
    # a hex snapshot: a later re-tune that still clears AA on the dark surface is not a false alarm.

    def _root_token(self, css, token, bundle_name, label):
        """Return the value core's Bootstrap ``_root.scss`` emits for ``:root --<token>`` in ``css``.

        Odoo sets ``$variable-prefix: ''`` (bootstrap_overridden.scss), so ``_root.scss`` emits
        ``--<token>`` (no ``bs-`` prefix) from the scheme's Sass var. This reads core's OWN
        :root emission - NOT this module's declaration - so if core renamed the token, this module's
        ``var(--<token>)`` reference is orphaned, nothing is found, and the guard goes RED instead of
        measuring a stale value (the R-7 discipline the rest of this file follows).

        Scheme-neutral: both bundles emit their own :root block, so the only thing that differs
        between light and dark is which compiled CSS is handed in."""
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
        """Resolve a compiled colour that is either a bare literal or a ``var(--token[, fallback])``.

        A custom-property lookup is followed through core's own :root emission of that token
        (:meth:`_root_token`); a plain literal is returned as-is. Returns ``(raw_value, rgb)``."""
        match = _VAR_REF_RE.fullmatch(value.strip())
        if match:
            value = self._root_token(css, match.group(1), bundle_name, label)
        return value, self._assert_rgb(value, label)

    def _resolve_dark_colour(self, css, value, label):
        """The dark-bundle reading of :meth:`_resolve_scheme_colour`."""
        return self._resolve_scheme_colour(css, value, DARK_BUNDLE, label)

    def test_dark_rotting_kanban_card_stays_a_readable_solid_danger_surface(self):
        """The overdue/rotting kanban card must paint a SOLID red danger tint readable under text.

        Core mail/static/src/scss/rotting_mixin.scss paints
        `.o_kanban_record.oe_kanban_card_rotting { background-color: rgba(255, 201, 201, .3) }` - a
        TRANSLUCENT light-pink LITERAL that no overridable Sass var reaches, so the C-2 dark recompile
        cannot flip it. Over the #111B1E dark card that 30% pink composites to a muddy near-neutral
        and loses the "overdue / danger" read. This module re-points it to `mix($danger, $body-bg,
        25%)`, a SOLID danger tint the recompile evaluates at compile time against the dark $body-bg.

        THE DEFECT IS THE TRANSLUCENCY, so the rule is stated on it: the winning dark background must
        be OPAQUE (a translucent wash over the dark card IS the muddy-neutral failure), must stay
        red-DOMINANT (the danger signal is chromatic - the fix darkens toward the panel, so a
        luminance-contrast measure would not capture it), and the dark body text must clear WCAG AA on
        it. The higher-specificity `.o_record_selected` state is deliberately excluded - it keeps the
        core selection highlight and is not this surface. WOULD FAIL IF REVERTED: drop this module's
        rule and core's `rgba(...,.3)` is the last writer, so the opacity assertion reports the
        translucent wash. Same-specificity (0,3,0) selector, later source order wins, so the
        assertions read the LAST-declared background."""
        css = self._compiled_css(DARK_BUNDLE)
        bodies = _bodies_matching(
            css,
            lambda selector: ".oe_kanban_card_rotting" in _selector_subject(selector)
            and ".o_record_selected" not in _selector_subject(selector), ANY_ANCESTORS,
        )
        self.assertTrue(
            bodies,
            "No compiled rule styles the base .oe_kanban_card_rotting card in %s - core's own "
            "rotting_mixin.scss is included via web.assets_web, so an empty match means the dark "
            "bundle did not build." % DARK_BUNDLE,
        )
        backgrounds = _declared_values(bodies, _BACKGROUND_RE)
        self.assertTrue(
            backgrounds,
            "The rotting card declares no background in %s; its danger surface cannot be verified."
            % DARK_BUNDLE,
        )
        winning = backgrounds[-1]

        # 1. OPAQUE - a translucent light wash over the dark card is the muddy-neutral defect itself.
        alpha_match = _RGBA_ALPHA_RE.search(winning)
        if alpha_match is not None:
            alpha = _to_alpha(alpha_match.group(1))
            self.assertIsNotNone(
                alpha, "The rotting card background %r has an unparseable alpha." % winning,
            )
            self.assertGreaterEqual(
                alpha, 1.0,
                "The dark rotting card compiled to the TRANSLUCENT %s - core's untouched "
                "rgba(255,201,201,.3) literal, which composites to a muddy near-neutral over the "
                "#111B1E card and loses the danger read. It must be a SOLID danger tint." % winning,
            )
        card_rgb = self._assert_rgb(winning, "dark rotting card background")

        # 2. STILL READS DANGER - red channel dominant (the signal is chromatic, not luminance).
        self.assertTrue(
            card_rgb[0] > card_rgb[1] and card_rgb[0] > card_rgb[2],
            "The dark rotting card compiled to %s (rgb%r), whose red channel is not dominant - it no "
            "longer reads as an overdue/danger card." % (winning, card_rgb),
        )

        # 3. READABLE - the dark body text core paints on kanban cards clears WCAG AA on the tint.
        body_text = self._dark_root_token(css, "body-color", "dark kanban card body text")
        text_rgb = self._assert_rgb(body_text, "dark body text")
        ratio = _contrast_ratio(text_rgb, card_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The dark rotting card text (%s) on its danger tint (%s) is only %.2f:1 - WCAG AA normal "
            "text needs >= %.1f:1." % (body_text, winning, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_chatter_message_date_muted_timestamp_clears_aa_on_the_dark_thread(self):
        """The chatter message timestamp must stay a READABLE muted grey on the dark thread.

        Core mail/static/src/core/common/message.scss:21-22 sets `.o-mail-Message-date { color:
        $text-muted }`, and Odoo maps $text-muted -> $o-main-color-muted = rgba($o-gray-700,
        $o-opacity-muted) = rgba(#495057, .76) (bootstrap_overridden.scss, primary_variables.scss:121).
        $o-gray-700 is NOT flipped by the dark recompile, so on the #111B1E thread this compiles to a
        translucent DARK grey reading only ~2.1:1 - below AA. This module re-points it to the dark
        muted-text token --secondary-color, which Bootstrap _root.scss emits from the dark
        $body-secondary-color = #8EA5A8 (6.75:1 on #111B1E).

        Resolved through core's OWN :root emission of --secondary-color (a rename orphans this
        module's reference and this goes RED), against the dark thread surface which the recompile
        drives both $body-bg and $o-view-background-color to (dark_palette.scss:45-46). Same
        specificity as core, later source order wins, so the LAST-declared colour is read."""
        css = self._compiled_css(DARK_BUNDLE)
        bodies = _bodies_matching(
            css,
            lambda selector: _selector_subject(selector) == ".o-mail-Message-date",
            ANY_ANCESTORS,
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
            "is normal muted text and needs >= %.1f:1. Core's untouched $text-muted resolves to "
            "rgba(#495057,.76) here at ~2.1:1."
            % (date_value, surface_value, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_surface_residue_is_wired_into_the_dark_bundle(self):
        """The mail-owned dark residue must stay explicitly contributed to web.assets_web_dark.

        Core's dark tail glob is web/mail-only (never this module), so mail_dark.scss reaches the dark
        bundle ONLY through this manifest entry. If it is dropped, both surfaces above silently revert
        to their core dark values - a translucent muddy rotting card and a ~2.1:1 timestamp. Read
        straight from the module's own __manifest__.py so the wiring is protected structurally, even
        on a database where the dark bundle is not compiled by another test."""
        with open(MANIFEST, "r", encoding="utf-8") as manifest_file:
            assets = ast.literal_eval(manifest_file.read()).get("assets", {})
        injected = _injected_sources(assets, DARK_BUNDLE)
        self.assertIn(
            DARK_SURFACE_SOURCE, injected,
            "%s is not injected into %s; the mail-owned dark surfaces it restores would render in "
            "core's un-flipped dark values." % (DARK_SURFACE_SOURCE, DARK_BUNDLE),
        )

    # ==============================================================================================
    # 13. Dark mode - Discuss app surfaces (owner-directed, PR #658)
    # ==============================================================================================
    # The C-2 recompile flips every Discuss surface that reads an OVERRIDABLE Sass var ($body-bg /
    # $o-view-background-color / $border-color / $body-color) for free - so the resting sidebar
    # surface, the conversation header, the thread message body and the composer are dark-correct with
    # NO rule added. The surfaces below are the exception: core `mail` sculpts them from the raw
    # Bootstrap grayscale ramp ($gray-100..500 / $white) that dark_palette.scss does NOT flip - in
    # BOTH its light *.scss (recompiled early in the web.assets_web include) AND its own *.dark.scss
    # tail - so they stayed LIGHT in dark, rendering the near-white $body-color text on a near-white
    # surface. Each guard measures the WCAG 2.x ratio of the COMPILED dark colours against the FIXED
    # AA threshold (never a hex snapshot, never the code's own computed output), so a later re-tune
    # that still clears AA is not a false alarm and a regression back to a light literal is caught.

    def test_dark_discuss_sidebar_border_is_scheme_aware_not_a_fixed_light_gray(self):
        """The Discuss sidebar divider must be the scheme-aware --border-color, not the light $gray-500.

        viin_brand_mail/static/src/core/web/discuss_sidebar.scss pinned
        `.o-mail-DiscussSidebar { border-right-color: $gray-500 !important }` - a compile-time light
        gray (#adb5bd) that never flips, so in dark the sidebar edge rendered as a "white" line on the
        dark app. Re-pointed to `var(--border-color)`, which core's Bootstrap _root.scss emits at
        :root from the recompiled dark $border-color = #25383C. Resolved THROUGH that :root emission
        (a core rename orphans the reference and this goes RED), and the old light gray is refused
        explicitly. WOULD FAIL IF REVERTED: the literal $gray-500 #adb5bd is neither var(--border-color)
        nor the dark #25383C."""
        css = self._compiled_css(DARK_BUNDLE)
        bodies = _bodies_matching(
            css,
            lambda selector: _selector_subject(selector) == ".o-mail-DiscussSidebar",
            ANY_ANCESTORS,
        )
        self.assertTrue(
            bodies,
            "No compiled rule styles the .o-mail-DiscussSidebar element in %s - the sidebar border "
            "override did not reach the bundle." % DARK_BUNDLE,
        )
        borders = _declared_values(bodies, _BORDER_COLOR_RE)
        self.assertTrue(
            borders,
            "The .o-mail-DiscussSidebar element declares no border colour in %s." % DARK_BUNDLE,
        )
        winning = borders[-1]
        self.assertNotIn(
            "#adb5bd", winning,
            "The Discuss sidebar border compiled to the fixed light gray $gray-500 (#adb5bd) in %s - "
            "it never flips, so the sidebar edge is a white line on the dark app. It must be the "
            "scheme-aware var(--border-color)." % DARK_BUNDLE,
        )
        border_value, border_rgb = self._resolve_dark_colour(css, winning, "dark sidebar border")
        self.assertEqual(
            border_rgb, self._assert_rgb("#25383c", "dark --border-color"),
            "The Discuss sidebar border resolves to %s; it must resolve to the recompiled dark "
            "--border-color #25383C, not a light gray." % border_value,
        )

    def test_dark_discuss_sidebar_channel_name_stays_readable_at_rest_hover_and_active(self):
        """Channel names must clear WCAG AA on the dark sidebar - resting, hovered AND on the open item.

        The name span (.o-mail-DiscussSidebarChannel-itemName) carries no colour of its own (btn
        text-reset -> inherited $body-color = the recompiled dark near-white #EDF4F5). What broke
        readability is the ITEM surface under it: core.dark.scss makes the RESTING sidebar dark, but
        the item HOVER (discuss_sidebar.scss:44-46, `mix($gray-100, $gray-200)`) and the ACTIVE item
        (discuss_sidebar.dark.scss:2-3, `mix($gray-200, $gray-300)`) both stayed a near-white gray, so
        the hovered row and the currently-open channel rendered near-white names on a near-white item.
        This module re-points the hover onto a raised dark neutral and restores the active token to the
        action-tinted dark surface the light rule's own fallback already intends. Each of the three
        surfaces is measured against the inherited name colour at the fixed AA threshold; a regression
        back to a light literal drops the ratio below 4.5 and this goes RED."""
        css = self._compiled_css(DARK_BUNDLE)
        name_rgb = self._assert_rgb(
            self._dark_root_token(css, "body-color", "dark sidebar channel name"),
            "dark sidebar channel name",
        )

        surfaces = []  # (label, resolved surface rgb) for the three item states the name renders on

        rest_bodies = _bodies_matching(
            css,
            lambda selector: _selector_subject(selector) == ".o-mail-discussSidebarBgColor",
            ANY_ANCESTORS,
        )
        rest_bgs = _declared_values(rest_bodies, _BACKGROUND_RE)
        self.assertTrue(
            rest_bgs,
            "No compiled .o-mail-discussSidebarBgColor background in %s - core's own core.dark.scss "
            "is in the bundle, so an empty match means the dark bundle did not build." % DARK_BUNDLE,
        )
        surfaces.append(
            ("resting sidebar", self._resolve_dark_colour(css, rest_bgs[-1], "resting sidebar")[1])
        )

        hover_bodies = _bodies_matching(
            css,
            lambda selector: _selector_subject(selector) == ".o-mail-DiscussSidebar-item:hover",
            ANY_ANCESTORS,
        )
        hover_bgs = _declared_values(hover_bodies, _BACKGROUND_RE)
        self.assertTrue(
            hover_bgs,
            "No compiled .o-mail-DiscussSidebar-item:hover background in %s - the sidebar item hover "
            "de-light did not reach the dark bundle." % DARK_BUNDLE,
        )
        surfaces.append(
            ("hovered sidebar item",
             self._resolve_dark_colour(css, hover_bgs[-1], "hovered sidebar item")[1])
        )

        active_bodies = _bodies_matching(
            css,
            lambda selector: _selector_subject(selector) == ".o-mail-DiscussSidebar-item",
            ANY_ANCESTORS,
        )
        active_tokens = _declared_values(
            active_bodies, _custom_property_re("mail-DiscussSidebar-itemActiveBgColor")
        )
        self.assertTrue(
            active_tokens,
            "No compiled --mail-DiscussSidebar-itemActiveBgColor on .o-mail-DiscussSidebar-item in %s "
            "- the active-item de-light did not reach the dark bundle." % DARK_BUNDLE,
        )
        surfaces.append(
            ("active sidebar item",
             self._resolve_dark_colour(css, active_tokens[-1], "active sidebar item")[1])
        )

        for label, surface_rgb in surfaces:
            with self.subTest(surface=label):
                ratio = _contrast_ratio(name_rgb, surface_rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "The Discuss channel name (dark $body-color) on the %s (rgb%r) is only %.2f:1 - "
                    "WCAG AA normal text needs >= %.1f:1. Core paints this surface from the un-flipped "
                    "$gray ramp, so a missing override leaves it near-white."
                    % (label, surface_rgb, ratio, WCAG_AA_NORMAL_TEXT),
                )

    def test_dark_discuss_thread_message_body_clears_aa_on_the_dark_thread(self):
        """A Discuss thread message body must stay readable on the dark thread surface.

        The message body carries no colour of its own - it inherits the recompiled dark $body-color
        (#EDF4F5), and the thread canvas is `.o-mail-DiscussContent-core { background-color: $body-bg }`
        (discuss_content.scss:7-9), flipped to #111B1E by dark_palette.scss - so this pair recompiles
        dark-correct for free and NO override is added for it (a dead override would be the wrong fix).
        This guard confirms the free flip holds: if the dark palette's text token or the thread canvas
        surface ever regressed to a light value, the body text would stop clearing AA and this goes
        RED. The surface is resolved from the real mail canvas rule (not a bare :root token), the text
        through core's own :root emission of $body-color, measured at the fixed AA threshold."""
        css = self._compiled_css(DARK_BUNDLE)
        body_text = self._assert_rgb(
            self._dark_root_token(css, "body-color", "dark thread message body"),
            "dark thread message body",
        )
        canvas_bodies = _bodies_matching(
            css,
            lambda selector: _selector_subject(selector) == ".o-mail-DiscussContent-core",
            ANY_ANCESTORS,
        )
        canvas_bgs = _declared_values(canvas_bodies, _BACKGROUND_RE)
        self.assertTrue(
            canvas_bgs,
            "No compiled .o-mail-DiscussContent-core background in %s - core's own discuss_content.scss "
            "is in the bundle, so an empty match means the dark bundle did not build." % DARK_BUNDLE,
        )
        surface_value, surface_rgb = self._resolve_dark_colour(
            css, canvas_bgs[-1], "dark thread canvas"
        )
        ratio = _contrast_ratio(body_text, surface_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The Discuss thread message body (dark $body-color) on the dark thread canvas (%s) is only "
            "%.2f:1 - WCAG AA normal text needs >= %.1f:1."
            % (surface_value, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_discuss_messaging_menu_panel_is_a_readable_dark_surface(self):
        """The messaging-menu / systray dropdown panel must be a dark surface its text can be read on.

        core/public_web/messaging_menu.scss fills the panel from `var(--mail-MessagingMenu-bg,
        $o-view-background-color)`, and messaging_menu.dark.scss re-points that custom property to
        `mix($gray-100, $gray-200, 65%)` - a near-white gray that never flips - so the whole dropdown
        rendered a near-white panel under the near-white $body-color text. This module re-points
        --mail-MessagingMenu-bg onto the dark view surface. Measured as the dropdown text ($body-color)
        against the resolved panel fill at the fixed AA threshold. WOULD FAIL IF REVERTED: dropping the
        override lets messaging_menu.dark.scss' light gray win as the last writer and the ratio falls
        below 4.5."""
        css = self._compiled_css(DARK_BUNDLE)
        menu_bodies = _bodies_matching(
            css,
            lambda selector: _selector_subject(selector) == ".o-mail-MessagingMenu",
            ANY_ANCESTORS,
        )
        fills = _declared_values(menu_bodies, _custom_property_re("mail-MessagingMenu-bg"))
        self.assertTrue(
            fills,
            "No compiled --mail-MessagingMenu-bg on .o-mail-MessagingMenu in %s - the messaging-menu "
            "dark de-light did not reach the bundle." % DARK_BUNDLE,
        )
        panel_value, panel_rgb = self._resolve_dark_colour(
            css, fills[-1], "dark messaging-menu panel"
        )
        text_rgb = self._assert_rgb(
            self._dark_root_token(css, "body-color", "dark messaging-menu text"),
            "dark messaging-menu text",
        )
        ratio = _contrast_ratio(text_rgb, panel_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The messaging-menu text (dark $body-color) on the resolved panel fill (%s) is only "
            "%.2f:1 - WCAG AA normal text needs >= %.1f:1. Core's messaging_menu.dark.scss paints this "
            "panel `mix($gray-100, $gray-200, 65%%)`, a near-white gray."
            % (panel_value, ratio, WCAG_AA_NORMAL_TEXT),
        )

    # ==============================================================================================
    # 14. Dark mode - surfaces the first pass MISSED (PR #658 review-fix, live mobile+dark sweep)
    # ==============================================================================================
    # A second live mobile+dark acceptance sweep found four more mail surfaces core sculpts from the
    # raw Bootstrap grayscale ramp / a compile-time literal that no overridable Sass var reaches, so
    # the C-2 dark recompile left them LIGHT: the near-white $body-color text sits on a near-white /
    # mid-gray fill and fails WCAG AA. Each guard measures the WCAG 2.x ratio of the COMPILED dark
    # colours against the FIXED AA threshold (never a hex snapshot, never the code's own computed
    # output), so a later re-tune that still clears AA is not a false alarm and a regression back to a
    # light literal is caught. Every one is RED before this module's mail_dark.scss additions and
    # GREEN after.

    def _dark_body_color_rgb(self, css, label):
        """The near-white dark body text ($body-color -> #EDF4F5), resolved through core's :root."""
        return self._assert_rgb(self._dark_root_token(css, "body-color", label), label)

    def test_dark_chat_window_body_is_a_dark_surface_under_its_message_text(self):
        """The chat-window body must be a dark surface, not the light `bg-100` gray.

        The chat popup / mobile fullscreen window root carries the `bg-100` utility
        (mail/static/src/core/common/chat_window.xml:6), which
        web/static/src/scss/bootstrap_review_backend.scss emits through o-print-color as
        `background-color: $o-gray-100 !important` (#F8F9FA). $o-gray-100 is NOT flipped by the dark
        recompile, so the window body stayed near-white under the near-white $body-color message text
        (1.06:1). This module re-points `.o-mail-ChatWindow` onto the dark view surface
        ($o-view-background-color -> #111B1E). WOULD FAIL IF REVERTED: with no `.o-mail-ChatWindow`
        background override, no rule declares a background on that subject and the assertion that the
        window body is painted at all fails - the body is left to the light `bg-100` utility."""
        css = self._compiled_css(DARK_BUNDLE)
        bodies = _bodies_matching(
            css, lambda selector: _selector_subject(selector) == ".o-mail-ChatWindow", ANY_ANCESTORS
        )
        self.assertTrue(
            bodies,
            "No compiled rule styles the .o-mail-ChatWindow element in %s." % DARK_BUNDLE,
        )
        backgrounds = _declared_values(bodies, _BACKGROUND_RE)
        self.assertTrue(
            backgrounds,
            "The .o-mail-ChatWindow element declares no background in %s, so its body is left to the "
            "light `bg-100` utility (#F8F9FA) - the near-white $body-color message text renders at "
            "1.06:1." % DARK_BUNDLE,
        )
        surface_value, surface_rgb = self._resolve_dark_colour(
            css, backgrounds[-1], "dark chat-window body"
        )
        text_rgb = self._dark_body_color_rgb(css, "dark chat-window message text")
        ratio = _contrast_ratio(text_rgb, surface_rgb)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The chat-window message text (dark $body-color) on its body surface (%s) is only "
            "%.2f:1 - WCAG AA normal text needs >= %.1f:1. The light `bg-100` utility (#F8F9FA) is the "
            "un-flipped default this override replaces."
            % (surface_value, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_message_bubbles_are_dark_tinted_surfaces_per_category(self):
        """Each message bubble (blue/green/orange) must be a DARK tinted surface under its body text.

        Core message.scss:91-104 sets `--o-message-bubble-bg: mix($o-view-background-color, $_color,
        90%)` per `.o-#{type}`, which WOULD recompile dark-correct for free. But
        mail/static/src/core/common/message.dark.scss (in web.assets_web_dark via mail's own
        `mail/static/src/**/*.dark.scss` glob) overrides each variant's `background-color` DIRECTLY
        with `mix($gray-100, darken($_color, ..), ..) !important` - light, because $gray-100 is
        unflipped - so the bubble stayed light blue (#D4E6F0) under the near-white $body-color (1.15:1),
        viewport-independent (desktop dark too). This module re-points every variant onto a dark
        surface tinted by its own category colour. WOULD FAIL IF REVERTED: message.dark.scss' light
        mix is then the last (0,2,0) writer and the ratio assertion reports it. Same specificity, later
        source order wins, so the LAST-declared background of each `.o-mail-Message-bubble.o-#{type}`
        is read (the `.o-muted` and tail selectors are excluded by the exact-subject match) - among
        the rules that REACH this bubble, which is what MESSAGE_BUBBLE_ANCESTORS decides: the same
        subject scoped under another module's root paints a bubble in that module's subtree, not
        this one, and reading it here would report a colour no dark thread ever renders."""
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
                backgrounds = _declared_values(bodies, _BACKGROUND_RE)
                self.assertTrue(
                    backgrounds,
                    "The %s bubble declares no background in %s." % (subject, DARK_BUNDLE),
                )
                bubble_value, bubble_rgb = self._resolve_dark_colour(
                    css, backgrounds[-1], "%s bubble" % variant
                )
                ratio = _contrast_ratio(text_rgb, bubble_rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "The %s message bubble body text (dark $body-color) on its bubble fill (%s) is "
                    "only %.2f:1 - WCAG AA normal text needs >= %.1f:1. Core's message.dark.scss "
                    "paints this `mix($gray-100, darken(...), ..)`, a near-white gray."
                    % (variant, bubble_value, ratio, WCAG_AA_NORMAL_TEXT),
                )

    def test_dark_read_notification_item_name_and_preview_clear_aa(self):
        """A READ conversation's name + preview in the messaging-menu list must clear WCAG AA.

        A read (non-unread, non-hard-muted) conversation is rendered by NotificationItem with muted=1
        (mail/static/src/core/public_web/messaging_menu.xml:45 `!thread.isUnread ? 1 : 0`), which
        stamps the `text-muted` class on the item root (notification_item.xml:9). Odoo's BACKEND
        redefines that utility to the Sass LITERAL `$text-muted` = $o-main-color-muted =
        rgba($o-gray-700, .76) (web/static/src/scss/utilities_custom_backend.scss:18,
        bootstrap_overridden.scss:85) - NOT Bootstrap 5.3's runtime `var(--secondary-color)` - so it
        does NOT flip: the read name + preview inherited rgba(73,80,87,.76) = 2.14:1 on the #111B1E
        list. This module re-points them onto the dark muted-text token --secondary-color (#8EA5A8),
        resolved through core's own :root emission (a rename orphans the reference and this goes RED).
        WOULD FAIL IF REVERTED: with no `.o-mail-NotificationItem.text-muted` name/preview override,
        no rule declares a colour on those subjects and the assertion fails - the read text is left to
        core's inherited $text-muted literal at 2.14:1. Measured against the dark list surface
        (body-bg -> #111B1E)."""
        css = self._compiled_css(DARK_BUNDLE)
        surface_rgb = self._assert_rgb(
            self._dark_root_token(css, "body-bg", "dark notification list surface"),
            "dark notification list surface",
        )
        for element in (".o-mail-NotificationItem-name", ".o-mail-NotificationItem-text"):
            with self.subTest(element=element):
                bodies = _bodies_matching(
                    css,
                    lambda selector, element=element: _selector_subject(selector) == element
                    and ".text-muted" in selector, ANY_ANCESTORS,
                )
                self.assertTrue(
                    bodies,
                    "No compiled rule re-points the READ (.text-muted) %s in %s - the read name/"
                    "preview is then left to core's inherited $text-muted literal rgba(73,80,87,.76) "
                    "= 2.14:1 on the dark list." % (element, DARK_BUNDLE),
                )
                colors = _declared_values(bodies, _COLOR_RE)
                self.assertTrue(
                    colors, "The read %s declares no colour in %s." % (element, DARK_BUNDLE),
                )
                text_value, text_rgb = self._resolve_dark_colour(
                    css, colors[-1], "read %s" % element
                )
                ratio = _contrast_ratio(text_rgb, surface_rgb)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "The read conversation %s (%s) on the dark list (%s) is only %.2f:1 - this is "
                    "normal muted text and needs >= %.1f:1. Core's backend `text-muted` utility "
                    "resolves to rgba(73,80,87,.76) here at 2.14:1."
                    % (element, text_value, self._dark_root_token(css, "body-bg", element),
                       ratio, WCAG_AA_NORMAL_TEXT),
                )

    def test_dark_composer_input_fill_clears_aa_under_its_text(self):
        """The composer field must be a dark fill its input text + placeholder can be read on.

        The composer field is `.o-mail-Composer-bg { background-color: var(--mail-Composer-bg,
        $o-view-background-color) }` (composer.scss:103-104) and the input is transparent over it.
        mail/static/src/core/common/composer.dark.scss sets `.o-mail-Composer { --mail-Composer-bg:
        mix($gray-100, $o-view-background-color) }` - a slightly raised field that with the unflipped
        light $gray-100 composites to the mid-gray #858A8C, only 3.14:1 under the near-white
        $body-color input text. This module re-points the field onto a subtly raised DARK neutral.
        WOULD FAIL IF REVERTED: composer.dark.scss' light mix is the last writer on `.o-mail-Composer`
        and the ratio assertion reports #858A8C at 3.14:1. Same selector, later source order wins, so
        the LAST-declared --mail-Composer-bg is read - last among the rules that REACH this composer,
        which is what COMPOSER_ANCESTORS decides: a rule scoped under another module's root declares
        the same token on the same subject for a composer inside THAT subtree."""
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
            "WCAG AA normal text needs >= %.1f:1. Core's composer.dark.scss paints this "
            "`mix($gray-100, $o-view-background-color)` = the mid-gray #858A8C at 3.14:1."
            % (fill_value, ratio, WCAG_AA_NORMAL_TEXT),
        )

    # ==============================================================================================
    # 14. Dark mode - the spreadsheet LIGHT ISLAND (the embedded comments Chatter)
    # ==============================================================================================
    # See the "spreadsheet LIGHT ISLAND" element-model section above for the collision these two
    # guards protect against and for why neither needs `spreadsheet` or `viin_spreadsheet` installed.

    def _island_forced_button_text(self):
        """Return ``(value, rgb)`` of the label core forces on every `.btn` inside `.o-spreadsheet`.

        Read out of core's OWN dark stylesheet rather than pinned here: that label is core's design
        decision for the light island, this module cannot change it, and reading it keeps the
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
            "%s no longer declares a `.btn { color: ... }` inside its `.o-spreadsheet` wrapper. That "
            "declaration is the whole reason a dark-palette Chatter goes unreadable inside the "
            "editor; if core dropped it, re-ground these guards rather than deleting them."
            % CORE_SPREADSHEET_DARK_SCSS,
        )
        value = _normalize_value(match.group(1))
        return value, self._assert_rgb(value, "spreadsheet light-island .btn label")

    def _rendered_backdrop(self, css, chain, bundle_name, label, siblings=()):
        """Return the :class:`Backdrop` an element in ``chain`` is really READ ON.

        WHICH PAINTED SIBLING SITS BEHIND IT IS AN INPUT, NOT AN ASSUMPTION. ``siblings`` declares
        the full-bleed overlays that MAY be painted behind this element; each one is applied only
        when its own container is a strict ancestor of the subject, which is the DOM fact that
        decides it (see the "WHICH PAINTED SIBLING SITS BEHIND THIS ELEMENT" section above for the
        rule and for the two directions it is wrong in). Passing none is the honest model for a
        subtree that has no overlay in it - not a shortcut - and is what every ancestor-only caller
        does.

        With no overlay applying, this walks OUTWARDS from the element and stops at the first
        ancestor that paints a fully opaque colour - the browser's own model for a transparent
        element, and the reason the guards over it are indifferent to WHERE a surface gets re-lit:
        any layer in the stack may carry the fix and none of them is prescribed.

        A stack that paints nothing anywhere shows the app's own body background, so that is the
        backstop rather than a failure - it is a real surface, and reading it from core's `:root`
        emission keeps the answer available on a database where the modules that would otherwise
        contribute the outer chrome are not installed at all."""
        self._require_cascade_resolver()
        for sibling in siblings:
            sibling_chain = _painted_sibling_chain(chain, sibling)
            if sibling_chain is None:
                continue
            value = _computed_value(css, sibling_chain, BACKGROUND_PROPS)
            self.assertIsNotNone(
                value,
                "No compiled background applies to the %s in %s. Core's own message stylesheets "
                "paint every variant, so an empty resolution means the modelled overlay no longer "
                "matches message.xml:89." % (sibling.label, bundle_name),
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

    def _island_rendered_surface(self, css, chain, label):
        """Return ``(depth, value, rgb)`` of the DARK-bundle surface an element renders on.

        The ancestor-only reading of :meth:`_rendered_backdrop`, kept as the entry point for the
        island guards whose subjects have no overlay in their subtree."""
        backdrop = self._rendered_backdrop(css, chain, DARK_BUNDLE, label)
        return backdrop.depth, backdrop.value, backdrop.rgb

    def _inherited_colour(self, css, chain, bundle_name, label):
        """Return ``(value, rgb)`` of the colour an element in ``chain`` really renders its text in.

        The INHERITED-property dual of :meth:`_rendered_backdrop`. `color` inherits, so the
        element's own declaration is only the first candidate: when no rule styles the element
        itself the value comes from the nearest ancestor that declares one, and only from the
        document body when no ancestor does either. Walking that outwards is what makes a
        declaration on a WRAPPER visible - resolving on the subject alone returns None whenever the
        colour lives one layer out, and a caller that then falls back to the body token reports a
        value the element does not render in. It is also the only way a BARE-class `!important`
        (0,1,0) on an ancestor is seen to beat a more specific normal rule further out, which is the
        cascade order a browser applies and the one core's `.o-discuss-text-body` turns on in BOTH
        schemes (core.scss:99-101 light, core.dark.scss:13-15 dark)."""
        self._require_cascade_resolver()
        for depth in range(len(chain)):
            value = _computed_value(css, chain[depth:], ("color",))
            if value is not None:
                return self._resolve_scheme_colour(css, value, bundle_name, label)
        fallback = self._root_token(css, "body-color", bundle_name, label)
        return self._resolve_scheme_colour(css, fallback, bundle_name, label)

    def _island_inherited_colour(self, css, chain, label):
        """The dark-bundle reading of :meth:`_inherited_colour`."""
        return self._inherited_colour(css, chain, DARK_BUNDLE, label)

    def _rendered_ink(self, css, chain, bundle_name, label):
        """Return ``(value, rgb, alpha)`` of the ink an element paints, alpha included.

        The colour half of a contrast pair is not always opaque, and in the LIGHT backend it usually
        is not: `$text-muted` is `rgba($o-gray-700, $o-opacity-muted)` (primary_variables.scss:121),
        so a muted glyph is ALREADY a translucent wash over whatever it lands on - which is the
        whole reason the surface under it decides whether it is readable. On top of that an element
        may carry an `opacity` utility, which composites the element as a whole. Both multiply into
        one effective alpha, and reading each from the COMPILED bundle rather than pinning `.76` or
        `.75` here keeps the arithmetic correct through a core re-tune of either."""
        self._require_cascade_resolver()
        value, rgb = self._inherited_colour(css, chain, bundle_name, label)
        alpha_match = _RGBA_ALPHA_RE.search(value)
        alpha = 1.0 if alpha_match is None else (_to_alpha(alpha_match.group(1)) or 1.0)
        opacity = _computed_value(css, chain, ("opacity",))
        if opacity is not None:
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

    def test_dark_spreadsheet_island_chatter_buttons_clear_aa_under_the_forced_light_label(self):
        """The embedded Chatter's composer buttons must be readable inside the spreadsheet island.

        THE COLLISION. Core keeps `.o-spreadsheet` a LIGHT island in dark mode and forces
        `.o-spreadsheet .btn { color: <light-island label> }` (0,2,0, no `!important`), which outranks
        Bootstrap's `.btn { color: var(--btn-color) }` (0,1,0) and repaints the LABEL of every button
        in the editor. It does not touch the FILL, so the three composer buttons keep resolving their
        background through the app-wide dark ladder - `.btn-secondary` onto dark_buttons.scss'
        $o-viin-dark-control-bg, `.btn-primary` onto the chrome teal. Each button therefore serves its
        label from the light scheme and its fill from the dark one. Measured live at 1440px: Log note
        1.19:1, Activity 1.19:1, Send message 2.17:1 - the dark_buttons pairing they were DESIGNED as
        is 10.95:1, so nothing here is a mis-designed colour, only a mis-matched pair.

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
            "The chatter composer buttons no longer carry those classes, so the island element "
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
                    "the bundle, so an empty resolution means the modelled element no longer matches "
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
        on whatever the stack behind it paints. When measured (1.70:1 live) that was the comments
        panel's own `bg-view`, which the dark recompile drove to the dark view surface;
        `viin_spreadsheet` 3c6dcc617 has since removed it, so the panel paints nothing and the walk
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
            "The muted secondary markers no longer carry those classes, so the element models below "
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
            "The composer textarea no longer carries those classes, so the element model below is "
            "keyed on markup core stopped rendering - re-transcribe it from composer.xml.",
        )
        css = self._compiled_css(DARK_BUNDLE)
        chain = _element_chain(ISLAND_COMPOSER_INPUT_CLASSES, ISLAND_COMPOSER_INPUT_LAYERS)

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

    # ==============================================================================================
    # 15. The painted-sibling surface model itself, pinned in BOTH directions
    # ==============================================================================================
    def test_message_bubble_is_composited_only_for_elements_inside_the_text_body_wrapper(self):
        """A full-bleed sibling must be the surface for what it covers, and for nothing else.

        WHY THIS IS ITS OWN GUARD. Every contrast assertion in this file is only as true as the
        surface it measured against, and the surface model is the one thing none of them can check:
        a guard that composites the wrong layer reports a confident, precise, wrong number and stays
        green. That is not hypothetical - it is how the 1.11:1 message-body defect survived a full
        contrast suite, and the correction over-applied the bubble to the message TIMESTAMP before
        it settled. Both mistakes are invisible to every other test here, so the rule that separates
        them is asserted directly.

        THE RULE. `.o-mail-Message-bubble` (message.xml:89) is `position-absolute top-0 start-0
        w-100 h-100` inside `.o-discuss-text-body` (:82). It is therefore the surface for the glyphs
        inside that wrapper and for no others - it is a SIBLING of the body, not an ancestor of it,
        and it is not in the timestamp's subtree at all (`.o-mail-Message-date` at :44 sits in
        `.o-mail-Message-header` at :38, outside the content container entirely).

        WHAT IS ASSERTED, AND WHY IT CANNOT BE SATISFIED BY EITHER MISTAKE. Not the bubble's colour
        and not the panel's - only that DECLARING the bubble CHANGES the resolved surface for the
        message body and does NOT change it for the timestamp. An ancestor-only resolver fails the
        first half (declaring the bubble changes nothing); a resolver that hands every element in
        the message subtree the bubble fails the second (it changes the timestamp too). No single
        wrong model passes both halves, which is what makes this red-before-green with no run:
        the two directions are mutually exclusive outcomes of the same declared overlay.

        WHY BOTH BUNDLES. The rule is a DOM fact, so it is scheme-independent; the light backend and
        the dark bundle paint different bubbles and different panels, and a model that happened to
        be right only where the two colours are far apart would be worth very little."""
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.xml",
            ("o-mail-Message-bubble position-absolute top-0 start-0 w-100 h-100",
             "d-inline-block o-discuss-text-body",
             'class="o-mail-Message-date o-xsmaller"'),
            "The bubble is no longer a full-bleed element inside `.o-discuss-text-body`, or the "
            "timestamp is no longer outside it, so the containment rule this guard pins is keyed on "
            "markup core stopped rendering - re-transcribe it from message.xml.",
        )
        body_chain = _element_chain(MESSAGE_BODY_CLASSES, CHATTER_TEXT_BODY_LAYERS)
        date_chain = _element_chain(MESSAGE_DATE_CLASSES, CHATTER_MESSAGE_HEADER_LAYERS)
        composer_chain = _element_chain(
            ISLAND_COMPOSER_INPUT_CLASSES, ISLAND_COMPOSER_INPUT_LAYERS
        )

        for sibling in MESSAGE_BUBBLE_SIBLINGS:
            with self.subTest(bubble=sibling.label, containment="inside the wrapper"):
                self.assertIsNotNone(
                    _painted_sibling_chain(body_chain, sibling),
                    "`.o-mail-Message-body` is a sibling of the %s inside `.o-discuss-text-body` "
                    "(message.xml:82-99), so the bubble IS the surface under its glyphs. Resolving "
                    "no chain for it means the surface model has gone back to compositing "
                    "ancestors only, which is what let a 1.11:1 body read as readable."
                    % sibling.label,
                )
            with self.subTest(bubble=sibling.label, containment="outside the wrapper"):
                self.assertIsNone(
                    _painted_sibling_chain(date_chain, sibling),
                    "`.o-mail-Message-date` (message.xml:44) renders in `.o-mail-Message-header` "
                    "(:38), a sibling of the content container - the %s is several layers further "
                    "in and is never painted behind a timestamp. Resolving a chain for it credits "
                    "the timestamp with a surface it does not render on."
                    % sibling.label,
                )
            with self.subTest(bubble=sibling.label, containment="the wrapper itself"):
                self.assertIsNone(
                    _painted_sibling_chain(composer_chain, sibling),
                    "The composer textarea carries `o-discuss-text-body` on its OWN element "
                    "(composer.xml:77), so it CONTAINS that wrapper rather than sitting next to a "
                    "bubble inside one - and no message bubble is in its subtree at all. Matching "
                    "the subject's own classes instead of a strict ancestor is what puts a message "
                    "surface under a composer field.",
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
                        "so this guard can no longer tell an ancestor-only surface model from a "
                        "correct one and every bubble assertion in this file has quietly stopped "
                        "measuring anything. Re-ground it rather than leaving it green."
                        % (bundle_name, sibling.label, plain_body.value, plain_body.rgb),
                    )
                with self.subTest(bundle=bundle_name, bubble=sibling.label, direction="applied"):
                    self.assertEqual(
                        bubbled_body.painter, sibling.label,
                        "In %s the message body resolves its surface from %s even with the %s "
                        "declared behind it. The bubble fills `.o-discuss-text-body` edge to edge "
                        "(message.xml:89), so it - not the layer behind it - is what the body text "
                        "is read on."
                        % (bundle_name, bubbled_body.painter, sibling.label),
                    )
                with self.subTest(bundle=bundle_name, bubble=sibling.label, direction="not applied"):
                    self.assertEqual(
                        (bubbled_date.painter, bubbled_date.rgb),
                        (plain_date.painter, plain_date.rgb),
                        "In %s declaring the %s CHANGED the surface the message timestamp is "
                        "measured against - from %s (rgb%r) to %s (rgb%r). The timestamp renders in "
                        "`.o-mail-Message-header` (message.xml:44 inside :38), outside "
                        "`.o-discuss-text-body` entirely, so no bubble is ever painted behind it "
                        "and the ancestor walk IS its surface. Applying an overlay to every element "
                        "in the message subtree measures the timestamp against a colour it never "
                        "renders on."
                        % (bundle_name, sibling.label, plain_date.painter, plain_date.rgb,
                           bubbled_date.painter, bubbled_date.rgb),
                    )

    # ==============================================================================================
    # 16. LIGHT mode - the muted/dimmed tiers of an ordinary form-view chatter
    # ==============================================================================================
    # These three guards are NOT scoped to the spreadsheet island and NOT in the dark bundle: they
    # measure `web.assets_backend`, so every form-view chatter in the product is in scope. They share
    # one arithmetic: an already-translucent ink (`$text-muted` is `rgba($o-gray-700, .76)`,
    # primary_variables.scss:121) optionally dimmed further by an `opacity` utility, composited onto
    # the surface the message really renders on - the light chatter panel, or a bubble when the
    # message has one. That surface split is the reason the painted-sibling model above exists, and
    # the reason a tier tuned against the panel alone is not enough on its own.

    def _assert_readable_on_every_message_surface(
        self, bundle_name, chain, subject, why, panel_label="the chatter panel",
    ):
        """Assert ``subject`` clears AA on the panel AND on each bubble it can be read on.

        One helper for the tiers below because the failure they share is the SURFACE, not the
        colour: each tier is set by one rule and lands on four different backdrops, so a fix that
        satisfies the lightest one and no other is the exact defect being guarded against. Every
        value is resolved from the compiled bundle, so a fix may re-point the tier, drop the
        dimming, or re-tune the bubbles - any coherent choice passes and no incoherent one does.

        ``panel_label`` NAMES the surface the ancestor walk lands on, and it is not decoration: the
        same subject is measured in four containers that paint four different panels, so a failure
        that only says "the panel" sends a reader to the wrong stylesheet. The walk still RESOLVES
        the colour; the label only says which container was walked."""
        css = self._compiled_css(bundle_name)
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
                    "In %s the %s renders %s at an effective alpha of %.4f - painting rgb%r - on %s "
                    "(%s, rgb%r), only %.2f:1 where WCAG AA normal text needs >= %.1f:1. %s"
                    % (bundle_name, subject, ink_value, alpha, painted, label, backdrop.value,
                       backdrop.rgb, ratio, WCAG_AA_NORMAL_TEXT, why),
                )

    def test_light_message_timestamp_muted_tier_clears_aa_on_the_chatter_panel(self):
        """The message timestamp must be readable in an ordinary light-mode chatter.

        THE DEFECT. `.o-mail-Message-date { color: $text-muted }` (mail message.scss:21) and
        `$text-muted: $o-main-color-muted = rgba($o-gray-700, $o-opacity-muted)`
        (bootstrap_overridden.scss:85, primary_variables.scss:121) - a 76%-alpha wash of #495057.
        Composited on the light chatter panel that is a sub-AA grey: measured 4.34:1 against white
        live, and the panel is not white - `.o-mail-Form-chatter` paints
        `$o-webclient-background-color` = `$o-gray-100` (form_renderer.scss:5-6), one step darker
        than the measurement was taken on. Every timestamp in every form-view chatter in the product
        is this tier; nothing here is spreadsheet-scoped and nothing here is dark-mode-only.

        WHY THE SURFACE IS RESOLVED AND NOT ASSUMED WHITE. The timestamp is the ONE subject in this
        section that never sits on a bubble (message.xml:44 puts it in `.o-mail-Message-header`,
        outside `.o-discuss-text-body`), so its surface is whatever the ancestor walk lands on - and
        assuming that is white is how a tier gets tuned 0.1 too optimistically.

        WOULD FAIL IF REVERTED: the untouched tier composites to rgb(115, 121, 126) on the
        `$o-gray-100` panel - 4.22:1, under the 4.5:1 floor."""
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.scss",
            (".o-mail-Message-date {", "color: $text-muted;"),
            "The timestamp no longer takes `$text-muted`, so this guard measures a tier core "
            "stopped applying to it.",
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

        THE DEFECT. message.xml:110 renders `<i class="text-muted opacity-75">` in place of a body
        when the message has no content. That stacks TWO dimmings that were each chosen alone: the
        muted tier is already a 76%-alpha wash, and `.opacity-75` composites the whole element again
        at 75%, so the glyphs paint at an effective 57% - far fainter than anything the muted tier
        was tuned for. Measured 2.68:1 live.

        AND IT IS NOT ALWAYS ON THE PANEL. The placeholder is a child of `.o-mail-Message-body`, so
        it is inside `.o-discuss-text-body` and a bubbled message paints its bubble behind it - the
        same surface split the message body has, resolved through the same declared overlay. A fix
        checked only against the panel leaves every bubbled empty message exactly as faint.

        WHAT IS ASSERTED. The compiled contrast, never a hex and never an opacity literal: both the
        tier alpha and the utility opacity are read out of the bundle, so dropping `opacity-75`,
        darkening the tier, or re-tuning the bubbles all satisfy it, and none of them can be faked
        by a different-but-equally-faint shade.

        WOULD FAIL IF REVERTED: the untouched pair composites to rgb(148, 153, 157) on the
        `$o-gray-100` panel - 2.73:1 - and lands under the floor on all three bubbles too."""
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.xml",
            ('t-if="message.isEmpty" class="text-muted opacity-75"',),
            "The empty-message placeholder no longer carries those classes, so the element model "
            "below is keyed on markup core stopped rendering.",
        )
        self._assert_readable_on_every_message_surface(
            BACKEND_BUNDLE,
            _element_chain(MESSAGE_EMPTY_PLACEHOLDER_CLASSES, CHATTER_BODY_MUTED_LAYERS,
                           tag=MESSAGE_EMPTY_PLACEHOLDER_TAG),
            "empty-message placeholder",
            "`text-muted opacity-75` (message.xml:110) dims an already-translucent tier a second "
            "time, and the two dimmings were chosen independently. This is the ONLY text a "
            "contentless message shows, so it cannot be the least readable thing on the screen.",
        )

    def test_light_edited_marker_clears_aa_on_every_surface_it_lands_on(self):
        """The `(edited)` marker must stay readable, not merely present.

        THE DEFECT. `mail.Message.edited` (message.xml:151-153) renders
        `<span class="o-xsmaller opacity-50"> (edited)</span>` into the `.o-mail-Message-edited`
        marker the server writes into the body HTML (message.js:449-450). It declares no colour, so
        it inherits the body tier - core's bare-class `!important` on `.o-discuss-text-body`
        (core.scss:99-101, `$gray-700`) - and then halves it. A 50% opacity turns a comfortable
        8.2:1 body tier into a 2.3:1 marker: measured 2.32:1 live. It is small text carrying real
        information about the message's history, not decoration.

        SAME SURFACE SPLIT. The marker renders inside `.o-mail-Message-body`, so a bubbled message
        paints its bubble behind it exactly as it does behind the body text, and the panel is only
        one of the four surfaces it can land on.

        WOULD FAIL IF REVERTED: the untouched marker composites to rgb(160, 164, 168) on the
        `$o-gray-100` panel - 2.36:1, roughly half the floor - and fails on every bubble as well."""
        self._assert_core_source_contains(
            "mail/static/src/core/common/message.xml",
            ('<t t-name="mail.Message.edited">', 'class="o-xsmaller opacity-50"'),
            "The `(edited)` marker no longer carries those classes, so the element model below is "
            "keyed on markup core stopped rendering.",
        )
        self._assert_readable_on_every_message_surface(
            BACKEND_BUNDLE,
            _element_chain(MESSAGE_EDITED_MARKER_CLASSES, CHATTER_EDITED_MARKER_LAYERS,
                           tag=MESSAGE_EDITED_MARKER_TAG),
            "(edited) marker",
            "`opacity-50` (message.xml:152) halves the body tier this marker inherits. It tells a "
            "reader the message was changed after posting, so it has to be legible; re-point the "
            "marker or drop the dimming rather than lowering the floor.",
        )

    # ==============================================================================================
    # 17. DARK mode - the same two dimmed nodes, OUTSIDE the spreadsheet island
    # ==============================================================================================
    # Section 16 measures these two nodes in the LIGHT backend bundle; the island guards measure the
    # island's own tiers on its light ground. Neither reaches the case below: every form-view
    # chatter, the Discuss app and every chat window render this subtree on the DARK palette, where
    # both the ink and all four surfaces are different values.
    #
    # WHAT CHANGES IN DARK, AND WHY IT IS NOT THE SAME DEFECT TWICE. In light both nodes are dimmed
    # versions of a DARK ink on a LIGHT ground, so dimming pulls them toward the surface. In dark the
    # ink is LIGHT and the ground is dark, so the same utilities pull them toward the surface from the
    # other side - and they arrive there from a different starting tier: the placeholder's
    # `.text-muted` is not the un-flipped light literal here (dark_palette.scss re-points
    # $o-main-color-muted onto $body-secondary-color), and the marker inherits the dark
    # `.o-discuss-text-body` `!important` (core.dark.scss:13-15) rather than the light one
    # (core.scss:99-101). Two different inks, two different tiers, one shared symptom - which is why
    # a light fix cannot be assumed to carry, and why these are separate guards rather than a second
    # bundle argument on the light ones.
    #
    # THREE CONTAINERS, NOT ONE. `Thread` renders the identical subtree in all three, and they paint
    # DIFFERENT panels: the form-view chatter takes $o-webclient-background-color, while Discuss
    # (discuss_content.scss:7-9) and the chat window (this module's own `.o-mail-ChatWindow` rule)
    # both take the view surface, a lighter dark. The chatter panel is the darkest of the three and
    # therefore the most forgiving, so measuring the chatter alone is measuring the best case.
    #
    # The markup transcription these element models are keyed on is pinned once, by the light guards
    # in section 16 - the same message.xml lines, and a scheme cannot change them - so it is not
    # re-asserted here (ODOO-AI-ETHOS #11).

    def _assert_dark_node_readable_in_every_container(self, subject_layers, element, tag, subject,
                                                      why):
        """Assert one dimmed body node clears AA on every dark surface, in every container.

        Loops the containers rather than taking one, because the defect this section exists for is a
        fix that lands in the container it was measured in: the three panels are two distinct darks,
        so a rule tuned against the chatter alone leaves Discuss and the chat window short, and
        nothing about the subject itself says which container a reader is in."""
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

        THE DEFECT. message.xml:110 renders `<i class="text-muted opacity-75">` in place of a body.
        On the dark palette `.text-muted` is no longer the un-flipped light literal - dark_palette
        re-points $o-main-color-muted onto $body-secondary-color, an OPAQUE mid grey that is a
        deliberate dark muted tier - and then `.opacity-75` composites the whole element down onto
        whatever is behind it. The tier was chosen as a readable muted grey; the utility was chosen
        with no surface in mind, and the product of the two was chosen by nobody.

        THE SURFACE IS WHAT DECIDES IT, AND ONE SURFACE ALREADY PASSES. Measured on the current tree
        the darkest panel - the form-view chatter's - clears the floor at 4.53:1, so a guard that
        measured only the chatter would be GREEN while the same glyphs sat at 3.36:1 two panels away:

            surface                     ratio
            form-view chatter panel     4.53   (already clears AA - the best case)
            Discuss thread canvas       4.35
            chat-window body            4.35
            o-blue bubble               3.74
            o-green bubble              3.68
            o-orange bubble             3.36   (worst)

        That spread is the reason every surface is its own subTest: an average over the six is above
        the floor, and a reader never sees an average.

        WHAT IS ASSERTED. The compiled contrast, never a hex and never an opacity literal: the tier,
        the utility and all four surfaces are read out of the dark bundle, so dropping the dimming,
        re-pointing the tier or re-tuning the bubbles all satisfy it - and none of them can be faked
        by a different-but-equally-faint shade.

        The placeholder is a direct child of `.o-mail-Message-body`, so it is inside
        `.o-discuss-text-body` and a bubbled message paints its bubble behind it. Both halves of the
        selector core styles it through are modelled - the `<i>` tag and the child relation - so this
        guard exercises the rule rather than routing around it: a class-only model would skip a
        `.o-mail-Message-body > i.text-muted.opacity-75` fix entirely and keep reporting the
        undimmed tier."""
        self._assert_dark_node_readable_in_every_container(
            _body_muted_layers,
            MESSAGE_EMPTY_PLACEHOLDER_CLASSES,
            MESSAGE_EMPTY_PLACEHOLDER_TAG,
            "empty-message placeholder",
            "`text-muted opacity-75` (message.xml:110) dims the dark muted tier a second time, and "
            "the two dimmings were chosen independently. This is the ONLY text a contentless "
            "message shows, so it cannot be the least readable thing on the screen - and a fix has "
            "to hold on every panel and every bubble, not on the darkest panel alone.",
        )

    def test_dark_edited_marker_clears_aa_in_every_container_it_renders_in(self):
        """The `(edited)` marker must stay readable on the dark palette, not merely present.

        THE DEFECT. `<span class="o-xsmaller opacity-50">` (message.xml:152) declares no colour, so
        it inherits the dark body tier core forces on `.o-discuss-text-body` as a bare-class
        `!important` (core.dark.scss:13-15) - and then halves it. Halving a near-white ink on a dark
        ground walks it straight toward the surface, so the 50% IS the whole defect: there is no
        second tier to re-point, only the dimming and the surfaces under it.

        WHERE IT FAILS, AND WHERE IT DOES NOT. Every PANEL clears the floor on the current tree; only
        the bubbles fall short, because each bubble is a lighter dark than the panel behind it:

            surface                     ratio
            form-view chatter panel     4.92   (clears AA)
            Discuss thread canvas       4.83   (clears AA)
            chat-window body            4.83   (clears AA)
            o-blue bubble               4.33
            o-green bubble              4.29
            o-orange bubble             4.04   (worst)

        A guard modelling the panel only would be green on all three containers while every bubbled
        message showed a sub-AA marker - the exact inverse of the placeholder's split, and the reason
        the painted-sibling overlay is a declared input rather than a per-guard condition.

        The marker tells a reader the message was changed after posting, so it carries real history
        and has to be legible; the fix belongs on the dimming or the bubbles, never on the floor."""
        self._assert_dark_node_readable_in_every_container(
            _edited_marker_layers,
            MESSAGE_EDITED_MARKER_CLASSES,
            MESSAGE_EDITED_MARKER_TAG,
            "(edited) marker",
            "`opacity-50` (message.xml:152) halves the dark body tier this marker inherits, and on "
            "a dark ground halving walks the ink toward the surface. Every bubble is a lighter dark "
            "than the panel behind it, so a marker tuned against the panel cannot clear AA on one.",
        )

    # ==============================================================================================
    # 18. Dark mode - the island's OWN dimmed nodes, which nothing measured
    # ==============================================================================================
    # The island guards in section 14 measure the muted tier through the `Subject:` line - chosen
    # BECAUSE it is the one in-body marker carrying no `opacity` of its own, so the tier could be
    # read undimmed. That leaves the two nodes that DO carry one measured by nothing: the island's
    # `.o-mail-Message-body > i.text-muted.opacity-75` and `.o-mail-Message-edited .opacity-50`
    # corrections are the only rules holding them up, and no assertion in this file resolves either.
    #
    # WHY THAT MATTERS BEYOND COVERAGE. These two guards assert the island CONTRACT - AA inside the
    # island - through the compiled cascade, never the rule that delivers it. So if the island
    # corrections are ever SUBSUMED by a product-wide dark rule and the duplicates cut, they keep
    # passing when the replacement also clears AA on the island's LIGHT ground, and go RED when it
    # does not. Without them that consolidation is unobservable: the island can regress all the way
    # back to its pre-fix values with the whole suite green.

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
        and the 50% IS its whole de-emphasis - so flattening it is not the fix: at full opacity it
        would be body copy in a smaller size. The correction thins it to the least Bootstrap rung
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

    # ==============================================================================================
    # 19. Dark mode - the (edited) marker must not depend on WHICH other module shares the bundle
    # ==============================================================================================
    # Section 17 compiles `web.assets_web_dark` through THIS registry's actually-installed modules
    # (`self._compiled_css`, backed by `ir.qweb._get_asset_bundle`). That is honest about what this
    # DB renders, but it is silent about a different hazard: mail_dark.scss:337-339 reads a bare Sass
    # variable - `color: $text-muted;`, no `!default` anywhere between the read and any other
    # writer - and Sass gives every module compiled into the SAME bundle a chance to overwrite it
    # first. `hr_skills` ships exactly that overwrite: its manifest wildcard-globs
    # `hr_skills/static/src/scss/*.scss` into `web.assets_backend` (hr_skills/__manifest__.py:53),
    # pulling in `report_employee_cv.scss:3` - `$text-muted: #3b4757;`, no `!default` - and
    # `web.assets_web_dark` is `('include', 'web.assets_web')` + a dark tail, so that write reaches
    # this file whenever hr_skills sits anywhere in the same install (Runbot installs the whole
    # repo, so it always does there). A DB that installs only this branding cluster's own tests
    # never installs hr_skills, so `self._compiled_css(DARK_BUNDLE)` never sees the overwrite and
    # section 17's guards stay green regardless of whether the rule the marker reads is safe against
    # one - which is exactly how this shipped green locally and red on Runbot.
    #
    # WHAT IS COMPILED, AND WHY IT NEEDS NO hr_skills INSTALL. `TransactionCase` isolation forbids
    # `cr.commit()`, and installing a module for real needs one - so this section never installs
    # hr_skills. Instead it re-derives the SAME real Odoo SCSS compile section 17 already trusts
    # (`ir.qweb._get_asset_bundle` -> `AssetsBundle.stylesheets`, each a real `ScssStylesheetAsset`
    # whose `.get_source()` is its actual file content) and hands the SAME real entry point
    # production calls (`AssetsBundle.compile_css` -> `ScssStylesheetAsset.compile`, libsass) ONE
    # extra line of source: the hr_skills literal above, transcribed verbatim, spliced in
    # immediately ahead of THIS module's own `mail_dark.scss` contribution. No production file is
    # read differently and no production code is exercised differently than a real hr_skills install
    # would exercise it - only which SCSS TEXT reaches the same compiler differs, and only by the
    # one line hr_skills itself would contribute.
    #
    # WHY THE SPLICE POINT DOES NOT NEED TO MATCH hr_skills' REAL POSITION. `$text-muted` is a global
    # Sass variable with no `!default` guard anywhere on this path, so whichever assignment source
    # order puts LAST before a read is the one that read sees - there is no way for an assignment to
    # "lose" to an earlier one. Splicing immediately before `mail_dark.scss`'s own fragment means
    # nothing in this concatenation can assign `$text-muted` between the splice and the read, which
    # makes the probe airtight in the one direction that matters: if this guard passes, the marker's
    # colour no longer depends on `$text-muted` at all, wherever in the bundle it gets hijacked from.
    def _compiled_css_with_text_muted_clobbered(self, bundle_name):
        """Recompile ``bundle_name`` with one extra, UNPROTECTED `$text-muted` write spliced in.

        Returns real compiled CSS from Odoo's own compiler, never a hand-built string - every
        assertion downstream reads it exactly as it reads `self._compiled_css`'s output."""
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
            "%s carries no compiled SCSS asset at all - the bundle definition changed, so there is "
            "no real Odoo SCSS compile left to splice a probe into." % bundle_name,
        )
        marker_index = next(
            (index for index, asset in enumerate(scss_assets)
             if asset.url and asset.url.endswith("/" + os.path.basename(DARK_SURFACE_SOURCE))),
            None,
        )
        self.assertIsNotNone(
            marker_index,
            "%s no longer injects %s as its own SCSS asset, so there is no longer a place to splice "
            "an external `$text-muted` write immediately ahead of THIS module's own read of it."
            % (bundle_name, DARK_SURFACE_SOURCE),
        )
        sources = [asset.get_source() for asset in scss_assets]
        clobber = (
            "/* test-injected stand-in for hr_skills/static/src/scss/report_employee_cv.scss:3, an "
            "UNPROTECTED global Sass variable write that reaches this bundle through hr_skills' own "
            "wildcard glob into web.assets_backend whenever hr_skills is installed alongside this "
            "module */\n$text-muted: #3b4757;\n"
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

        Same arithmetic, same primitives (`_rendered_ink` / `_rendered_backdrop` / `_composite` /
        `_contrast_ratio`) over the same declared bubble-sibling map - nothing here re-derives the
        cascade or the contrast formula. The only difference is that ``css`` is handed in rather
        than fetched by bundle NAME through `_compiled_css`'s per-class cache, because the css under
        test here is a one-off recompile (an install-topology probe spliced into the real bundle
        source) that this DB's registry never actually serves and can therefore never be looked up
        by name."""
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
        """The `(edited)` marker's dark colour must not depend on nobody else touching `$text-muted`.

        THE HAZARD SECTION 17 CANNOT SEE. mail_dark.scss:338 reads `color: $text-muted;` - a bare
        Sass variable, not a CSS custom property - so whichever module's SCSS assigns it LAST before
        this rule compiles wins, with nothing here protecting the read. `hr_skills` ships exactly
        such an assignment with no `!default` (see the section banner above), and it reaches
        `web.assets_web_dark` whenever hr_skills is installed alongside this module - which Runbot
        always does and a solo run of this module's own suite never does. Section 17's guards read
        `self._compiled_css(DARK_BUNDLE)`, i.e. THIS registry's actual install, so they can never
        observe that hazard on a DB that never installed hr_skills - the exact gap that let this
        reach Runbot while every local run of this file stayed green.

        WHAT IS ASSERTED. Not a hex, and not hr_skills' own rule: the compiled CONTRAST of the
        marker against every dark surface it renders on, exactly as sections 16-17 assert it,
        recompiled with hr_skills' literal spliced into the SAME real bundle source one line ahead
        of this module's own contribution (see `_compiled_css_with_text_muted_clobbered`). Any fix
        that stops reading `$text-muted` - a CSS custom property Bootstrap emits from a DIFFERENT
        Sass variable, a private Sass variable declared from one, or anything else hr_skills' single
        `$text-muted` write cannot reach - clears this guard; a fix that still reads `$text-muted`
        under any other name does not.

        WOULD FAIL TODAY: spliced ahead of the CURRENT `color: $text-muted;` this compiles the
        marker to the LITERAL hr_skills assigns, `#3b4757` - relative luminance ~0.061, versus
        ~0.010 for the `#111b1e` form-chatter panel section 17 already measures this exact marker
        against. That is ~1.85:1, and every other dark surface the marker can land on is a LIGHTER
        dark still closer to `#3b4757` than to white - nowhere near WCAG AA's 4.5:1 floor, on the
        panel or on any bubble."""
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
