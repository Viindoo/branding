# Compiled-cascade behaviour guard for the 18.0 styling-cascade semantic restore
# (design SSOT .odoo-ai/designs/cluster-semantic-restore-2026-07-24.md, "MODULE
# viin_brand_common"; ODOO-AI-ETHOS #8). Sibling of tests/test_brand_color_compile.py, which
# guards the BRAND-IDENTITY tier (navbar surface, --primary, .btn-primary, --link-color). This
# file guards the CHROME tier restored on top of it: navbar entry states, search facets,
# statusbar, settings tab, stat values and the progress-bar trough.
#
# WHY THESE ASSERT ON COMPILED CSS AND NOT ON THE SCSS SOURCE
# -----------------------------------------------------------------------------------------------
# Almost every surface below is restored through a NATIVE core lever - an SCSS `!default`
# variable set first in brand_variables.scss, or a CSS custom property core already reads. A
# source-substring check ("brand_variables.scss contains $o-component-active-border") would stay
# green after core renames the variable, moves the surface to a different token, or wraps the
# consumer in a rule the module no longer wins. Only the COMPILED web.assets_backend bundle shows
# whether the token still reaches the pixel. So every assertion here resolves the value a real
# element would compute, through the real cascade.
#
# WHY A SMALL CASCADE RESOLVER (_computed_value) INSTEAD OF SUBSTRING MATCHING
# -----------------------------------------------------------------------------------------------
# "Does #007F8E appear somewhere in the bundle" is not a behaviour assertion - the hex appears
# dozens of times for unrelated surfaces, so such a test passes even when the facet renders flat
# teal. The declaration that actually paints an element is decided by the CSS cascade:
# `!important` first, then specificity, then source order; and CSS custom properties resolve
# through var() with inheritance from ancestors. The helpers below implement exactly that, scoped
# to the compounds these surfaces use. Two concrete regressions this machinery exists to catch:
#   1. A groupBy facet rule keyed on `:not(.btn)` silently stops matching when core adds a bare
#      `btn` class (env.searchModel.canOrderByCount) - the selector still LOOKS right in source.
#   2. A non-`!important` module declaration silently loses to a core `!important` declaration of
#      LOWER specificity - the module rule still LOOKS right in source.
# Both are invisible to substring checks and both are caught here.
#
# COLOUR LADDER UNDER TEST (declared once in static/src/scss/brand_variables.scss)
# -----------------------------------------------------------------------------------------------
#   $o-brand-primary / $o-brand-odoo  #00BBCE  DECORATIVE identity teal, 2.33:1 - never under
#                                              white text, never on interactive chrome
#   $o-viin-chrome-base               #007F8E  4.74:1 - base chrome, carries WHITE text
#   $o-viin-chrome-deep               #005E68  7.50:1 - hover / focus / pressed / open rung
#   $o-brand-secondary                #7F4282  6.99:1 on the form sheet - stat values
#
# TWO DELIBERATE NON-RESTORATIONS ARE ASSERTED AS SUCH (owner decisions, 2026-07-24). A future
# test that asserts the OPPOSITE of either would be WRONG - read the docstrings before changing:
#   - the FAVOURITE search facet keeps its native v19 yellow (18.0 flattened it to teal, which
#     erased the "saved filter" affordance);
#   - the STAT VALUE is PURPLE, not teal (18.0's `color: $o-brand-primary` resolved through the
#     18.0 name inversion to the brand SECONDARY purple).
import os
import re

from odoo.tests.common import TransactionCase, tagged

try:
    # Flat DECORATIVE brand teal, read from the module's single Python SSOT - never re-literalised
    # here. Imported defensively so a missing constant yields a crisp per-test failure rather than
    # breaking collection of the whole tests package (same contract as the sibling test files).
    from ..controllers.webmanifest import VIINDOO_THEME_COLOR
except ImportError:
    VIINDOO_THEME_COLOR = None

# Base rung of the chrome ladder. Declared ONCE, by tests/test_brand_color_compile.py, which owns
# the "#007F8E is the AA-compliant Viindoo teal" design fact; imported rather than re-declared
# (ODOO-AI-ETHOS #11 SSOT). ODOO_ENTERPRISE_AUBERGINE / ODOO_COMMUNITY_PURPLE - the two Odoo
# brand-family hexes - are owned by that same sibling and reused here for the content-palette scope
# guard rather than re-literalised.
from .test_brand_color_compile import (
    ODOO_COMMUNITY_PURPLE,
    ODOO_ENTERPRISE_AUBERGINE,
    VIINDOO_NAVBAR_BACKGROUND_COLOR,
)
# $o-brand-secondary is declared only in SCSS (there is no Python constant for it, unlike the
# brand primary). Reuse the SCSS resolver that tests/test_brand_ssot.py already owns so the
# expected stat-value colour is READ from the module's own token SSOT instead of being hardcoded
# a second time here.
from .test_brand_ssot import BRAND_VARIABLES_SCSS, _resolve_scss_hex

BACKEND_BUNDLE = "web.assets_backend"

# --- The ladder, in the normalised form the resolver returns -------------------------------------
# A fixed, hand-chosen design constant asserted as a literal - NOT derived by re-computing a Sass
# darken()/mix() inside the test, which would re-implement production logic and compare it against
# itself. Rationale for each value is in the header block above.
CHROME_BASE = VIINDOO_NAVBAR_BACKGROUND_COLOR            # #007f8e
CHROME_DEEP = "#005e68"                                  # pressed / open / hover rung
PROGRESS_TROUGH_WASH = "#ebfafb"                         # 8% brand teal washed into white
WHITE = "#ffffff"
BLACK = "#000000"
# Core's untouched progress-bar trough - $o-view-background-color, i.e. plain white.
CORE_PROGRESS_TROUGH = WHITE
# Core's editor/website CONTENT swatch colour (base-1 o-color-1). Reused from the sibling's SSOT
# rather than re-literalised: it is core's own $o-enterprise-color default (#714b67), the value
# html_editor seeds base-1 o-color-1 with. The whole point of brand_palette_reset.scss is that this
# content swatch stays core aubergine even though the CHROME uses of $o-enterprise-color are teal.
CORE_CONTENT_O_COLOR_1 = ODOO_ENTERPRISE_AUBERGINE

# WCAG 2.1 SC 1.4.3 minimum contrast for normal-size text.
WCAG_AA_NORMAL_TEXT = 4.5

# ==================================================================================================
# DARK ARM (PR #658 review-fix C-6) - assert every base dark-arm token on the surface it RENDERS on
# ==================================================================================================
# Before this arm the suite had ZERO dark surface in its matrix: every assertion resolved against
# web.assets_backend on WHITE, so it structurally COULD NOT fail on any dark-mode defect - it
# green-lit the #7F4282 stat purple that measures only 2.50:1 on the dark panel. The dark arm
# resolves the SAME tokens through the SAME cascade resolver against web.assets_web_dark - which is
# `('include', 'web.assets_web')` (-> web.assets_backend) + a trailing `*.dark.scss` glob (core
# web/__manifest__.py), so every backend surface RECOMPILES in the dark bundle - and asserts each
# clears WCAG AA against the dark surface it actually sits on.
#
# The dark surface neutrals are FIXED design constants (owner-committed dark palette), asserted as
# the surface a token renders on - NOT re-derived by resolving the (currently un-darkened) panel
# background out of the bundle. That is deliberate: until the dark palette lands, the dark bundle
# still paints panels white, so resolving the surface from the bundle would report a misleading
# WHITE and let a dark-on-white pass. The design COMMITS the dark panel to #111B1E; a token that
# will render on that panel in dark mode must clear AA against #111B1E. That is the behaviour under
# guard, and it is what makes this arm RED until the dark tokens are added.
DARK_BUNDLE = "web.assets_web_dark"
DARK_BODY_BG = "#111b1e"   # dark body / form-sheet / panel tier (surface a readable token sits on)
DARK_APP_BG = "#0b1315"    # dark webclient background band behind panels
DARK_RAISED = "#152225"    # dark raised tier (list/kanban/settings headers)
# Owner-confirmed dark arm (2026-07-24) for the interactive link: #007F8E -> #4FD4E2. Quoted for the
# failure message only - the LOAD-BEARING assertion is the measured WCAG contrast against the dark
# surface, so a different AA-passing dark value would still pass.
DARK_LINK_REF = "#4fd4e2"

# ==================================================================================================
# OWNER REVISION 2026-08-03 - THE BRAND PURPLE IS A LIGHT-MODE-ONLY ACCENT
# ==================================================================================================
# The 2026-07-24 pass gave $o-brand-secondary a DARK ARM (#B589B8) so the purple could survive on the
# dark panel. The owner reversed that: purple is wrong on a dark canvas, so in web.assets_web_dark
# there is NO purple accent at all - every purple surface falls back to its DEFAULT look (the bright
# body-text tier for text, core's own paint for a fill).
#
# Mechanically this is a compile-time flag, $o-viin-dark-bundle (brand_variables.scss, set true by
# dark_palette.scss): our purple rules are wrapped in `@if not $o-viin-dark-bundle` so they emit
# NOTHING into the dark bundle. On top of that $o-brand-secondary itself is re-pointed in dark, which
# is NOT redundant - THREE CORE rules read the token directly and no guard of ours can reach them:
#   web/static/src/views/form/form_controller.scss:1120       .o_xxs_form_view .o_form_label
#   web/static/src/search/search_panel/search_view.scss:111    section header border-bottom
#   point_of_sale/.../pos_kanban_view/pos_kanban_view.scss:5,16
# Left purple, the first of those is 2.50:1 on the dark panel - an outright AA failure.
#
# The two constants below are therefore a REGRESSION SIGNATURE (must never appear in dark) and the
# neutral the token now collapses onto (the dark muted-text tier, $body-secondary-color).
RETIRED_DARK_PURPLE = "#b589b8"   # the deleted dark arm - must NOT come back
DARK_MUTED_TIER = "#8ea5a8"       # $body-secondary-color: 6.75:1 on #111B1E, and NOT purple

# FIX GROUP 1 (PR #658 review-fix) - the secondary SOLID surfaces that stayed LIGHT in dark because
# they are painted from a compile-time grayscale literal ($o-gray-100 #F8F9FA / $o-gray-200 #E9ECEF)
# or a Bootstrap table-variant, none of which the $body-*-bg Layer-1 var overrides reach. These are
# FIXED design constants (the owner-committed dark ladder + a dark info-tinted selection), asserted as
# the concrete dark hex each surface must resolve to in the dark bundle - solid backgrounds, so they
# are directly testable (unlike a translucent overlay). RED until dark_palette.scss ($o-kanban-background)
# + dark_secondary_surfaces.dark.scss land.
DARK_KANBAN_CANVAS = "#0b1315"        # kanban renderer/group/header canvas -> app-grey
DARK_SETTINGS_SIDEBAR = "#0b1315"     # settings tab sidebar (--settings__tab-bg) -> app-grey
DARK_SETTINGS_HEADER = "#152225"      # settings section-header strip (--settings__title-bg) -> raised
DARK_FACET_BAND = "#152225"           # search-facet .bg-200 resting band -> raised
DARK_TABLE_INFO_BAND = "#123037"      # selected .table-info row (--bs-table-bg) -> dark info tint
# The LIGHT values Bootstrap's `.table-info` variant paints a selected-row CELL with, measured on
# the live DOM in the PR #658 review-fix pass (mixins/_table-variants.scss shift-color($info,-80%)
# band + its light inset accent overlay). The cell must resolve to the dark band, NOT either of
# these - the render-faithful companion below asserts inequality against both so the guard is
# non-vacuous even if a light cell rule is later re-introduced.
LIGHT_TABLE_INFO_BAND = "#ccebfa"     # core .table-info --bs-table-bg (the light band background-color)
LIGHT_TABLE_INFO_ACCENT = "#c1deec"   # the light inset box-shadow accent overlay repainting the cell
DARK_READABLE_TEXT = "#edf4f5"        # the dark body text ($body-color) that sits on these surfaces

# ==================================================================================================
# 2026-08-03 SEMANTIC ACCENT + a11y items - the CORE values each fix must move away from
# ==================================================================================================
# All three are grounded from CORE 19.0 source (never from the fix), so each guard is red-before-green
# and names the exact regression signature in its failure message.
#
# `.text-secondary`. Bootstrap builds the TEXT utility out of $theme-colors
# (lib/bootstrap/scss/_maps.scss:99-111 `$utilities-colors: $theme-colors-rgb` ->
# `$utilities-text-colors: map-loop(..., rgba-css-var, "$key", "text")`), and Odoo's BACKEND
# re-declares `$secondary: $gray-300` (web/static/src/scss/bootstrap_overridden.scss:32) because that
# token also paints the SURFACE tier (.bg-secondary chips, .border-secondary hairlines). So
# `.text-secondary` compiles to #DEE2E6 = 1.30:1 on white - invisible. Odoo's own FRONTEND is not
# affected (pre_variables.scss:64 keeps stock Bootstrap's $gray-600 there).
CORE_INVISIBLE_TEXT_SECONDARY = "#dee2e6"
# ... and the SURFACE tier that must NOT move with it. `--secondary-rgb` is the shared :root token
# `.bg-secondary` / `.border-secondary` / `.text-bg-secondary` all read; the fix corrects the TEXT
# tier only, so this stays at core's $gray-300 triplet. Whitespace-stripped for comparison.
CORE_SECONDARY_RGB = "222,226,230"

# The neutral BUTTON pair core compiles from $o-btns-bs-override["secondary"]
# (web/static/src/scss/primary_variables.scss:247-250: $o-gray-300 fill, $o-gray-900 label). The
# $o-gray-* ramp is a fixed compile-time scale that dark_palette.scss deliberately does not re-point,
# so these LIGHT values recompiled unchanged into web.assets_web_dark - light-grey pills on the
# #0B1315 canvas (the pager arrows, the resting chatter Log note / Activity toggles).
CORE_LIGHT_BTN_SECONDARY_BG = "#dee2e6"
CORE_LIGHT_BTN_SECONDARY_FG = "#212529"

# ==================================================================================================
# OWNER DEFECT REPORT 2026-08-03 (dark mode) - the CORE values each fix must move away from
# ==================================================================================================
# "The statusbar active step and the stat buttons are glaring / text sinks."
#
# (1) THE CURRENT STATUSBAR STEP. Core's $o-component-active-bg is
# `mix($o-action, $o-gray-100, 20%)` (primary_variables.scss:133) with $o-action left at the flat
# decorative brand teal, i.e. #C6EDF1 - a LIGHT cyan tint. It reaches the step through
# statusbar_field.scss:14 (--o-statusbar-background-active). Neither the mix operands nor the token
# is reachable from the $body-*-bg overrides, so it recompiled unchanged into web.assets_web_dark.
CORE_LIGHT_STATUSBAR_ACTIVE_BG = "#c6edf1"
# (2) THE STAT BUTTON. $o-btns-bs-outline-override["secondary"] (primary_variables.scss:276-286)
# keys off the same grayscale ramp, and Odoo expands the OUTLINE map through the SAME
# `button-variant` mixin as the filled one (bootstrap_review_backend.scss:32-45, NOT Bootstrap's
# `button-outline-variant`), so `border` is a literal border colour and `hover-background` a literal
# fill. form_compiler.js:157-164 compiles every smart button as
# `oe_stat_button btn btn-outline-secondary`, so both landed straight on the dark form sheet.
CORE_LIGHT_BTN_OUTLINE_BORDER = "#dee2e6"      # 13.45:1 on the dark panel - the reported glare
CORE_LIGHT_BTN_OUTLINE_HOVER_BG = "#e9ecef"    # the near-white hover fill the dark label vanishes on

# A hairline SEPARATES without GLARING. Expressed as a contrast BAND rather than a pinned hex so a
# later tuning pass does not have to edit the guard: the lower bound rejects an invisible border,
# the upper bound rejects the white one the owner reported. Light mode's own stat-button border is
# #DEE2E6 on white = 1.30:1, which is the relationship the dark arm has to reproduce, so the band is
# anchored on that rather than invented.
SUBTLE_BORDER_MIN_CONTRAST = 1.15
SUBTLE_BORDER_MAX_CONTRAST = 3.0

# The dark current-step fill is a SURFACE TIER, not a light slab. Light mode's own active fill
# (#C6EDF1) sits only 1.25:1 from the white sheet it is drawn on - the current step is marked by its
# teal OUTLINE, not by brightness - so the dark arm is held to the same order of magnitude. The
# ceiling is deliberately generous: it exists to reject the forwarded light tint (14.0:1 on the dark
# panel), not to pin a design value.
DARK_ACTIVE_FILL_MAX_GLARE = 4.0

# The numbering layer's own source, read by the geometry-absence guard below. Kept next to the
# constants it belongs with rather than inside the test, so a file rename fails loudly in one place.
STATUSBAR_STEPS_SCSS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "static", "src", "views", "fields", "statusbar", "statusbar_steps.scss",
)

# --- Element models for the 2026-08-03 items, transcribed from core's own markup ------------------
# web/static/src/core/pager/pager.xml:23-25 - `<nav class="o_pager d-flex gap-2 h-100">` >
# `<span class="btn-group d-print-none">` > `<button class="btn btn-secondary o_pager_previous px-2
# rounded-start">`. Chosen as the representative `.btn-secondary` because it is CORE web (no mail /
# theme dependency) and is present on every multi-record view. It is the first element child of the
# btn-group, so it models no previous sibling - which correctly rejects Bootstrap's sibling-gated
# `.btn-check:checked + .btn` competitors.
PAGER_ANCESTORS = frozenset({
    "o_web_client", "o_action_manager", "o_view_controller", "o_control_panel", "o_cp_pager",
    "o_pager", "d-flex", "gap-2", "h-100", "btn-group", "d-print-none",
})
PAGER_PREVIOUS_CLASSES = frozenset({
    "btn", "btn-secondary", "o_pager_previous", "px-2", "rounded-start",
})

# A bare `.text-secondary` in ordinary view content - the class any addon or Studio author types.
# The ancestor pool is deliberately MINIMAL and carries no view-type class, so a rule scoped to a
# particular view (`.o_form_view .text-secondary`) is correctly excluded and the guard measures the
# generic utility, which is what the a11y defect is about.
TEXT_SECONDARY_CLASSES = frozenset({"text-secondary"})
TEXT_SECONDARY_ANCESTORS = frozenset({"o_web_client", "o_action_manager", "o_view_controller"})

# web/static/src/views/list/list_renderer.xml:209-216 - the grouped-list group row is
# `<tr class="o_group_has_content o_group_header o_group_open cursor-pointer">` and its name cell is
# `<th class="o_group_name fs-6 fw-bold {{!group.isFolded ? 'text-black' : 'text-body'}}">`, inside
# `<div class="o_list_renderer o_renderer table-responsive">` > `<table class="o_list_table table
# table-sm table-hover position-relative mb-0 o_list_table_grouped">` (:7 and :14). BOTH foreground
# shapes are modelled: they resolve through DIFFERENT levers (`.text-black` is Odoo's o-print-color
# `color: var(--color) !important`, `.text-body` is Bootstrap's `color: rgba(var(--body-color-rgb),
# ...) !important`), so a rule that beats only one of them is a latent half-fix.
LIST_GROUP_NAME_ANCESTORS = frozenset({
    "o_web_client", "o_action_manager", "o_view_controller", "o_list_view", "o_list_renderer",
    "o_renderer", "table-responsive", "o_list_table", "table", "table-sm", "table-hover",
    "position-relative", "mb-0", "o_list_table_grouped", "o_group_has_content", "o_group_header",
    "o_group_open", "cursor-pointer",
})
_LIST_GROUP_NAME_BASE = frozenset({"o_group_name", "fs-6", "fw-bold"})
LIST_GROUP_NAME_OPEN = _LIST_GROUP_NAME_BASE | {"text-black"}
LIST_GROUP_NAME_FOLDED = _LIST_GROUP_NAME_BASE | {"text-body"}
# The list-view cell surface. Core paints the table from `--table-bg: $o-view-background-color`
# (`white !default`, web/static/src/scss/primary_variables.scss:136); dark_palette.scss re-points
# that same Sass var to the dark panel. The group header itself declares no background on screen -
# core's only `.o_group_header` background rule is inside `@include media-only(print)`
# (list_renderer.scss:52-62), which never applies on screen.
LIST_SURFACE_LIGHT = WHITE
LIST_SURFACE_DARK = DARK_BODY_BG

# WCAG 2.1 SC 1.4.11 minimum contrast for NON-TEXT (UI component) - used by the a11y focus ring in
# the sibling test_focus_ring_compile.py; declared here as the single WCAG-threshold SSOT.
WCAG_NON_TEXT_MIN = 3.0

# PR #658 batch 3 item 6a - core's DIM default for the empty/readonly/false form-label variant,
# grounded verbatim from web/static/src/views/form/form_controller.scss:606
# (`.o_form_view .o_form_label.o_form_label_{empty,false,readonly} { opacity: 0.66 }`). This is the
# core LITERAL the dark polish lifts ABOVE - a grounded threshold, never the fix's own 0.85 value, so
# the item-6a guard is red-before-green without comparing the fix against itself.
CORE_FADED_LABEL_OPACITY = 0.66

# $o-gray-900 #212529 (web/static/src/scss/primary_variables.scss:59) - the near-black the .text-900
# emphasis utility bakes as a COMPILE-TIME literal (bootstrap_review_backend.scss via
# text-emphasis-variant -> o-print-color: `--color: RGBA(33,37,41,var(--text-opacity,1)); color:
# var(--color) !important`). dark_palette.scss re-points $body-color / $o-main-text-color to #EDF4F5,
# but NOT the $o-gray-* scale, so .text-900 stays #212529 in BOTH bundles. Core wraps every
# form-label CELL in `o_wrap_label text-break text-900` (form_group.xml:33/46/58); the bare
# `<label class="o_form_label">` (form_label.xml:5) has no colour of its own and INHERITS that #212529
# from the cell - 1.14:1 on the dark sheet #111B1E, the exact dark-on-dark reversion the GENERAL form
# label (and every other .text-900 surface) must never resolve to in web.assets_web_dark. It is fixed
# by giving .o_form_label its own `color: var(--body-color)` AND re-pointing .text-900's `--color` to
# the dark body tier (dark_secondary_surfaces.dark.scss). This #212529 is the reversion SIGNATURE the
# base-tier guards forbid, not the fix's own value.
LIGHT_BODY_TEXT = "#212529"

# PR #658 batch 3 - the MOBILE burger / app-menu sidebar light island. Core's
# web/static/src/webclient/burger_menu/burger_menu.variables.scss declares all four tokens the panel
# is painted from, every one an `!default` LIGHT literal that burger_menu.scss reads directly:
#   :3 $o-burger-base-bg     $o-white     #FFFFFF -> panel background      (burger_menu.scss:34)
#   :4 $o-burger-base-color  $o-gray-800  #343A40 -> li/button entry text, at .8 alpha  (:60)
#   :6 $o-burger-topbar-bg   $o-gray-100  #F8F9FA -> topbar band                        (:21)
#   :7 $o-burger-topbar-color $o-black    #000000 -> topbar text                        (:22)
# None is reachable from the $body-*-bg surface neutrals, so the panel recompiled WHITE in
# web.assets_web_dark. These are the LIGHT values the dark bundle must NOT resolve (and the light
# bundle must keep, unchanged) - grounded from core, never from the fix.
CORE_BURGER_PANEL_BG = WHITE                # $o-burger-base-bg
CORE_BURGER_ENTRY_TEXT = "#343a40"          # $o-burger-base-color, painted at .8 alpha
CORE_BURGER_TOPBAR_BG = "#f8f9fa"           # $o-burger-topbar-bg
CORE_BURGER_TOPBAR_TEXT = BLACK             # $o-burger-topbar-color
# burger_menu.scss:60 - `@include o-hover-text-color(rgba($o-burger-base-color, .8), ...)`. The .8 is
# core's own literal, so the composite the user reads is measured, not the raw text colour.
CORE_BURGER_ENTRY_TEXT_ALPHA = 0.8
# The dark tiers the fix maps those four tokens onto (dark_palette.scss, end of file). Aliases of the
# ladder constants above rather than new literals - the panel is the same tier as the form sheet and
# the topbar the same raised tier as the list/kanban/settings headers (ODOO-AI-ETHOS #11 SSOT).
DARK_BURGER_PANEL = DARK_BODY_BG            # #111b1e
DARK_BURGER_TOPBAR = DARK_RAISED            # #152225

# --- Element models, transcribed from core's own markup ------------------------------------------
# web/static/src/search/search_bar/search_bar.xml, t-name "web.SearchBar.Facets", lines 16-23:
#   'text-bg-action': facet.type == 'groupBy'
#   'btn':            facet.type == 'groupBy' and env.searchModel.canOrderByCount
#   'btn btn-primary':   facet.type == 'field' || facet.type == 'filter'
#   'btn btn-favourite': facet.type == 'favorite'
# on a div that always carries o_searchview_facet_label. So a groupBy facet has TWO shapes, and a
# rule that matches only one of them is a latent bug - hence both are asserted separately.
# The label div's STATIC classes (same line 16) are carried too: an element model that lists only
# the classes the assertion cares about hides competitor rules keyed on the others, and a missing
# class can only ever cause a false PASS.
_FACET_LABEL_BASE = frozenset({
    "o_searchview_facet_label", "position-relative", "rounded-start-2", "px-1", "rounded-end-0",
    "p-0",
})
FACET_LABEL_FIELD = _FACET_LABEL_BASE | {"btn", "btn-primary"}
FACET_LABEL_GROUPBY = _FACET_LABEL_BASE | {"text-bg-action"}
FACET_LABEL_GROUPBY_ORDERABLE = _FACET_LABEL_BASE | {"text-bg-action", "btn"}
FACET_LABEL_FAVORITE = _FACET_LABEL_BASE | {"btn", "btn-favourite"}
# search_bar.xml line 44.
FACET_VALUES = frozenset({
    "o_facet_values", "position-relative", "d-flex", "flex-wrap", "align-items-center", "ps-2",
    "rounded-end-2", "text-wrap", "overflow-hidden",
})
# The div core renders immediately BEFORE the facet label (search_bar.xml line 14, the ":hover
# overlay"). Modelled because Bootstrap ships sibling-gated button rules whose subject carries no
# state pseudo-class; without a real sibling to test them against they would be treated as
# competitors for the resting facet paint.
FACET_LABEL_PREV_SIBLING = frozenset({
    "position-absolute", "start-0", "top-0", "bottom-0", "end-0", "bg-view", "border",
    "rounded-2", "shadow", "opacity-0", "opacity-100-hover",
})

# --- Ancestor class pools, transcribed from the core templates that render each surface ----------
# A compiled rule applies to an element only if the ancestors its selector demands are ancestors
# the element actually has. Each pool below is the union of the classes on the real ancestor chain,
# so an UNSCOPED rule (Bootstrap's bare `.btn`) is correctly treated as applying, while a rule
# scoped to a context the element is not in (`.o_navbar_apps_menu .dropdown-toggle`,
# `.o_bottom_sheet .o-form-buttonbox`) is correctly excluded. Pools are deliberately generous: an
# over-wide pool can only ADD a competitor and make a guard fail loudly, whereas a too-narrow pool
# would silently hide the override that breaks the surface.
#
# EACH POOL IS READ OFF THE COMPILED SELECTOR - i.e. the full SCSS NESTING of the rule that paints
# the surface - not off the template markup alone. The two differ: SCSS wrappers contribute
# ancestor classes that never appear as a parent in the XML reader's mental model. Deriving
# SETTINGS_TAB_ANCESTORS from settings_page.xml alone missed the two-class wrapper
# `.o_base_settings_view .o_form_renderer` that settings_form_view.scss:46 nests the whole block
# in, so the pool matched nothing and the resolver reported "no declaration" instead of a colour.
# When adding a surface: find the rule in core's SCSS, walk its nesting to column 0, and list
# every class on the way up.
# navbar.xml - .o_main_navbar > .o_menu_sections > (.o_nav_entry | .dropdown-toggle); the overflow
# menu renders as .o_menu_sections_more inside the same .o_menu_sections.
NAVBAR_ANCESTORS = frozenset({
    "o_web_client", "o_main_navbar", "o_menu_sections", "o_menu_sections_more", "dropdown",
})
# search_bar.xml - .o_cp_searchview > .o_searchview > .o_searchview_input_container >
# .o_searchview_facet > (.o_searchview_facet_label + .o_facet_values).
SEARCH_FACET_ANCESTORS = frozenset({
    "o_web_client", "o_control_panel", "o_cp_searchview", "o_searchview",
    "o_searchview_input_container", "o_searchview_facet",
})
# statusbar_field.xml - .o_field_statusbar > .o_statusbar_status > .o_arrow_button (which core
# renders as `btn btn-secondary o_arrow_button`, hence the "secondary" button map feeding it).
STATUSBAR_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_form_statusbar", "o_field_statusbar", "o_statusbar_status",
})
# The two step STATES, transcribed from statusbar_field.xml:36-46.
#
# `disabled` on the CURRENT step is load-bearing, not decoration: core renders it
# `t-att-disabled="props.isDisabled || item.isSelected"`, and Bootstrap paints a disabled button
# from --btn-disabled-color - which the `button-variant` mixin defaults to
# `color-contrast($background)`, NOT to the map's own `color` key. That default is precisely the
# value that measured WHITE on the light-cyan active fill (1.25:1) in the dark bundle, and a model
# without the `disabled` state would resolve the map's `color` instead and miss the defect.
# `o_viin_numbered_step` is this cluster's own hook (statusbar_steps.xml); carrying it here keeps
# the model faithful to the rendered markup and lets the marker's own rules compete honestly.
STATUSBAR_CURRENT_STEP = {
    "classes": frozenset({
        "btn", "btn-secondary", "o_arrow_button", "o_viin_numbered_step",
        "o_arrow_button_current",
    }),
    "states": frozenset({"disabled"}),
    "ancestors": STATUSBAR_ANCESTORS,
    "prev_sibling": frozenset({"btn", "btn-secondary", "o_arrow_button"}),
}
# A CLICKABLE (not current, not disabled) step - what every other stage renders as on a form whose
# statusbar the user may click, e.g. crm.lead's stage_id.
STATUSBAR_STEP = {
    "classes": frozenset({"btn", "btn-secondary", "o_arrow_button", "o_viin_numbered_step"}),
    "ancestors": STATUSBAR_ANCESTORS,
    "prev_sibling": frozenset({"btn", "btn-secondary", "o_arrow_button"}),
}
# ... and the same step on a READONLY statusbar, which is what sale.order / account.move /
# purchase.order actually render: `props.isDisabled` is true, so EVERY step is `disabled` and core
# swaps the label onto $text-muted (statusbar_field.scss:118). A different token from the clickable
# state, hence a separate model - and the one that exposed $o-main-color-muted having no dark arm.
STATUSBAR_STEP_DISABLED = dict(STATUSBAR_STEP, states=frozenset({"disabled"}))
# settings_form_view.scss nesting, walked to column 0: line 46 `.o_base_settings_view
# .o_form_renderer` -> 70 `.o_setting_container` -> 75 `.settings_tab` -> 82 `.selected`. The
# compiled selector is therefore
# `.o_base_settings_view .o_form_renderer .o_setting_container .settings_tab .selected`; the two
# wrapper classes are invisible in settings_page.xml, which only shows .o_setting_container down.
# (.o_form_view is kept because line 39 scopes a sibling block as `.o_form_view.o_base_settings_view`.)
SETTINGS_TAB_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_base_settings_view", "o_form_renderer",
    "o_setting_container", "settings_tab",
})
# button_box.xml + form_compiler.js:158-164 - the desktop form sheet holds
# .o-form-buttonbox > .oe_stat_button > .o_stat_info > .o_stat_value. o_bottom_sheet is
# deliberately ABSENT: that mobile context is core's own sanctioned exception, which pins
# --o-stat-text-color to currentColor and must keep winning there.
BUTTONBOX_ANCESTORS = frozenset({"o_web_client", "o_form_view", "o_form_sheet", "o_form_sheet_bg"})
# form_compiler.js:157-164 compiles a stat button as
# `oe_stat_button btn btn-outline-secondary flex-grow-1 flex-lg-grow-0`, so those classes are
# genuinely on the ancestor chain of .o_stat_value and must be in the pool.
STAT_BUTTON_ANCESTORS = BUTTONBOX_ANCESTORS | {
    "o-form-buttonbox", "oe_stat_button", "btn", "btn-outline-secondary", "flex-grow-1",
    "flex-lg-grow-0", "o_stat_info", "o_field_statinfo",
}
# ... and the stat BUTTON itself, as the same form_compiler.js line renders it. Modelled here rather
# than only as an ancestor pool because the 2026-08-03 guards resolve the button's OWN outline-map
# tokens (--btn-border-color / --btn-color / --btn-hover-bg / --btn-hover-color).
STAT_BUTTON = {
    "classes": frozenset({
        "oe_stat_button", "btn", "btn-outline-secondary", "flex-grow-1", "flex-lg-grow-0",
    }),
    "ancestors": BUTTONBOX_ANCESTORS | {"o-form-buttonbox"},
    "prev_sibling": frozenset(),
}
# progress_bar_field.xml - .o_progressbar > .o_progress.
PROGRESSBAR_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_list_view", "o_field_widget", "o_progressbar",
})
# form_controller.scss:1110-1121 nests the mobile form-label colour as
# `.o_form_view.o_xxs_form_view .o_group .o_inner_group .o_form_label { color: $o-brand-secondary }`
# (grounded verbatim). So the label reads the SAME $o-brand-secondary Sass var as the desktop stat
# value - which is why both re-tint together when the dark arm of that var lands. Ancestors walked
# to column 0 must include EVERY class the compiled selector demands (o_group AND o_inner_group);
# omitting o_group made the rule fail the subset check and the resolver reported "no declaration".
XXS_FORM_LABEL_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_xxs_form_view", "o_group", "o_inner_group",
})
# form_controller.scss:597-609 nests the desktop label + its faded variant as
# `.o_form_view { .o_form_label { &.o_form_label_empty/false/readonly { opacity: 0.66 } } }`, so the
# compiled selector is `.o_form_view .o_form_label.o_form_label_{empty,false,readonly}` - the only
# ancestor it demands is .o_form_view. o_form_sheet/o_form_sheet_bg are added because a real desktop
# label always sits inside the sheet; a generous pool can only ADD a competitor and fail loudly.
FORM_LABEL_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_form_sheet_bg", "o_form_sheet",
})
# form_group.xml:33/46/58 - core wraps every form-label CELL in `o_cell o_wrap_label text-break
# text-900`. The bare `<label class="o_form_label">` (form_label.xml:5) is a CHILD of that cell and
# has no colour of its own, so `color` INHERITS from the cell - and the cell carries `.text-900`,
# whose compile-time #212529 is the inherited value the general label actually renders. Modelling this
# cell as the label's styling parent is what makes the dark-on-dark reversion observable; the earlier
# resolver read only the label's own rules and missed it. (The VALUE cell is `o_wrap_input`, WITHOUT
# text-900 - which is why field values stay the readable #EDF4F5.)
FORM_LABEL_CELL_CLASSES = frozenset({"o_cell", "o_wrap_label", "text-break", "text-900"})
# kanban_header.xml:13 - a kanban column title is `o_column_title flex-grow-1 ... fw-bold ... text-900`
# and carries `.text-900` DIRECTLY (not via a parent cell), on the dark kanban header canvas. Used as
# a representative NON-form-label .text-900 surface to prove FIX 2 (the class-wide --color re-point)
# reaches beyond form labels.
KANBAN_TITLE_CLASSES = frozenset({
    "o_column_title", "flex-grow-1", "min-w-0", "mw-100", "fw-bold", "text-900",
})
KANBAN_HEADER_ANCESTORS = frozenset({
    "o_web_client", "o_kanban_view", "o_kanban_renderer", "o_kanban_header",
})
# navbar.scss:38 / navbar.variables.scss:13 - a resting menu entry paints
# `color: var(--NavBar-entry-color, #{$o-navbar-entry-color})` and $o-navbar-entry-color is
# `rgba($o-white, .9)`. The `.o_nav_entry` / `.o_menu_toggle` selectors carry that colour directly
# (the entry-base placeholder is @extend-merged into them at compile). The navbar is scheme-INVARIANT
# teal, so this token is asserted once (not per arm): DEF-005 requires the entry text render as
# OPAQUE #FFFFFF so it clears AA on the teal bar, not the .9-alpha composite (#E6F2F4, ~4.15:1).
NAVBAR_ENTRY_CLASSES = frozenset({"o_nav_entry", "o_menu_toggle"})

# FIX GROUP 1 (PR #658 review-fix) - ancestor pools for the secondary dark surfaces.
# kanban_controller.scss:86 - `.o_kanban_renderer` DECLARES --Kanban-background (and the derived
# --KanbanGroup-background) from $o-kanban-background, so the renderer is where the token resolves.
KANBAN_RENDERER_ANCESTORS = frozenset({"o_web_client", "o_view_controller", "o_kanban_view"})
# settings_form_view.scss:46 - the settings custom props are declared on `.o_base_settings_view
# .o_form_renderer`; that two-class wrapper is the element the tokens live on.
SETTINGS_RENDERER_ANCESTORS = frozenset({"o_web_client", "o_form_view", "o_base_settings_view"})
# search_bar.xml:6 - the facet pill itself carries `o_searchview_facet` + the `bg-200` utility; its
# ancestors are the control-panel search chain (the pill is the element, not a descendant of itself).
FACET_PILL_ANCESTORS = frozenset({
    "o_web_client", "o_control_panel", "o_cp_searchview", "o_searchview",
    "o_searchview_input_container",
})
# list_renderer.js:938 - a selected row is `<tr class="table-info o_data_row">` inside the list table;
# `--bs-table-bg` / `--bs-table-color` are declared on that row and inherited by its cells.
TABLE_INFO_ROW_ANCESTORS = frozenset({
    "o_web_client", "o_list_view", "o_list_renderer", "o_list_table",
})

# PR #658 batch 3 - the MOBILE burger / app-menu sidebar, transcribed from core's markup.
# Both mobile panels are `t-portal="'body'"` (navbar.xml:106, burger_menu.xml:14), so neither is a
# descendant of .o_web_client - the ancestor pool is the panel root alone, exactly as core's
# `.o_burger_menu, .o_app_menu_sidebar { ... }` (burger_menu.scss:5) scopes it. The app-menu sidebar
# is modelled because it is the panel the review measured; the burger's own panel compiles from the
# SAME nested block (one selector group, identical declarations), so one arm proves both.
BURGER_SIDEBAR_ANCESTORS = frozenset({"o_app_menu_sidebar"})
# navbar.xml:115 / burger_menu.xml:24 - the scrolling panel; `o_burger_menu_app` is what carries the
# background, and BOTH panels set it (so the user-burger is not a second, un-darkened island).
BURGER_PANEL_CLASSES = frozenset({
    "o_burger_menu_content", "o_burger_menu_app", "flex-grow-1", "flex-shrink-1", "overflow-auto",
})
# navbar.xml:113 / burger_menu.xml:17 - the topbar band above the panel.
BURGER_TOPBAR_CLASSES = frozenset({
    "o_sidebar_topbar", "d-flex", "align-items-center", "justify-content-between",
    "flex-shrink-0", "py-0", "fs-4",
})
# navbar.xml:49-54, t-name "web.SectionMenu" - a TOP-LEVEL (non-nested) section title is a
# `<div class="bg-transparent">` whose t-att-class adds `fw-bolder text-900 pt-3 pb-2`. It carries
# `.text-900` DIRECTLY, so it computes the dark #EDF4F5 the emphasis re-point feeds that utility - the
# text half of the 1.11:1 failure the panel background is the other half of.
BURGER_SECTION_TITLE_CLASSES = frozenset({
    "bg-transparent", "fw-bolder", "text-900", "pt-3", "pb-2",
})
# The panel classes are ancestors of anything rendered inside it (navbar.xml:120 `ul.list-unstyled`,
# :47 `li.px-3`). A generous pool can only ADD a competitor and fail loudly, never hide one.
BURGER_SECTION_TITLE_ANCESTORS = (
    BURGER_SIDEBAR_ANCESTORS | BURGER_PANEL_CLASSES | {"list-unstyled", "py-2", "ps-0", "mb-0", "px-3"}
)

# background / background-color are resolved as ONE property family: the `background` shorthand
# resets background-color, and core uses both spellings for these surfaces.
BACKGROUND_PROPS = ("background", "background-color")


# ==================================================================================================
# FIVE PROVEN DARK-MODE ROOT CAUSES (RC-1 .. RC-5), root-caused by live confirm-by-toggle 2026-08-03
# ==================================================================================================
# Every constant below is grounded from CORE 19.0 SOURCE, never from the fix, so each guard names the
# exact regression signature it refuses and is red-before-green. The measured ratios in the comments
# are the live values from the dark bundle BEFORE the fix.
#
# RC-1. bootstrap_overridden.scss:184-189 re-declares the four Bootstrap dropdown-link scalars and
# only $dropdown-link-color is semantic; the other three are literals off the black/grayscale ramp
# that no surface or text override reaches, so they recompiled unchanged into web.assets_web_dark.
CORE_DROPDOWN_LINK_HOVER_COLOR = BLACK      # :185 $black - the autocomplete active row = 1.20:1
CORE_DROPDOWN_LINK_ACTIVE_COLOR = BLACK     # :188 $black
# RC-2. bootstrap_overridden.scss:199-203 - the list-group action/active tiers.
CORE_LIST_GROUP_ACTION_HOVER_COLOR = "#212529"   # :203 $gray-900 - the systray row = 1.14:1
# RC-3. The $o-grays ramp (primary_variables.scss:50-58) that feeds .bg-N00 through o-print-color
# (bootstrap_review_backend.scss:240-243). .bg-100 is the command-palette footer strip: the muted
# text tier #8EA5A8 on it measured 2.46:1.
CORE_LIGHT_BG_100 = "#f8f9fa"   # $o-gray-100
CORE_LIGHT_BG_200 = "#e9ecef"   # $o-gray-200
CORE_LIGHT_BG_300 = "#dee2e6"   # $o-gray-300
# RC-4. The near-black text + light surface utilities. $o-gray-900 / $o-black / $o-white / $o-gray-100.
CORE_LIGHT_TEXT_DARK = "#212529"
CORE_LIGHT_TEXT_BLACK = BLACK
# ... and the SEPARATE lever RC-4 was actually measured on: bootstrap_review_backend.scss:122-129
# wraps every `.btn-link.text-*` in `o-btn-link-variant($o-gray-600 !important, ...)`, which emits a
# DIRECT `color:` (utils.scss:184-201), not a custom property - so it outranks the .text-dark utility
# whatever --color holds. The mail-activity "Reschedule" toggler measured 3.73:1 at rest.
CORE_LIGHT_BTN_LINK_MUTED = "#6c757d"   # $o-gray-600
# RC-5. Two accent FOREGROUNDS with no dark arm.
#  (a) `.btn-outline-primary` - core ships no "primary" key in $o-btns-bs-outline-override, so the
#      class falls through to `button-outline-variant($theme-colors["primary"])`
#      (bootstrap_review_backend.scss:64-76) and the LABEL compiles the light-mode AA teal #007F8E
#      verbatim = 3.69:1 on the dark panel. That is the "New" button of every form view
#      (form_controller.xml:9) and the kanban "Load more..." control.
#  (b) $o-theme-text-colors (primary_variables.scss:92-97) is core's OWN WCAG-tuning seam for the
#      contextual TEXT utilities - four values tuned for a WHITE page. `.text-danger` (the cog-menu
#      "Delete") measured 3.76:1; the other three sit at 3.71-3.85:1.
CORE_LIGHT_TEXT_DANGER = "#d23f3a"
CORE_LIGHT_TEXT_SUCCESS = "#008818"
CORE_LIGHT_TEXT_INFO = "#0180a5"
CORE_LIGHT_TEXT_WARNING = "#9a6b01"
CORE_LIGHT_THEME_TEXT_COLORS = {
    "danger": CORE_LIGHT_TEXT_DANGER,
    "success": CORE_LIGHT_TEXT_SUCCESS,
    "info": CORE_LIGHT_TEXT_INFO,
    "warning": CORE_LIGHT_TEXT_WARNING,
}

# A hover / selection BAND must be perceptible without becoming a slab. Expressed as a contrast band
# rather than a pinned hex so a tuning pass need not edit the guard. The floor is anchored on light
# mode's own relationship - core's `rgba($black, .08)` composites to ~#EBEBEB on white = 1.19:1 - so
# a dark band that clears it is at least as visible as the light one users already accept. The
# ceiling rejects a bright slab (the same intent as DARK_ACTIVE_FILL_MAX_GLARE above).
DARK_STATE_BAND_MIN_CONTRAST = 1.15
DARK_STATE_BAND_MAX_CONTRAST = 3.0

# --- Element models for RC-1 .. RC-5, transcribed from core's own markup + generated selectors -----
# Bootstrap emits the dropdown-link scalars as runtime custom properties on `.dropdown-menu`
# (lib/bootstrap/scss/_dropdown.scss:37-40; $prefix is '' in Odoo, so the names carry no bs- prefix),
# and `.dropdown-item` reads them (_dropdown.scss:191/198). The ancestor pool is deliberately minimal
# so an unscoped rule always applies and no view-specific rule is admitted.
#
# The modelled menu is a BOOTSTRAP-NATIVE `.dropdown-menu`, deliberately NOT an OWL
# `.o-dropdown--menu`, and the distinction is load-bearing. Core zeroes the native hover/active
# effects for OWL menus and drives the highlight from a JS-managed `.focus` class instead
# (core/dropdown/dropdown.scss:81-90, its own comment: "Remove default active/hover effects so it's
# only controlled via the .focus class") - so inside an `.o-dropdown--menu` a `:hover` item resolves
# `background-color: transparent` at (0,3,0) no matter what the tokens hold. That path reads the SAME
# `$dropdown-link-hover-bg` scalar on `.dropdown-item.focus` (:88), and viin_backend_theme then
# overrides it with a translucent teal wash - a different module's surface, guarded in that module.
# What RC-1's tokens govern directly is the native shape: `.dropdown-item:hover` / `.active`
# (lib/bootstrap/scss/_dropdown.scss:191/198), which is what the html_editor toolbars, the
# model-field-selector popover and utils.scss' o-nocontent dropdown all render.
DROPDOWN_MENU_CLASSES = frozenset({"dropdown-menu"})
DROPDOWN_MENU_ANCESTORS = frozenset({"o_web_client"})
DROPDOWN_ITEM_CLASSES = frozenset({"dropdown-item"})
DROPDOWN_ITEM_ANCESTORS = DROPDOWN_MENU_ANCESTORS | DROPDOWN_MENU_CLASSES
# Bootstrap's list-group: `--list-group-action-hover-color` / `--list-group-active-*` are declared on
# `.list-group` (_list-group.scss:15-22) and read by the item (`.list-group-item-action:hover`,
# `.list-group-item.active`). The systray Activity/Messaging menu is the surface RC-2 was measured on.
LIST_GROUP_CLASSES = frozenset({"list-group"})
LIST_GROUP_ANCESTORS = frozenset({"o_web_client"})
LIST_GROUP_ITEM_ACTION_CLASSES = frozenset({"list-group-item", "list-group-item-action"})
LIST_GROUP_ITEM_ACTIVE_CLASSES = frozenset({"list-group-item", "list-group-item-action", "active"})
LIST_GROUP_ITEM_ANCESTORS = LIST_GROUP_ANCESTORS | LIST_GROUP_CLASSES
# A bare utility class in ordinary webclient content - what any addon, snippet or Studio author types.
# No view-type class in the pool, so a view-scoped rule is correctly excluded and the guard measures
# the GENERIC utility, which is what the defect is about.
UTILITY_ANCESTORS = frozenset({"o_web_client", "o_action_manager", "o_view_controller"})
# form_controller.xml:9 - `<button class="btn btn-outline-primary o_form_button_create">New</button>`,
# inside the control panel. It is not a sibling-gated element, so no previous sibling is modelled.
FORM_NEW_BUTTON_CLASSES = frozenset({"btn", "btn-outline-primary", "o_form_button_create"})
FORM_NEW_BUTTON_ANCESTORS = frozenset({
    "o_web_client", "o_action_manager", "o_view_controller", "o_form_view", "o_control_panel",
    "o_cp_buttons", "d-flex",
})
# The black-on-light PILL exceptions RC-3/RC-4 must NOT reach. All three carry their own bg+text pair:
# `.o_tag.o_tag_color_N` through o-print-color on BOTH axes (tags_list.scss:6-13), `.badge` +
# `.o_badge_color_N` through direct `!important` declarations (badge.scss:3-6), and `.text-bg-300`
# through core's own color-contrast() label (bootstrap_review_backend.scss:245-247). Colour index 1 is
# representative: the loop generates every index from the same two adjust-color() expressions.
TAG_PILL_CLASSES = frozenset({"o_tag", "o_tag_color_1"})
BADGE_PILL_CLASSES = frozenset({"badge", "o_badge_color_1"})
TEXT_BG_300_CLASSES = frozenset({"text-bg-300"})
# autocomplete.xml:54-66 - the HIGHLIGHTED suggestion row of an m2o/m2m/o2m dropdown. Carrying none
# of the `o_m2o_start_typing` / `o_m2o_no_result` / `o_m2o_dropdown_option` variant classes is
# load-bearing: autocomplete.scss ships four competing `ui-state-active` rules and the most specific
# one belongs to the "start typing..." PLACEHOLDER row, whose `background: none` must not be mistaken
# for this row's band.
AUTOCOMPLETE_ACTIVE_ROW_CLASSES = frozenset({
    "dropdown-item", "ui-menu-item-wrapper", "text-truncate", "ui-state-active",
})
AUTOCOMPLETE_ACTIVE_ROW_ANCESTORS = frozenset({
    "o_web_client", "o-autocomplete", "o-autocomplete--dropdown-menu", "ui-widget", "show",
    "o-autocomplete--dropdown-item", "ui-menu-item", "d-block",
})


# ==================================================================================================
# WCAG contrast - implemented from the specification, deliberately NOT from any product formula
# ==================================================================================================
def _colour_spellings(hex_colour):
    """Every lower-cased form the SCSS compiler can emit a given ``#rrggbb`` colour as.

    Two are enough for this cluster: the hex literal itself, and the bare ``r,g,b`` triplet Odoo's
    `to-rgb()` produces when a colour is fed to the o-print-color mixin (`RGBA(127,66,130, var(...))`)
    - which is exactly how the group-by facet paints, so a hex-only search would miss it. The triplet
    is emitted without spaces by the asset minifier, so both spacings are returned."""
    red, green, blue = (int(hex_colour.lstrip("#")[start:start + 2], 16) for start in (0, 2, 4))
    return (
        hex_colour.lower(),
        "%d,%d,%d" % (red, green, blue),
        "%d, %d, %d" % (red, green, blue),
    )


def _relative_luminance(hex_colour):
    """Relative luminance per WCAG 2.1 "relative luminance" definition.

    Transcribed from the W3C specification (sRGB linearisation threshold 0.03928, gamma 2.4,
    coefficients 0.2126 / 0.7152 / 0.0722) - an EXTERNAL formula, so a readability assertion built
    on it can never degenerate into comparing production logic against itself."""
    channels = []
    for offset in (1, 3, 5):
        srgb = int(hex_colour[offset:offset + 2], 16) / 255.0
        channels.append(srgb / 12.92 if srgb <= 0.03928 else ((srgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast_ratio(hex_a, hex_b):
    """Contrast ratio between two normalised #rrggbb colours, per WCAG 2.1 SC 1.4.3."""
    lum_a, lum_b = _relative_luminance(hex_a), _relative_luminance(hex_b)
    lighter, darker = max(lum_a, lum_b), min(lum_a, lum_b)
    return (lighter + 0.05) / (darker + 0.05)


def _composite_over(fg_hex, bg_hex, alpha):
    """Alpha-composite ``fg_hex`` at ``alpha`` over an opaque ``bg_hex``; return the #rrggbb result.

    Standard source-over compositing (out = fg*a + bg*(1-a)) per channel. A CSS ``opacity`` on an
    element blends the whole element - text included - over whatever it sits on, so the pixel a user
    actually reads is this composite, NOT the un-faded text colour. Contrast must be measured on the
    composite; a raw #EDF4F5-vs-#111B1E check would ignore the fade entirely."""
    fg = [int(fg_hex[o:o + 2], 16) for o in (1, 3, 5)]
    bg = [int(bg_hex[o:o + 2], 16) for o in (1, 3, 5)]
    out = [round(fg[i] * alpha + bg[i] * (1 - alpha)) for i in range(3)]
    return "#%02x%02x%02x" % tuple(out)


# ==================================================================================================
# Compiled-CSS parsing
# ==================================================================================================
# A single non-nested "selectors { body }" rule. [^{}] keeps each match to one rule, so rules
# nested inside @media / @supports wrappers are still captured individually (the wrapper prelude
# itself never matches, because no '}' precedes its inner '{').
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
# Odoo's asset pipeline (odoo/addons/base/models/assetsbundle.py, preprocess_css()) prepends a
# "/* <source-file-path> */" banner before each per-source-file fragment, in both debug and
# minified mode. _RULE_RE has no comment awareness, so a banner glues itself to the following
# selector group; strip it before parsing selectors.
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
# Tokens inside one compound selector. Pseudo-classes/elements FIRST so ':not(...)' and '::before'
# win over the bare-identifier branch; the nested-paren alternative keeps ':not(.a:hover)' intact.
_COMPOUND_TOKEN_RE = re.compile(
    r"::?[\w-]+(?:\((?:[^()]|\([^()]*\))*\))?"   # :pseudo-class(...) / ::pseudo-element
    r"|\.[\w-]+"                                  # .class
    r"|\#[\w-]+"                                  # #id
    r"|\[[^\]]*\]"                                # [attr=value]
    r"|\*"                                        # universal
    r"|[\w-]+"                                    # type selector
)
# A whole value that is exactly one var() reference, with an optional fallback.
_VAR_RE = re.compile(r"^var\(\s*(--[\w-]+)\s*(?:,\s*(.*))?\)$", re.DOTALL)
_HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
# Core emits colours as `RGBA(0, 187, 206, var(--bg-opacity, 1))` via the o-print-color mixin, so
# a hex-only reader would silently see "no colour" there and report a false pass.
# Channels are matched as DECIMALS, not integers: Sass colour functions legitimately produce
# fractional channels and the compiler emits them verbatim. `adjust-color()` on the $o-colors chips is
# the live case - `.o_tag.o_tag_color_1` compiles
# `RGBA(255, 155.5, 155.5, var(--bg-opacity, 1))` - and an integer-only pattern silently reported "no
# colour" there, i.e. a real surface the guards could not see at all. Values are rounded to the nearest
# integer channel by _normalize_colour, which is what a browser rasterises anyway.
_FUNC_RGB_RE = re.compile(
    r"\brgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)", re.IGNORECASE,
)

# Pseudo-classes that describe a STATE or a structural position of the element rather than a
# different element. A compound is a candidate only if every one of these it carries was declared
# by the caller, so a `:hover` rule never pollutes the resting-state answer.
_STATE_PSEUDO_CLASSES = frozenset({
    "hover", "focus", "focus-visible", "focus-within", "active", "disabled", "enabled",
    "checked", "first-child", "last-child", "only-child", "first-of-type", "last-of-type",
})


def _normalize_colour(value):
    """Return ``value``'s first colour as a lower-case #rrggbb string, or None.

    Accepts #rgb, #rrggbb, #rrggbbaa and rgb()/rgba() function form so that core's o-print-color
    output and hand-written hexes compare on equal terms."""
    hex_match = _HEX_RE.search(value)
    if hex_match:
        digits = hex_match.group(0)[1:].lower()
        if len(digits) == 3:
            digits = "".join(digit * 2 for digit in digits)
        return "#" + digits[:6]
    func_match = _FUNC_RGB_RE.search(value)
    if func_match:
        channels = tuple(
            max(0, min(255, int(round(float(group))))) for group in func_match.groups()
        )
        return "#%02x%02x%02x" % channels
    return None


def _alpha_of(value):
    """Return the alpha channel (0.0-1.0) a colour value carries, or 1.0 when fully opaque / unknown.

    Detects the two forms core emits a translucent colour in: ``rgba(r, g, b, a)`` / ``hsla(...)``
    and the 8-digit ``#rrggbbaa`` hex. A plain #rrggbb, an rgb()/hsl() triple, or a non-colour value
    is treated as opaque (1.0). Needed because _normalize_colour deliberately DROPS alpha (it answers
    "which hue"), so a token whose defect is opacity - e.g. the navbar entry text
    ``rgba(255,255,255,.9)`` - would look like an AA-passing #FFFFFF to the contrast machinery. This
    reads the alpha so that opacity defect is observable."""
    if value is None:
        return 1.0
    func_alpha = re.search(
        r"\b(?:rgba|hsla)\([^)]*,\s*([0-9]*\.?[0-9]+)\s*%?\s*\)", value, re.IGNORECASE
    )
    if func_alpha:
        alpha = float(func_alpha.group(1))
        return alpha / 100.0 if "%" in func_alpha.group(0) else alpha
    hex_match = _HEX_RE.search(value)
    if hex_match and len(hex_match.group(0)) == 9:      # #rrggbbaa
        return int(hex_match.group(0)[7:9], 16) / 255.0
    return 1.0


def _split_compounds(selector):
    """Split a complex selector into ``[(combinator, compound), ...]``, left to right.

    The first entry's combinator is ``""``; descendant is ``" "``. Parenthesis/bracket depth is
    tracked so whitespace inside ``:not(.a .b)`` or ``[title="a b"]`` never splits a compound."""
    compounds, buffer, combinator, depth, index = [], "", "", 0, 0
    while index < len(selector):
        char = selector[index]
        if char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        if depth == 0 and char in " \t\n>+~":
            run_end, seen = index, " "
            while run_end < len(selector) and selector[run_end] in " \t\n>+~":
                if selector[run_end] in ">+~":
                    seen = selector[run_end]
                run_end += 1
            if buffer:
                compounds.append((combinator, buffer))
                buffer, combinator = "", seen
            index = run_end
            continue
        buffer += char
        index += 1
    if buffer:
        compounds.append((combinator, buffer))
    return compounds


def _compound_classes(compound):
    """Return the set of class names a compound requires POSITIVELY (``:not()`` args excluded)."""
    return {
        token[1:]
        for token in _COMPOUND_TOKEN_RE.findall(compound)
        if token.startswith(".")
    }


def _compound_state_pseudo_classes(compound):
    """Return the state/structural pseudo-classes a compound requires directly.

    The state axis dual of :func:`_compound_classes` (``:not()`` args and pseudo-ELEMENTS
    excluded). Used to reject an ANCESTOR compound the class-only ancestor model can never satisfy -
    see :func:`_matches_element`."""
    found = set()
    for token in _COMPOUND_TOKEN_RE.findall(compound):
        if token.startswith(":not(") or token.startswith("::"):
            continue
        if token.startswith(":"):
            name = token[1:].split("(", 1)[0]
            if name in _STATE_PSEUDO_CLASSES:
                found.add(name)
    return found


def _compound_matches(compound, classes, states, pseudo_element):
    """Whether one compound selector matches an element with ``classes`` in ``states``.

    Deliberately CONSERVATIVE about what it does not model: a compound carrying an id, an
    attribute selector or a type selector returns False, and so does an unrecognised pseudo-class.
    Every surface asserted in this file is styled purely through classes, so the only effect is
    that exotic competitor rules are ignored - which is stated in each test's docstring rather
    than hidden.

    Pseudo-element matching is STRICT IN BOTH DIRECTIONS: a query for ``::before`` is matched only
    by a compound that names that pseudo-element, and a compound naming one never matches a query
    for the originating element. Without the first half, `.btn` would be treated as a competitor
    for a ``::before`` background, which it is not (background-color does not inherit into a
    pseudo-element box)."""
    matched_pseudo_element = False
    for token in _COMPOUND_TOKEN_RE.findall(compound):
        if token.startswith("::"):
            if token[2:] != (pseudo_element or ""):
                return False
            matched_pseudo_element = True
        elif token.startswith(":not("):
            # :not() fails the match as soon as ANY of its arguments matches the element. Its
            # arguments constrain the ORIGINATING element, never the pseudo-element box, so the
            # pseudo-element is not propagated into the recursion.
            for argument in token[5:-1].split(","):
                if _compound_matches(argument.strip(), classes, states, None):
                    return False
        elif token.startswith(":"):
            name = token[1:].split("(", 1)[0]
            if name in ("before", "after"):          # legacy single-colon pseudo-element form
                if name != (pseudo_element or ""):
                    return False
                matched_pseudo_element = True
            elif name in _STATE_PSEUDO_CLASSES:
                if name not in states:
                    return False
            else:
                return False
        elif token.startswith("."):
            if token[1:] not in classes:
                return False
        elif token == "*":
            continue
        else:
            return False                              # id, [attr] or type selector - not modelled
    if pseudo_element and not matched_pseudo_element:
        return False
    # Require at least one positive class so the universal-ish rules of unrelated components are
    # never treated as competitors.
    return bool(_compound_classes(compound))


def _specificity(selector):
    """Return the CSS specificity ``(ids, classes, types)`` of a complete selector."""
    ids = classes = types = 0
    for _combinator, compound in _split_compounds(selector):
        for token in _COMPOUND_TOKEN_RE.findall(compound):
            if token.startswith("#"):
                ids += 1
            elif token.startswith("::"):
                types += 1
            elif token.startswith(":not("):
                # :not() itself adds nothing; its most specific argument counts.
                arguments = [_specificity(arg.strip()) for arg in token[5:-1].split(",")]
                best = max(arguments) if arguments else (0, 0, 0)
                ids, classes, types = ids + best[0], classes + best[1], types + best[2]
            elif token.startswith(":"):
                classes += 1 if token[1:].split("(", 1)[0] not in ("before", "after") else 0
                types += 1 if token[1:].split("(", 1)[0] in ("before", "after") else 0
            elif token.startswith(".") or token.startswith("["):
                classes += 1
            elif token != "*":
                types += 1
    return (ids, classes, types)


def _iter_rules(css):
    """Yield ``(order, selector, body)`` for every selector of every compiled rule, in order."""
    for order, (selector_group, body) in enumerate(_RULE_RE.findall(css)):
        for selector in _COMMENT_RE.sub("", selector_group).split(","):
            selector = selector.strip()
            if selector:
                yield order, selector, body


def _declarations(body, prop_names):
    """Return ``[(value, is_important), ...]`` for ``prop_names`` in declaration order."""
    found = []
    for declaration in body.split(";"):
        name, separator, value = declaration.partition(":")
        if not separator or name.strip() not in prop_names:
            continue
        value = value.strip()
        important = value.lower().endswith("!important")
        if important:
            value = value[: -len("!important")].rstrip()
        found.append((value, important))
    return found


def _winning_declaration(css, element, prop_names):
    """Return the value the cascade computes for ``prop_names`` on ``element``, or None.

    ``element`` is a dict with the keys accepted by :func:`_matches_element`. Ordering follows the
    CSS cascade for a single origin with no inline styles: ``!important`` beats normal, then
    higher specificity, then later source order, then later declaration order within a rule."""
    best_key, best_value = None, None
    for order, selector, body in _iter_rules(css):
        if not _matches_element(selector, element):
            continue
        for decl_order, (value, important) in enumerate(_declarations(body, prop_names)):
            key = (important, _specificity(selector), order, decl_order)
            if best_key is None or key > best_key:
                best_key, best_value = key, value
    return best_value


def _matches_element(selector, element):
    """Whether ``selector``'s SUBJECT (its right-most compound) matches the modelled element.

    Ancestor and sibling context are approximated rather than fully evaluated, which is enough for
    the class-only selectors these surfaces use:
    * every ANCESTOR compound's positive classes must be a subset of ``element["ancestors"]`` - so
      an unscoped rule always applies and a rule scoped to another context never does. A compound
      linked to the next one by a sibling combinator (``+``/``~``) is a SIBLING, not an ancestor,
      and is skipped by that check. An ancestor compound additionally gated on a state/structural
      pseudo-class (``fieldset:disabled``, ``:first-child`` ...) is rejected: the ancestor pool
      carries no state or position, and the surfaces asserted here are resting, enabled elements
      that are never inside such a context - so treating it as a phantom ancestor would let a rule
      like ``fieldset:disabled .btn`` (0,2,1) outrank the real ``.btn:hover`` (0,2,0);
    * when the SUBJECT is reached by a sibling combinator, the compound before it is matched
      against ``element["prev_sibling"]`` - the classes on the element's immediately preceding
      sibling, transcribed from the same core template as ``classes``. This check is
      UNCONDITIONAL: a sibling-gated rule must not apply to an element that has no such sibling.
      Bootstrap ships several (`.btn-check:checked + .btn`, `.btn-check:focus-visible + .btn`)
      whose subject carries no state pseudo-class at all, so skipping the check silently let them
      outrank the plain `.btn` rule on specificity and hand a resting-state query the PRESSED
      value. An element with no preceding sibling models it as an empty set, which correctly
      fails every sibling-gated rule.

    Combinator KIND (descendant vs child), ancestor ORDER, sibling chains deeper than one hop, and
    @media context are not distinguished. Each of those would only ADD candidate rules, and an
    extra candidate makes a guard fail loudly rather than pass silently."""
    compounds = _split_compounds(selector)
    if not compounds:
        return False
    if not _compound_matches(
        compounds[-1][1], element["classes"], element.get("states", frozenset()),
        element.get("pseudo_element"),
    ):
        return False
    ancestors = element["ancestors"]
    for position, (_combinator, compound) in enumerate(compounds[:-1]):
        if compounds[position + 1][0] in ("+", "~"):
            continue                                  # sibling of the chain, not an ancestor of it
        if not _compound_classes(compound) <= ancestors:
            return False
        if _compound_state_pseudo_classes(compound):
            # The ancestor pool is a set of CLASSES with no element state or structural position,
            # so an ancestor compound gated on a state/structural pseudo-class can never be
            # confirmed - and every surface asserted here is a resting, enabled element that is not
            # in that context. This is the ancestor-side dual of the subject rule in
            # _compound_matches (every state pseudo the SUBJECT carries must be declared by the
            # caller). Without it, a class-less ancestor compound passed the subset check above
            # vacuously: Bootstrap ships `fieldset:disabled .btn` in the SAME selector group as
            # `.btn:disabled` / `.btn.disabled`, and its `fieldset:disabled` compound carries no
            # class, so `_compound_classes(...) <= ancestors` was trivially True. `fieldset:disabled
            # .btn` (specificity 0,2,1) then outranked the real `.btn:hover` (0,2,0) and handed
            # every hovered/resting `.btn` facet the button's `--btn-disabled-bg` (which mirrors the
            # base fill) instead of the `--btn-hover-bg` deep rung - a phantom competitor, since a
            # search facet is never rendered inside a disabled <fieldset>.
            return False
    if compounds[-1][0] in ("+", "~"):
        prev_sibling = element.get("prev_sibling") or frozenset()
        if not _compound_matches(compounds[-2][1], prev_sibling, frozenset(), None):
            return False
    return True


def _computed_value(css, chain, prop_names, depth=6):
    """Resolve ``prop_names`` on ``chain[0]``, following ``var()`` through the ancestor ``chain``.

    ``chain`` is the element and its styling ancestors, innermost first. CSS custom properties
    INHERIT, so an unresolved ``var(--x)`` is looked up on the element itself and then outwards -
    which is how ``--o-stat-text-color``, set on .o-form-buttonbox, reaches the .o_stat_value
    descendant that reads it. A ``var()`` with no declaration anywhere falls back to its own
    fallback argument, exactly as a browser does."""
    value = _winning_declaration(css, chain[0], prop_names)
    while value is not None and depth > 0:
        var_match = _VAR_RE.match(value.strip())
        if not var_match:
            return value
        name, fallback = var_match.group(1), var_match.group(2)
        resolved = None
        for ancestor in chain:
            candidate = _winning_declaration(css, ancestor, (name,))
            if candidate is not None:
                resolved = candidate
                break
        value = resolved if resolved is not None else fallback
        depth -= 1
    return value


def _winning_topbar_mark_declaration(css, prop_names):
    """Cascade winner of ``prop_names`` for the debug db-name ``<mark>`` in the user menu, or None.

    The db name renders inside `.o_user_menu .oe_topbar_name mark` - a BARE <mark> with no class
    (user_menu.xml:12). The generic cascade resolver (:func:`_winning_declaration`) deliberately
    refuses type-only subjects (`_compound_matches` needs a positive class), so it cannot answer for
    a <mark>. This focused reader restores just enough cascade to resolve THIS element: among every
    compiled rule whose subject compound is exactly ``mark`` and whose selector scopes it under
    ``.oe_topbar_name``, pick the winner by (!important, specificity, source order, declaration
    order) - the same ordering _winning_declaration uses. It reads the COMPILED bundle, so a token
    rename inside the value still resolves; it returns None when no such rule exists (the pre-fix
    state), which is what makes the item-6b guard red-before-green."""
    best_key, best_value = None, None
    for order, selector, body in _iter_rules(css):
        compounds = _split_compounds(selector)
        if not compounds or compounds[-1][1].strip() != "mark":
            continue
        if "oe_topbar_name" not in selector:
            continue
        for decl_order, (value, important) in enumerate(_declarations(body, prop_names)):
            key = (important, _specificity(selector), order, decl_order)
            if best_key is None or key > best_key:
                best_key, best_value = key, value
    return best_value


def _winning_burger_entry_declaration(css, prop_names):
    """Cascade winner of ``prop_names`` for a RESTING burger/app-menu sidebar menu row, or None.

    A menu row inside the panel is a bare ``<li>`` / ``<button>`` carrying no class of its own
    (navbar.xml:47/:65), and core styles it BY TYPE: ``.o_burger_menu_content { li, button {
    @include o-hover-text-color(rgba($o-burger-base-color, .8), $o-burger-base-color) } }``
    (burger_menu.scss:59-61). The generic resolver deliberately refuses type-only subjects
    (:func:`_compound_matches` requires a positive class), so it cannot answer for these rows. This
    focused reader restores just enough cascade for THEM - the same
    (!important, specificity, source order, declaration order) ordering :func:`_winning_declaration`
    uses - among rules whose subject compound is exactly ``li``/``button`` and whose selector scopes
    it under ``.o_burger_menu_content``. Mirrors :func:`_winning_topbar_mark_declaration`, which
    solves the same type-only-subject problem for the debug ``<mark>``.

    RESTING state only: the mixin's hover arm compiles subjects ``li:hover`` / ``li.focus``, which do
    not equal ``li`` and are therefore skipped - so a hover value can never be mistaken for the
    resting one. Returns None when no such rule exists (core moved or renamed the component), which
    surfaces as a loud failure rather than a silent pass."""
    best_key, best_value = None, None
    for order, selector, body in _iter_rules(css):
        compounds = _split_compounds(selector)
        if not compounds or compounds[-1][1].strip() not in ("li", "button"):
            continue
        if "o_burger_menu_content" not in selector:
            continue
        for decl_order, (value, important) in enumerate(_declarations(body, prop_names)):
            key = (important, _specificity(selector), order, decl_order)
            if best_key is None or key > best_key:
                best_key, best_value = key, value
    return best_value


def _strip_type_selectors(selector):
    """Rewrite ``selector`` with bare TYPE tokens dropped from every compound, or None.

    :func:`_compound_matches` deliberately refuses any compound carrying a type selector, so a
    class-only element model is never over-claimed. That is the right default, but it makes a whole
    family of core rules unreadable - the ones whose SUBJECT is an element plus a class, like
    autocomplete's ``a.ui-state-active``. Dropping the type token turns such a compound into the
    class-only shape the matcher understands, while the class and state constraints - the parts that
    decide whether the rule applies to the modelled element at all - are kept intact.

    A compound made ONLY of a type selector (a bare ``a`` ancestor) is omitted rather than kept: the
    ancestor pool is a set of classes with no element names, so such a compound can never be
    confirmed, and :func:`_matches_element` already treats a class-less ancestor compound as
    vacuously satisfied. Omitting it therefore preserves existing behaviour and errs toward ADMITTING
    a competitor, which makes a guard fail loudly rather than pass silently. Returns None when the
    SUBJECT itself is type-only, which no assertion here models."""
    parts, compounds = [], _split_compounds(selector)
    for index, (combinator, compound) in enumerate(compounds):
        kept = [
            token for token in _COMPOUND_TOKEN_RE.findall(compound)
            if token[0] in ".#:[*"
        ]
        if not kept:
            if index == len(compounds) - 1:
                return None                       # type-only SUBJECT - not modelled
            continue                              # type-only ANCESTOR - unconfirmable, so omitted
        parts.append(("" if not parts else (combinator or " "), "".join(kept)))
    return "".join("%s%s" % (combinator, compound) for combinator, compound in parts) or None


def _winning_declaration_for_typed_subject(css, element, prop_names, scope):
    """Cascade winner of ``prop_names`` on an element whose core rules use a TYPE+class subject.

    Same (!important, specificity, source order, declaration order) ordering as
    :func:`_winning_declaration`, and specificity is measured on the ORIGINAL selector so type
    tokens still count - only the MATCHING step goes through :func:`_strip_type_selectors`.
    ``scope`` is a substring every candidate selector must contain, which keeps the scan inside one
    component instead of the whole bundle.

    WHY THIS EXISTS RATHER THAN A THIRD HAND-ROLLED READER. The two readers above
    (:func:`_winning_topbar_mark_declaration`, :func:`_winning_burger_entry_declaration`) each solve
    the type-only-subject problem for one element by matching a fixed subject NAME and ignoring class
    context entirely. That shortcut is wrong for the autocomplete row, and provably so: the component
    ships FOUR competing `ui-state-active` rules, and the highest-specificity one is
    `.o-autocomplete .ui-menu-item.o_m2o_start_typing a.ui-state-active { background: none }`
    (autocomplete.scss:42-46) - a rule for the "start typing..." PLACEHOLDER row. A name-only reader
    hands that `background: none` to a query about the real suggestion row, which is a different
    element. Honouring the class context is what excludes it."""
    best_key, best_value = None, None
    for order, selector, body in _iter_rules(css):
        if scope not in selector:
            continue
        modelled = _strip_type_selectors(selector)
        if not modelled or not _matches_element(modelled, element):
            continue
        for decl_order, (value, important) in enumerate(_declarations(body, prop_names)):
            key = (important, _specificity(selector), order, decl_order)
            if best_key is None or key > best_key:
                best_key, best_value = key, value
    return best_value


def _autocomplete_active_row_declaration(css, prop_names):
    """Cascade winner of ``prop_names`` for the HIGHLIGHTED m2o/m2m autocomplete suggestion, or None.

    Element transcribed from autocomplete.xml:54-66 - the row is
    ``<a class="dropdown-item ui-menu-item-wrapper text-truncate ui-state-active">`` inside
    ``<li class="o-autocomplete--dropdown-item ui-menu-item d-block">`` inside
    ``<ul class="o-autocomplete--dropdown-menu ui-widget show">`` inside ``<div class="o-autocomplete">``.
    It carries NONE of the `o_m2o_start_typing` / `o_m2o_no_result` / `o_m2o_dropdown_option` variant
    classes, so the rules gated on those are correctly excluded.

    This row is why RC-1 is a COMPILE-TIME defect and not only a custom-property one: core reads the
    pair as raw Sass here (autocomplete.scss:25-26 `color: $dropdown-link-hover-color;
    background-color: $dropdown-link-hover-bg`), so no runtime `--dropdown-link-*` re-point can reach
    it - only the Sass SCALAR can. Returns None if core moves or renames the component, which fails
    loudly rather than passing."""
    element = {
        "classes": AUTOCOMPLETE_ACTIVE_ROW_CLASSES,
        "ancestors": AUTOCOMPLETE_ACTIVE_ROW_ANCESTORS,
        "prev_sibling": frozenset(),
    }
    return _winning_declaration_for_typed_subject(css, element, prop_names, "o-autocomplete")


@tagged("post_install", "-at_install")
class BrandCascadeCompileTest(TransactionCase):

    # ----------------------------------------------------------------------------------------
    # Bundle access
    # ----------------------------------------------------------------------------------------
    def _backend_bundle(self):
        """Return the compiled web.assets_backend AssetsBundle.

        Grounded 19.0 API (OSM + odoo/addons/base/models/assetsbundle.py): ``ir.qweb
        ._get_asset_bundle(bundle_name, css=True, js=False)`` returns an AssetsBundle whose
        ``.css()`` yields the compiled ir.attachment recordset and whose ``.css_errors`` list is
        populated by that call. See tests/test_brand_color_compile.py for the same API contract."""
        return self.env["ir.qweb"]._get_asset_bundle(BACKEND_BUNDLE, css=True, js=False)

    def _compiled_backend_css(self, bundle=None):
        """Compile the backend bundle and return its CSS payload as decoded text."""
        bundle = bundle or self._backend_bundle()
        attachments = bundle.css() or self.env["ir.attachment"]
        return "".join(
            (attachment.raw or b"").decode("utf-8", "replace") for attachment in attachments
        )

    def _css(self):
        css = self._compiled_backend_css()
        self.assertTrue(
            css.strip(),
            "web.assets_backend compiled to empty CSS - the bundle did not build, so none of the "
            "restored cascade surfaces can be verified.",
        )
        return css

    def _compiled_css(self, bundle_name):
        """Compile ANY asset bundle by name and return its CSS payload as decoded text.

        Generalises _compiled_backend_css to the dark bundle (web.assets_web_dark) so the dark arm
        resolves through the SAME machinery. Fails loudly on an empty payload - a bundle that did
        not build cannot verify any surface. Same 19.0 API contract as _backend_bundle."""
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

    def _root_custom_prop_values(self, css, prop):
        """Return every value declared for the custom property ``--<prop>`` on a :root rule.

        CSS custom properties like --link-color are declared on :root, which the cascade
        _matches_element intentionally does not model (it needs a positive class). This is the
        :root-scoped reader (mirrors test_brand_color_compile.py) used for token-level dark-arm
        checks. The ``\\s*:`` guard keeps ``--link-color`` from matching ``--link-color-rgb``."""
        pattern = re.compile(r"--%s\s*:\s*([^;}]+)" % re.escape(prop))
        values = []
        for _order, selector, body in _iter_rules(css):
            if selector != ":root":
                continue
            for match in pattern.finditer(body):
                values.append(match.group(1).strip().lower())
        return values

    def _assert_flat_teal_available(self):
        self.assertIsNotNone(
            VIINDOO_THEME_COLOR,
            "VIINDOO_THEME_COLOR must be defined in "
            "viin_brand_common/controllers/webmanifest.py (the single Python brand-hex SSOT).",
        )
        return VIINDOO_THEME_COLOR.lower()

    def _brand_secondary_ssot(self):
        """Return the LIGHT $o-brand-secondary hex, READ from the module's own token SSOT.

        Re-literalising the purple in every guard would let the tests and brand_variables.scss drift
        apart silently; every "purple" assertion here anchors on this one reader instead
        (ODOO-AI-ETHOS #11). The "purple, NOT teal" claim is always asserted separately against the
        teal ladder, so pointing $o-brand-secondary at a teal would still fail loudly."""
        with open(BRAND_VARIABLES_SCSS, encoding="utf-8") as scss_file:
            value = _resolve_scss_hex(scss_file.read(), "$o-brand-secondary")
        self.assertIsNotNone(
            value,
            "$o-brand-secondary must be declared in %s - it is the SSOT for every META/STRUCTURE "
            "purple surface in this cluster." % os.path.basename(BRAND_VARIABLES_SCSS),
        )
        return value.lower()

    def _resolve_colour(self, css, chain, prop_names, surface):
        """Resolve a property to a normalised colour, failing loudly when nothing paints it."""
        value = _computed_value(css, chain, prop_names)
        self.assertIsNotNone(
            value,
            "No compiled declaration of %s applies to %s. The surface is unstyled, so the "
            "restored brand cascade cannot be reaching it." % ("/".join(prop_names), surface),
        )
        colour = _normalize_colour(value)
        self.assertIsNotNone(
            colour,
            "%s resolves %s to %r, which carries no colour. The restored token was dropped or "
            "core moved the surface to a different lever."
            % (surface, "/".join(prop_names), value),
        )
        return colour

    # ----------------------------------------------------------------------------------------
    # 1. Navbar menu-entry chrome states
    # ----------------------------------------------------------------------------------------
    def test_navbar_menu_entry_interactive_states_use_deep_chrome_rung(self):
        """Hovered, focused, pressed and open navbar menu entries must render the deep chrome rung.

        Core paints all four states from two `!default` variables it declares in
        navbar.variables.scss - $o-navbar-entry-bg--hover and --active - defaulting to
        rgba($o-black, .08), which composites to a barely perceptible ~#007583 over the teal
        navbar. brand_variables.scss sets both to $o-viin-chrome-deep FIRST, so core's later
        `!default` no-ops. Entry text is white, so the hovered surface must clear WCAG AA; the deep
        rung reaches 7.5:1 while the decorative brand teal only reaches 2.33:1.

        WOULD FAIL IF REVERTED: dropping either variable from brand_variables.scss restores core's
        translucent black, which carries no hex at all - the resolver then returns the rgba()
        default and every assertion below reports it."""
        flat_brand_teal = self._assert_flat_teal_available()
        css = self._css()

        # The two hooks core reads are never DECLARED anywhere in the bundle, only read, so the
        # var() fallback - which is what the restored variables feed - is genuinely load-bearing.
        # If a later core release starts declaring them, the fallback stops rendering and this
        # guard must be re-grounded rather than silently passing on a dead token.
        navbar_state_hooks = (
            "--NavBar-entry-backgroundColor--hover", "--NavBar-entry-backgroundColor--active",
        )
        for hook in navbar_state_hooks:
            self.assertNotIn(
                hook + ":", css.replace(" ", ""),
                "Core now DECLARES %s, so the compiled var() fallback that carries the restored "
                "chrome rung no longer renders. Re-ground this guard against the new lever."
                % hook,
            )

        # Every navbar chrome state, as a real element inside .o_menu_sections.
        states_under_test = (
            ("hovered menu entry", {"o_nav_entry"}, frozenset({"hover"})),
            ("focused menu entry", {"o_nav_entry"}, frozenset({"focus"})),
            ("pressed menu entry", {"o_nav_entry"}, frozenset({"active"})),
            ("hovered section dropdown toggle", {"dropdown-toggle"}, frozenset({"hover"})),
            # .dropdown.show.dropdown-toggle also covers the OPEN overflow ("More") menu, which
            # core renders inside .o_menu_sections (navbar.xml, web.NavBar.SectionsMenu.MoreDropdown).
            ("open section/overflow dropdown", {"dropdown", "show", "dropdown-toggle"}, frozenset()),
        )
        for label, classes, states in states_under_test:
            element = {
                "classes": frozenset(classes),
                "states": states,
                "ancestors": NAVBAR_ANCESTORS,
                "prev_sibling": frozenset({"o_nav_entry", "dropdown-toggle"}),
            }
            colour = self._resolve_colour(css, [element], BACKGROUND_PROPS, label)
            self.assertEqual(
                colour, CHROME_DEEP,
                "The %s compiled to %s instead of the deep chrome rung %s. The restored "
                "$o-navbar-entry-bg--hover / --active levers were dropped or reverted, so core's "
                "translucent-black default (or the decorative teal) is painting the state."
                % (label, colour, CHROME_DEEP),
            )
            self.assertNotEqual(
                colour, flat_brand_teal,
                "The %s compiled to the flat DECORATIVE brand teal %s (2.33:1 with the white "
                "entry text). Chrome states must use the deep rung %s (7.5:1)."
                % (label, flat_brand_teal, CHROME_DEEP),
            )
            self.assertNotEqual(
                colour, CHROME_BASE,
                "The %s compiled to the chrome BASE %s, which is the navbar's own resting "
                "surface - a hovered entry would be indistinguishable from the bar behind it. "
                "It must darken to the deep rung %s." % (label, CHROME_BASE, CHROME_DEEP),
            )

        self.assertGreaterEqual(
            _contrast_ratio(CHROME_DEEP, WHITE), WCAG_AA_NORMAL_TEXT,
            "The deep chrome rung %s must clear WCAG AA (>= %.1f:1) against the white navbar entry "
            "text; it measures %.2f:1."
            % (CHROME_DEEP, WCAG_AA_NORMAL_TEXT, _contrast_ratio(CHROME_DEEP, WHITE)),
        )

    # ----------------------------------------------------------------------------------------
    # 2. Search facet - field / filter
    # ----------------------------------------------------------------------------------------
    def test_search_facet_field_and_filter_render_chrome_base_on_white(self):
        """Field and filter search facets must render the chrome base with white text.

        v19 core renders these two facet types as `btn btn-primary`. 18.0 painted every facet with
        one uniform brand chrome; the restore pins the Bootstrap button custom properties the .btn
        variant already reads (--btn-bg / --btn-border-color / --btn-color and their hover and
        active rungs) on the label element itself, so the sibling .o_facet_remove close button
        keeps its red.

        The resting and hovered backgrounds are asserted as the value the cascade actually
        computes - Bootstrap's `.btn { background-color: var(--btn-bg) }` and
        `.btn:hover { background-color: var(--btn-hover-bg) }` resolved through the pinned tokens.
        The PRESSED rung is asserted on the `--btn-active-bg` token instead: core reaches that
        state through `.btn:first-child:active` / `.btn.active` / `.btn.show`, which turn on
        structural position and runtime-only classes rather than anything a static compiled
        stylesheet can pin to this element. The token is the lever Bootstrap reads for all of
        them, so it is the honest observable there - and it still fails if the deep rung is lost.

        The three rungs share ONE declaration block in brand_cascade.scss but are consumed by
        THREE distinct core selectors, so the resting query must not pick up a pressed value.
        Guarding that is why the resolver models each element's previous sibling: Bootstrap ships
        `.btn-check:checked + .btn` (specificity 0,3,0) whose subject carries no state pseudo-class
        at all, and the facet label's real previous sibling - the `:hover` overlay div of
        search_bar.xml line 14 - is what rules it out.

        WOULD FAIL IF REVERTED: on the HOVER and PRESSED rungs, immediately - removing the facet
        rule hands those states back to the $o-btns-bs-override primary map, whose hover is #00515B
        and whose pressed state is the near-white #E6F2F4, neither of which is the deep chrome
        rung. The RESTING rung is deliberately NOT the load-bearing assertion here: it is
        co-guarded by that same $o-btns-bs-override lever (already covered by
        tests/test_brand_color_compile.py), so it would survive a revert of this rule. It is still
        asserted, because it is what makes the facet a chrome surface at all and it is the anchor
        for the WCAG check below."""
        flat_brand_teal = self._assert_flat_teal_available()
        css = self._css()
        element = {
            "classes": FACET_LABEL_FIELD, "ancestors": SEARCH_FACET_ANCESTORS,
            "prev_sibling": FACET_LABEL_PREV_SIBLING,
        }
        hovered = dict(element, states=frozenset({"hover"}))

        resting_bg = self._resolve_colour(
            css, [element], BACKGROUND_PROPS, "resting field/filter search facet"
        )
        self.assertEqual(
            resting_bg, CHROME_BASE,
            "A field/filter search facet compiled to %s instead of the chrome base %s. The "
            "restored --btn-* pinning on .o_searchview_facet_label was dropped, so core's "
            ".btn-primary tokens (keyed off the decorative $o-brand-primary) are painting it."
            % (resting_bg, CHROME_BASE),
        )
        self.assertNotEqual(
            resting_bg, flat_brand_teal,
            "A field/filter search facet compiled to the flat DECORATIVE brand teal %s, which is "
            "only 2.33:1 against its white label text." % flat_brand_teal,
        )

        resting_fg = self._resolve_colour(
            css, [element], ("color",), "resting field/filter search facet text"
        )
        self.assertEqual(
            resting_fg, WHITE,
            "A field/filter search facet's text compiled to %s instead of white. The restored "
            "--btn-color pinning was dropped; the chrome base is a dark surface and needs white "
            "text." % resting_fg,
        )
        self.assertGreaterEqual(
            _contrast_ratio(resting_bg, resting_fg), WCAG_AA_NORMAL_TEXT,
            "A field/filter search facet renders %s text on %s - %.2f:1, below the WCAG AA "
            "normal-text threshold of %.1f:1."
            % (resting_fg, resting_bg, _contrast_ratio(resting_bg, resting_fg),
               WCAG_AA_NORMAL_TEXT),
        )

        hovered_bg = self._resolve_colour(
            css, [hovered], BACKGROUND_PROPS, "hovered field/filter search facet"
        )
        self.assertEqual(
            hovered_bg, CHROME_DEEP,
            "A hovered field/filter search facet compiled to %s instead of the deep chrome rung "
            "%s. The restored --btn-hover-bg pinning was dropped or reverted."
            % (hovered_bg, CHROME_DEEP),
        )

        pressed_token = self._resolve_colour(
            css, [element], ("--btn-active-bg",), "pressed field/filter search facet token"
        )
        self.assertEqual(
            pressed_token, CHROME_DEEP,
            "The pressed-state token --btn-active-bg on a field/filter search facet compiled to "
            "%s instead of the deep chrome rung %s." % (pressed_token, CHROME_DEEP),
        )

        border = self._resolve_colour(
            css, [element], ("--btn-border-color",), "field/filter search facet border token"
        )
        self.assertEqual(
            border, CHROME_BASE,
            "A field/filter search facet's border token compiled to %s; it must match the chrome "
            "base fill %s so the pill reads as one branded unit." % (border, CHROME_BASE),
        )

    # ----------------------------------------------------------------------------------------
    # 3. Search facet - groupBy (BOTH shapes)
    # ----------------------------------------------------------------------------------------
    def test_search_facet_groupby_is_the_structure_purple_not_the_filter_teal(self):
        """A groupBy search facet must render the STRUCTURE purple - distinct from a filter facet.

        OWNER DECISION 2026-08-03 (supersedes the earlier uniform-teal restore). The colour law in
        brand_variables.scss reads TEAL = ACT / PURPLE = META-STRUCTURE. A field or filter facet
        NARROWS the record set, which is an action, so it stays teal (guarded by the sibling test
        above). A groupBy facet narrows nothing - it re-ORGANISES what is already there - so it is
        the purple one, and the two facet kinds become distinguishable at a glance. A test asserting
        the groupBy facet is TEAL would now be WRONG; do not "restore" it without an owner reversal.

        THE DISCRIMINATOR IS TYPE-DRIVEN, NOT A DOMAIN PROXY. The v19 template branches directly on
        the facet type - `'text-bg-action': facet.type == 'groupBy'` (search_bar.xml:20) - so that
        class IS the predicate. The `.o_facet_with_domain` class two lines up (:7,
        `{o_facet_with_domain: facet.domain}`) also happens to be absent on a groupBy today, but it
        keys on facet.domain, so it would leak onto any future domain-less non-groupBy facet and
        would stop matching the moment a groupBy gained a domain.

        BOTH core shapes are asserted. web.SearchBar.Facets gives a groupBy `text-bg-action` ALWAYS
        and additionally a bare `btn` when env.searchModel.canOrderByCount - so a rule keyed on
        `:not(.btn)` paints the facet on most views and silently stops the moment a view offers
        order-by-count.

        THE SECOND TRAP IS IMPORTANCE, NOT SPECIFICITY: core generates .text-bg-action through the
        o-print-color mixin (scss/functions.scss:48-51), which emits
        `background-color: var(--background-color) !important` and `color: var(--color) !important`.
        An `!important` beats a normal declaration at ANY specificity, so a plain background-color /
        color here never renders - the override must feed the two custom properties core's own
        important declarations read.

        >>> OWNER REVISION 2026-08-03 (same day, supersedes the dark arm): LIGHT MODE ONLY. <<<
        The first version of this fix gave the purple a dark arm so the facet could stay purple in
        web.assets_web_dark. The owner reversed it - purple is wrong on a dark canvas - so the two
        arms of this test now assert OPPOSITE things, deliberately:
          light  the facet IS the brand purple #7F4282 under a #FFFFFF label (6.99:1), and is a
                 different colour from a filter facet;
          dark   the facet is NOT purple (neither #7F4282 nor the retired #B589B8) and IS core's own
                 untouched `.text-bg-action` paint - the rule must not be emitted into that bundle at
                 all, which is what `@if not $o-viin-dark-bundle` guarantees.
        The dark arm is a real GUARD, not a deletion: it fails if a purple-in-dark regression returns
        AND it fails if the surface lands on some third colour of ours.

        WOULD FAIL IF REVERTED: reverting to the chrome base fails the "not the filter teal"
        assertion in the light arm; re-adding a dark purple arm fails both dark refusals; forgetting
        to guard the FRAME rule while guarding the label rule fails the dark frame assertion."""
        flat_brand_teal = self._assert_flat_teal_available()
        expected_light_purple = self._brand_secondary_ssot()

        shapes = (
            ("groupBy facet (plain)", FACET_LABEL_GROUPBY),
            ("groupBy facet (orderable, core also adds `btn`)", FACET_LABEL_GROUPBY_ORDERABLE),
        )
        arms = (
            ("light", BACKEND_BUNDLE),
            ("dark", DARK_BUNDLE),
        )
        for arm, bundle_name in arms:
            css = self._compiled_css(bundle_name)
            # The FILTER facet is resolved through the same machinery in the same bundle, so the
            # "these two are different" claim is measured, not assumed.
            filter_element = {
                "classes": FACET_LABEL_FIELD, "ancestors": SEARCH_FACET_ANCESTORS,
                "prev_sibling": FACET_LABEL_PREV_SIBLING,
            }
            filter_background = self._resolve_colour(
                css, [filter_element], BACKGROUND_PROPS, "filter facet (%s arm)" % arm
            )
            self.assertEqual(
                filter_background, CHROME_BASE,
                "The FILTER facet compiled to %s instead of the chrome base %s in the %s bundle. "
                "Narrowing is an ACT and must stay teal - the group-by re-point leaked onto it."
                % (filter_background, CHROME_BASE, arm),
            )

            for label, classes in shapes:
                label = "%s [%s arm]" % (label, arm)
                element = {
                    "classes": classes, "ancestors": SEARCH_FACET_ANCESTORS,
                    "prev_sibling": FACET_LABEL_PREV_SIBLING,
                }
                background = self._resolve_colour(css, [element], BACKGROUND_PROPS, label)
                if arm == "light":
                    self.assertNotEqual(
                        background, flat_brand_teal,
                        "A %s compiled to the flat DECORATIVE brand teal %s (2.33:1) - core's "
                        "untouched .text-bg-action paint, so the override is not reaching this "
                        "shape." % (label, flat_brand_teal),
                    )
                    self.assertNotEqual(
                        background, filter_background,
                        "A %s compiled to %s - the SAME colour as a filter facet. Group-by is "
                        "STRUCTURE and filter is ACT; collapsing them onto one hue is the defect "
                        "this guard exists for. Either the rule no longer keys on .text-bg-action "
                        "(so it misses this shape) or it declares plain background-color and loses "
                        "to core's `background-color: var(--background-color) !important`."
                        % (label, background),
                    )
                    # Anchor the light arm on the token SSOT, so the resolver is proven to be
                    # reading $o-brand-secondary and not some unrelated purple.
                    self.assertEqual(
                        background, expected_light_purple,
                        "A %s compiled to %s instead of the brand secondary %s "
                        "($o-brand-secondary)." % (label, background, expected_light_purple),
                    )
                else:
                    # THE INVERTED DARK ARM (owner revision 2026-08-03). The claim flips from "this
                    # facet is purple" to "this facet has NO accent of ours": the rule must not be
                    # emitted at all, so the facet resolves core's own .text-bg-action paint. Both
                    # purples are refused by name, and the positive half asserts the CORE default -
                    # which is what makes this a guard rather than a deletion. (A group-by and a
                    # filter facet are consequently BOTH teal in dark, in two different shades; that
                    # is the price of "default look", and it is the owner's call - which is why the
                    # "must differ from the filter facet" assertion is light-only.)
                    self.assertNotEqual(
                        background, expected_light_purple,
                        "A %s compiled the brand purple %s in the DARK bundle. The purple accent is "
                        "LIGHT-ONLY from 2026-08-03: the rule must be inside "
                        "`@if not $o-viin-dark-bundle` so it never reaches web.assets_web_dark."
                        % (label, expected_light_purple),
                    )
                    self.assertNotEqual(
                        background, RETIRED_DARK_PURPLE,
                        "A %s compiled the RETIRED dark purple %s. That arm of $o-brand-secondary "
                        "was deleted on the owner's instruction - do not restore it."
                        % (label, RETIRED_DARK_PURPLE),
                    )
                    self.assertEqual(
                        background, flat_brand_teal,
                        "A %s compiled %s in the dark bundle, but the DEFAULT the owner asked for is "
                        "core's own `.text-bg-action` paint - $o-action, i.e. the flat brand teal "
                        "%s, whose color-contrast() foreground is self-contrasting. Getting "
                        "something else here means a dark accent of ours is still being emitted."
                        % (label, background, flat_brand_teal),
                    )

                foreground = self._resolve_colour(css, [element], ("color",), label + " text")
                ratio = _contrast_ratio(background, foreground)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "A %s renders %s text on %s - %.2f:1, below the WCAG AA normal-text threshold "
                    "of %.1f:1. Light: the label is $o-white on the purple (6.99:1). Dark: the pair "
                    "is core's own, so a failure here means something re-tinted the facet without "
                    "re-tinting its label."
                    % (label, foreground, background, ratio, WCAG_AA_NORMAL_TEXT),
                )

            # The values half of the pill. In LIGHT it follows its label onto the purple so the facet
            # reads as ONE unit (core draws no border there at all; the teal frame is this module's).
            # In DARK the label reverts to core's teal, so the frame must revert WITH it - a purple
            # frame around a teal label would be the same "two components, not one pill" defect in
            # reverse, and is the signature of guarding the label rule but forgetting the frame rule.
            frame_element = {
                "classes": FACET_VALUES,
                "ancestors": SEARCH_FACET_ANCESTORS,
                "prev_sibling": FACET_LABEL_GROUPBY,
            }
            frame = self._resolve_colour(
                css, [frame_element], ("border-color", "border"),
                "group-by facet frame (%s arm)" % arm,
            )
            if arm == "light":
                self.assertNotEqual(
                    frame, CHROME_BASE,
                    "The group-by facet's .o_facet_values frame compiled the teal chrome base %s in "
                    "the %s bundle while its label is purple - a purple label inside a teal frame "
                    "reads as two components, not one pill. The `.text-bg-action + .o_facet_values` "
                    "rule must stay AFTER the generic `:not(.btn-favourite)` frame rule (equal "
                    "specificity, source order decides)." % (CHROME_BASE, arm),
                )
                self.assertEqual(
                    frame, expected_light_purple,
                    "The group-by facet frame compiled %s instead of the brand secondary %s."
                    % (frame, expected_light_purple),
                )
            else:
                self.assertNotIn(
                    frame, (expected_light_purple, RETIRED_DARK_PURPLE),
                    "The group-by facet frame compiled the purple %s in the DARK bundle. Its label "
                    "is core-default there, so the frame rule must carry the SAME "
                    "`@if not $o-viin-dark-bundle` guard as the label rule." % frame,
                )
                self.assertEqual(
                    frame, CHROME_BASE,
                    "The group-by facet frame compiled %s in the dark bundle; with the purple gone "
                    "the generic `:not(.btn-favourite)` chrome-base frame %s is what should stand."
                    % (frame, CHROME_BASE),
                )

    # ----------------------------------------------------------------------------------------
    # 4. Search facet - favourite is a DELIBERATE exception
    # ----------------------------------------------------------------------------------------
    def test_search_facet_favourite_keeps_native_yellow_and_no_teal_frame(self):
        """A saved-favourite search facet must keep core's yellow and receive no chrome frame.

        OWNER DECISION 2026-07-24, deliberate deviation from 18.0. 18.0 flattened every facet type
        to one teal chrome, which also erased the "this is a saved filter" affordance. v19 renders
        a favourite facet as `btn btn-favourite`, generated by button-variant($o-main-favorite-color)
        - gold #f3cc00. The restore keeps that, so every teal-ifying facet rule carries a
        `:not(.btn-favourite)` guard, INCLUDING the .o_facet_values frame (a teal frame hugging a
        yellow label would contradict the decision just as loudly as repainting the label).

        A test asserting the favourite facet IS teal would be WRONG. Do not "fix" this test to
        match 18.0 - fix the code only if the owner reverses the decision.

        WOULD FAIL IF REVERTED: dropping any `:not(.btn-favourite)` guard makes the module's
        higher-specificity facet rule match this element too, and its chrome colours immediately
        show up as the computed value here."""
        css = self._css()
        chrome_ladder = (CHROME_BASE, CHROME_DEEP)
        label_element = {
            "classes": FACET_LABEL_FAVORITE, "ancestors": SEARCH_FACET_ANCESTORS,
            "prev_sibling": FACET_LABEL_PREV_SIBLING,
        }

        # The label itself - resting, hovered, and the token Bootstrap reads when pressed.
        checks = (
            ("resting", [dict(label_element)], BACKGROUND_PROPS),
            ("hovered", [dict(label_element, states=frozenset({"hover"}))], BACKGROUND_PROPS),
            ("pressed (token)", [dict(label_element)], ("--btn-active-bg",)),
        )
        for state_label, chain, props in checks:
            colour = self._resolve_colour(
                css, chain, props, "%s favourite search facet" % state_label
            )
            self.assertNotIn(
                colour, chrome_ladder,
                "The %s favourite search facet compiled to the chrome colour %s. The owner "
                "decision is that a saved filter keeps its native v19 yellow affordance in BOTH "
                "resting and interactive states - a `:not(.btn-favourite)` guard was dropped from "
                "the facet rules in brand_cascade.scss." % (state_label, colour),
            )

        # Non-vacuity: the favourite facet must still be painted by SOMETHING (core's gold button
        # variant), otherwise the assertions above would pass on an unstyled element.
        resting = self._resolve_colour(
            css, [label_element], BACKGROUND_PROPS, "resting favourite search facet"
        )
        self.assertNotEqual(
            resting, WHITE,
            "The favourite search facet compiled to plain white - core's .btn-favourite variant "
            "is not reaching it, so this guard would be vacuous. Re-ground it against the lever "
            "core now uses for saved-filter facets.",
        )

        # The sibling frame: .o_facet_values is the immediate next sibling of the label in
        # web.SearchBar.Facets, so a `+` rule is what draws it. Core draws no border at all.
        frame_element = {
            "classes": FACET_VALUES,
            "ancestors": SEARCH_FACET_ANCESTORS,
            "prev_sibling": FACET_LABEL_FAVORITE,
        }
        frame = _computed_value(css, [frame_element], ("border", "border-color"))
        frame_colour = _normalize_colour(frame) if frame else None
        self.assertNotIn(
            frame_colour, chrome_ladder,
            "The values half of a saved-favourite facet compiled a chrome border (%s). Core draws "
            "no border there, and the owner decision keeps the favourite facet 100%% native - the "
            "`:not(.btn-favourite)` guard on the .o_facet_values rule was dropped." % frame_colour,
        )

    # ----------------------------------------------------------------------------------------
    # 5. Statusbar current arrow
    # ----------------------------------------------------------------------------------------
    def test_statusbar_current_arrow_outline_is_chrome_base_over_a_light_fill(self):
        """The current statusbar arrow must be outlined in the chrome base over a light fill.

        v19 routes both the arrow OUTLINE and the arrow NOTCH through one token,
        --o-statusbar-border-active, which statusbar_field.scss seeds from the "secondary" entry of
        $o-btns-bs-override (`active-border: $o-component-active-border`) and then paints the
        .o_arrow_button_current::before clip-path with. brand_variables.scss sets
        $o-component-active-border to the chrome base, restoring exactly the pair 18.0 coloured
        (border-color plus the &:before notch).

        The FILL is deliberately NOT teal-ified: $o-action is untouched, so
        $o-component-active-bg stays a light tint carrying dark text - 18.0's own light-fill /
        dark-outline split. Asserting the fill is teal would be WRONG; what is asserted instead is
        the invariant that makes the split correct - the fill stays readable under dark text.

        WOULD FAIL IF REVERTED: dropping $o-component-active-border returns it to $o-action, i.e.
        the decorative teal, which the outline assertion rejects by name."""
        flat_brand_teal = self._assert_flat_teal_available()
        css = self._css()
        status_element = {
            "classes": frozenset({"o_statusbar_status"}), "ancestors": STATUSBAR_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        outline = self._resolve_colour(
            css, [status_element], ("--o-statusbar-border-active",), "statusbar current arrow"
        )
        self.assertEqual(
            outline, CHROME_BASE,
            "The statusbar current-arrow outline/notch token compiled to %s instead of the chrome "
            "base %s. $o-component-active-border was dropped from brand_variables.scss, so it fell "
            "back to core's $o-action." % (outline, CHROME_BASE),
        )
        self.assertNotEqual(
            outline, flat_brand_teal,
            "The statusbar current-arrow outline compiled to the flat DECORATIVE brand teal %s - "
            "a 2.33:1 outline that barely separates the current step from its neighbours."
            % flat_brand_teal,
        )

        # The notch: core paints .o_arrow_button_current::before from the same token, which is what
        # makes this ONE token cover BOTH surfaces 18.0 coloured separately. Asserting it keeps the
        # guard honest if core ever splits the notch onto its own lever.
        notch_element = {
            # statusbar_field.xml:36-41 - `btn btn-secondary o_arrow_button` plus the state
            # class. The two Bootstrap classes are load-bearing for this guard: without them the
            # model silently excludes every `.btn` rule instead of ruling it out on the merits.
            "classes": frozenset({
                "btn", "btn-secondary", "o_arrow_button", "o_arrow_button_current",
            }),
            "states": frozenset({"disabled"}),
            "pseudo_element": "before",
            "ancestors": STATUSBAR_ANCESTORS,
            # statusbar_field.xml renders a row of sibling arrow buttons.
            "prev_sibling": frozenset({"btn", "btn-secondary", "o_arrow_button"}),
        }
        notch = self._resolve_colour(
            css, [notch_element, status_element], BACKGROUND_PROPS, "statusbar current-arrow notch"
        )
        self.assertEqual(
            notch, CHROME_BASE,
            "The statusbar current-arrow NOTCH compiled to %s instead of the chrome base %s. Core "
            "no longer paints .o_arrow_button_current::before from --o-statusbar-border-active, so "
            "the single restored token no longer covers both 18.0 surfaces." % (notch, CHROME_BASE),
        )

        fill = self._resolve_colour(
            css, [status_element], ("--o-statusbar-background-active",),
            "statusbar current-arrow fill",
        )
        self.assertNotIn(
            fill, (CHROME_BASE, CHROME_DEEP),
            "The statusbar current-arrow FILL compiled to the chrome colour %s. $o-action must "
            "stay untouched so the arrow keeps 18.0's light fill with dark text - only the "
            "outline tier darkens." % fill,
        )
        self.assertGreaterEqual(
            _contrast_ratio(fill, BLACK), WCAG_AA_NORMAL_TEXT,
            "The statusbar current-arrow fill %s only reaches %.2f:1 against the dark step label, "
            "below the WCAG AA normal-text threshold of %.1f:1 - it is no longer the light tint "
            "the light-fill/dark-outline split depends on."
            % (fill, _contrast_ratio(fill, BLACK), WCAG_AA_NORMAL_TEXT),
        )

    # ----------------------------------------------------------------------------------------
    # 6. Selected settings tab
    # ----------------------------------------------------------------------------------------
    def test_selected_settings_tab_indicator_is_chrome_base(self):
        """The selected Settings tab must show a chrome-base inset indicator.

        settings_form_view.scss draws it as `box-shadow: inset 2px 0 0 $o-component-active-border`
        - the v19 equivalent of 18.0's `inset 3px 0 0 $brand-primary`. It shares the single
        $o-component-active-border lever with the statusbar arrow, which is why this is a separate
        test: the two surfaces must be able to fail independently if core ever re-routes one of
        them onto a different variable.

        WOULD FAIL IF REVERTED: without the restored lever the indicator falls back to $o-action,
        i.e. the 2.33:1 decorative teal, which is rejected by name below."""
        flat_brand_teal = self._assert_flat_teal_available()
        css = self._css()
        element = {
            "classes": frozenset({"tab", "selected"}),
            "ancestors": SETTINGS_TAB_ANCESTORS, "prev_sibling": frozenset({"tab"}),
        }

        indicator = self._resolve_colour(
            css, [element], ("box-shadow",), "selected settings tab indicator"
        )
        self.assertEqual(
            indicator, CHROME_BASE,
            "The selected Settings tab indicator compiled to %s instead of the chrome base %s - "
            "$o-component-active-border was dropped from brand_variables.scss."
            % (indicator, CHROME_BASE),
        )
        self.assertNotEqual(
            indicator, flat_brand_teal,
            "The selected Settings tab indicator compiled to the flat DECORATIVE brand teal %s, "
            "which barely reads as a selection marker at 2.33:1." % flat_brand_teal,
        )

    # ----------------------------------------------------------------------------------------
    # 7. Stat values are PURPLE - deliberately not teal
    # ----------------------------------------------------------------------------------------
    def test_stat_value_renders_brand_secondary_purple_with_a_teal_icon(self):
        """A stat-button value must render the brand SECONDARY purple, paired with a teal icon.

        OWNER DECISION 2026-07-24, FAITHFUL-18.0. 18.0's `.o_stat_value { color: $o-brand-primary }`
        looks teal until it is read against the 18.0 variable file, where the two names were
        inverted: `$o-brand-primary: $o-enterprise-primary-color` = the brand SECONDARY purple. So
        the stat value was a purple accent, paired with a teal icon. v19 core reads the colour from
        `var(--o-stat-text-color, $o-brand-primary)` whose fallback is the 2.33:1 decorative teal,
        so the restore pins the custom property on .o-form-buttonbox.

        A test asserting the stat value is TEAL would be WRONG - it would encode the 18.0 name
        inversion as if it were an 18.0 intent.

        The expected purple is READ from the module's own $o-brand-secondary token rather than
        re-literalised here, so this test cannot drift from the SSOT; the "purple, not teal" claim
        is then asserted independently against both teals, so pointing $o-brand-secondary at a teal
        would still fail.

        WOULD FAIL IF REVERTED: dropping the .o-form-buttonbox pin restores core's decorative-teal
        var() fallback, which is rejected by name; repainting it with the chrome base (the value
        the design doc originally suggested, before the owner ruling) is rejected too."""
        flat_brand_teal = self._assert_flat_teal_available()
        with open(BRAND_VARIABLES_SCSS, encoding="utf-8") as scss_file:
            expected_purple = _resolve_scss_hex(scss_file.read(), "$o-brand-secondary")
        self.assertIsNotNone(
            expected_purple,
            "$o-brand-secondary must be declared in %s - it is the SSOT for the stat-value colour."
            % os.path.basename(BRAND_VARIABLES_SCSS),
        )
        expected_purple = expected_purple.lower()

        css = self._css()
        # .o_bottom_sheet is core's own sanctioned exception (it pins --o-stat-text-color to
        # currentColor on mobile so the value follows the sheet); the desktop form sheet is the
        # surface under test, so that context is excluded from the resolution.
        buttonbox = {
            # button_box.xml:5
            "classes": frozenset({
                "o-form-buttonbox", "d-print-none", "position-relative", "d-flex", "w-md-auto",
                "o_not_full",
            }),
            "ancestors": BUTTONBOX_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        stat_value = {
            "classes": frozenset({"o_stat_value"}), "ancestors": STAT_BUTTON_ANCESTORS,
            "prev_sibling": frozenset({"o_stat_text"}),   # button_box.xml renders text then value
        }

        value_colour = self._resolve_colour(
            css, [stat_value, buttonbox], ("color",), "stat-button value"
        )
        self.assertEqual(
            value_colour, expected_purple,
            "A stat-button value compiled to %s instead of the brand secondary purple %s "
            "($o-brand-secondary). The --o-stat-text-color pin on .o-form-buttonbox was dropped, "
            "so core's decorative-teal var() fallback is painting it."
            % (value_colour, expected_purple),
        )
        self.assertNotEqual(
            value_colour, flat_brand_teal,
            "A stat-button value compiled to the flat DECORATIVE brand teal %s - core's untouched "
            "var(--o-stat-text-color, $o-brand-primary) fallback, only 2.33:1 on the form sheet."
            % flat_brand_teal,
        )
        self.assertNotEqual(
            value_colour, CHROME_BASE,
            "A stat-button value compiled to the chrome base %s. The owner ruled this surface "
            "FAITHFUL-18.0 purple, not teal - see this test's docstring before changing it."
            % CHROME_BASE,
        )
        self.assertGreaterEqual(
            _contrast_ratio(value_colour, WHITE), WCAG_AA_NORMAL_TEXT,
            "A stat-button value renders %s on the white form sheet - %.2f:1, below the WCAG AA "
            "normal-text threshold of %.1f:1."
            % (value_colour, _contrast_ratio(value_colour, WHITE), WCAG_AA_NORMAL_TEXT),
        )

        # The pairing: 18.0 showed a teal ICON above a purple VALUE. Core reads the icon from
        # var(--o-stat-button-color, $primary) and $primary is already the chrome base, so the
        # pairing holds for free - assert it so a future change to $primary cannot silently
        # collapse the two halves onto one colour.
        icon = {
            "classes": frozenset({"o_button_icon"}), "ancestors": STAT_BUTTON_ANCESTORS,
            "prev_sibling": frozenset(),                  # the icon is the first child
        }
        icon_colour = self._resolve_colour(css, [icon, buttonbox], ("color",), "stat-button icon")
        self.assertEqual(
            icon_colour, CHROME_BASE,
            "The stat-button ICON compiled to %s instead of the chrome base %s, breaking 18.0's "
            "teal-icon / purple-value pairing." % (icon_colour, CHROME_BASE),
        )
        self.assertNotEqual(
            icon_colour, value_colour,
            "The stat-button icon and value both compiled to %s. 18.0 paired a teal icon with a "
            "purple value; collapsing them onto one colour loses that pairing." % icon_colour,
        )

    # ----------------------------------------------------------------------------------------
    # 8. Progress-bar trough
    # ----------------------------------------------------------------------------------------
    def test_progressbar_trough_carries_the_brand_wash_not_core_white(self):
        """The progress-bar trough must carry the near-white brand wash, not core's plain white.

        18.0 tinted the track with a near-white wash of the brand palette; v19 core leaves it at
        $o-view-background-color, i.e. plain white, which makes an empty bar indistinguishable
        from the sheet behind it. Pure decoration - the track carries no text (the value renders in
        the sibling .o_progressbar_value) and the filled portion is core's .bg-primary - so the
        wash is asserted for PRESENCE and hue, not for contrast.

        Both a fixed expected value and a hue invariant are asserted: the exact wash is the current
        contract, while the invariant (a near-white tint leaning to the brand's cyan side) states
        the rule that survives a future tweak of the mix percentage. The expected value is a fixed
        design constant, NOT a Python re-implementation of the Sass mix() that produces it.

        WOULD FAIL IF REVERTED: removing the rule from brand_cascade.scss returns the trough to
        core's #ffffff, which fails both the equality and the "not plain white" assertion."""
        css = self._css()
        element = {
            # progress_bar_field.xml:7
            "classes": frozenset({"o_progress", "align-middle", "overflow-hidden"}),
            "ancestors": PROGRESSBAR_ANCESTORS,
            "prev_sibling": frozenset({"o_progressbar_title"}),
        }

        trough = self._resolve_colour(css, [element], BACKGROUND_PROPS, "progress-bar trough")
        self.assertNotEqual(
            trough, CORE_PROGRESS_TROUGH,
            "The progress-bar trough compiled to core's plain white %s - the brand wash rule was "
            "dropped from brand_cascade.scss, so an empty bar disappears into the sheet."
            % CORE_PROGRESS_TROUGH,
        )
        self.assertEqual(
            trough, PROGRESS_TROUGH_WASH,
            "The progress-bar trough compiled to %s instead of the brand wash %s."
            % (trough, PROGRESS_TROUGH_WASH),
        )

        red, green, blue = (int(trough[offset:offset + 2], 16) for offset in (1, 3, 5))
        self.assertTrue(
            red < green and red < blue and min(red, green, blue) >= 0xE0,
            "The progress-bar trough %s is not a near-white wash of the brand teal (expected a "
            "tint whose red channel is the lowest and whose channels all stay above 0xE0, so the "
            "track reads as a faint brand-tinted surface behind the filled portion)." % trough,
        )

    # ----------------------------------------------------------------------------------------
    # 9. The bundle itself
    # ----------------------------------------------------------------------------------------
    def test_backend_bundle_compiles_without_css_errors(self):
        """web.assets_backend must compile clean - no Sass error, and no cached error payload.

        Every assertion in this file reads the compiled bundle, so a silent compile failure is the
        one regression that could make them all meaningless. On a Sass error Odoo does not raise:
        assetsbundle.py's css() collects the message into ``css_errors`` and serves the PREVIOUS
        stylesheet with an error banner appended, so the backend keeps rendering with stale styles
        and every colour assertion above would happily read the old, correct values.

        Both halves are needed. ``css_errors`` reports the compile that just happened, but css()
        returns early when a compiled attachment is already cached, in which case the list stays
        empty even though the cached payload is an error payload - so the payload markers are
        checked too.

        WOULD FAIL IF REVERTED: any malformed SCSS in brand_variables.scss or brand_cascade.scss -
        an undefined variable, a Sass function banned by tests/test_asset_upgrade.py, a bad
        map-merge - lands here as a non-empty css_errors list and an error banner in the payload."""
        bundle = self._backend_bundle()
        css = self._compiled_backend_css(bundle)

        self.assertFalse(
            bundle.css_errors,
            "web.assets_backend reported SCSS compile errors: %s. The restored cascade files "
            "(brand_variables.scss / brand_cascade.scss) must compile clean - on an error Odoo "
            "silently serves the previous stylesheet, so the backend looks fine while every "
            "brand token is stale." % "; ".join(bundle.css_errors),
        )
        self.assertTrue(
            css.strip(),
            "web.assets_backend compiled to an empty payload - the bundle did not build.",
        )
        for marker in ("## CSS error message ##", "css_error_message", "A css error occured"):
            self.assertNotIn(
                marker, css,
                "The compiled web.assets_backend payload carries the error marker %r that "
                "assetsbundle.py appends when a Sass compile fails. A previously cached error "
                "payload is being served, so the backend is rendering stale styles." % marker,
            )

    # ----------------------------------------------------------------------------------------
    # 10. Content colour-palette SCOPE - the brand teal must NOT bleed into o-color-1
    # ----------------------------------------------------------------------------------------
    def test_content_palette_o_color_1_stays_core_aubergine_while_chrome_stays_teal(self):
        """The editor/website CONTENT swatch o-color-1 must render core aubergine, not the brand teal.

        brand_variables.scss sets `$o-enterprise-color: #00BBCE` (teal) because chrome and the portal
        chatter path require it. But core seeds the CONTENT palette from that same variable at Sass
        compile time (html_editor.variables.scss:121 `'o-color-1': $o-enterprise-color`), so without a
        fix the user-facing swatch o-color-1 bleeds to teal - breaking the core Hoot tests
        (html_editor color_selector.test.js and website builder image_shape.test.js) that assert
        rgb(113, 75, 103) = #714B67. brand_palette_reset.scss map-merges the CONTENT palette base-1
        o-color-1 back to core aubergine AFTER html_editor builds it, touching no chrome token.

        This asserts the OBSERVABLE: .bg-o-color-1, generated by html_editor.common.scss:515-520
        (web.assets_backend) from the active palette's o-color-1 entry - the exact class the core
        Hoot tests read. And it proves the fix is SCOPED in the same compiled bundle: a chrome facet
        still renders the brand chrome teal, and the decorative brand teal still exists elsewhere.

        RED BEFORE GREEN: on the current (bleeding) code .bg-o-color-1 compiles to the flat brand
        teal #00BBCE, so the equality below fails; it passes only once the content palette is reset.

        WOULD FAIL IF REVERTED: dropping brand_palette_reset.scss (or its append from the manifest)
        returns o-color-1 to $o-enterprise-color = the brand teal, which the equality rejects by
        value and the "not the flat brand teal" assertion rejects by name."""
        # The content palette (and thus .bg-o-color-1) is built by html_editor. When html_editor is
        # not installed there is no palette to bleed into - brand_palette_reset.scss is a deliberate
        # no-op there - so this guard is not applicable and would otherwise fail vacuously on an
        # unstyled swatch. Skip rather than assert nothing. (The configuration this fix targets - the
        # one where the 4 core Hoot tests live - always has html_editor installed.)
        if not self.env["ir.module.module"].search_count(
            [("name", "=", "html_editor"), ("state", "=", "installed")]
        ):
            self.skipTest(
                "html_editor is not installed - no content colour palette is built, so the brand "
                "teal cannot bleed into o-color-1 and there is nothing to guard."
            )
        flat_brand_teal = self._assert_flat_teal_available()
        css = self._css()

        # The content swatch. .bg-o-color-1 is a plain, unscoped utility (bg-variant), so it needs
        # no ancestor context; core paints it !important via the o-print-color / bg-variant mixin,
        # which the resolver's cascade + RGBA() normalisation already handle.
        swatch = {
            "classes": frozenset({"bg-o-color-1"}),
            "ancestors": frozenset(),
            "prev_sibling": frozenset(),
        }
        swatch_colour = self._resolve_colour(
            css, [swatch], BACKGROUND_PROPS, "o-color-1 content swatch (.bg-o-color-1)"
        )
        self.assertEqual(
            swatch_colour, CORE_CONTENT_O_COLOR_1,
            "The CONTENT swatch .bg-o-color-1 compiled to %s instead of core aubergine %s. The "
            "brand teal $o-enterprise-color bled into the content palette (html_editor.variables.scss "
            "seeds base-1 o-color-1 from it) - brand_palette_reset.scss was dropped or its manifest "
            "append was removed, so the swatch is no longer reset to core."
            % (swatch_colour, CORE_CONTENT_O_COLOR_1),
        )
        self.assertNotEqual(
            swatch_colour, flat_brand_teal,
            "The CONTENT swatch .bg-o-color-1 compiled to the flat brand teal %s. o-color-1 is a "
            "user-facing content colour, NOT chrome; it must stay core aubergine %s (this is what "
            "the core color_selector / image_shape Hoot tests assert)."
            % (flat_brand_teal, CORE_CONTENT_O_COLOR_1),
        )
        self.assertNotEqual(
            swatch_colour, ODOO_COMMUNITY_PURPLE,
            "The CONTENT swatch .bg-o-color-1 compiled to Odoo community purple %s - the palette "
            "reset must land on aubergine %s, not the community-edition brand colour."
            % (ODOO_COMMUNITY_PURPLE, CORE_CONTENT_O_COLOR_1),
        )

        # Scoped-fix proof #1: a real chrome surface in the SAME bundle stays the brand chrome teal.
        # If the reset had disturbed a chrome lever, the field/filter facet base would move off
        # CHROME_BASE here.
        facet = {
            "classes": FACET_LABEL_FIELD, "ancestors": SEARCH_FACET_ANCESTORS,
            "prev_sibling": FACET_LABEL_PREV_SIBLING,
        }
        facet_bg = self._resolve_colour(
            css, [facet], BACKGROUND_PROPS, "field/filter search facet (chrome, scope check)"
        )
        self.assertEqual(
            facet_bg, CHROME_BASE,
            "Resetting the content palette disturbed chrome: the field/filter facet compiled to %s "
            "instead of the chrome base %s. The reset must touch ONLY base-1 o-color-1 / theme "
            "beta." % (facet_bg, CHROME_BASE),
        )

        # Scoped-fix proof #2: the decorative brand identity teal must still exist in the bundle -
        # the reset restores a CONTENT swatch, it does not purge the brand.
        self.assertIn(
            flat_brand_teal, css.lower(),
            "The flat brand-identity teal %s vanished from the compiled bundle. The content-palette "
            "reset must not nuke the brand decorative teal - only base-1 o-color-1 returns to core."
            % flat_brand_teal,
        )

    # ----------------------------------------------------------------------------------------
    # 11. DARK ARM (C-6) - brand-secondary readable text clears AA on BOTH the light and dark panel
    # ----------------------------------------------------------------------------------------
    def test_brand_secondary_text_clears_wcag_aa_on_light_and_dark_surfaces(self):
        """The $o-brand-secondary readable-text surfaces must clear WCAG AA in BOTH schemes.

        Three surfaces read the SAME $o-brand-secondary Sass var as readable text: the desktop
        stat-button value AND its label (both via .o-form-buttonbox's --o-stat-text-color, OURS) and
        the mobile form label (.o_xxs_form_view .o_form_label, form_controller.scss:1120, CORE'S). On
        the LIGHT sheet #7F4282 clears AA (6.99:1 on white). On the DARK panel #111B1E that SAME
        #7F4282 measures only 2.50:1 - the "missing dark arm" defect the owner originally flagged.

        The stat LABEL joined this guard on 2026-08-03 with the stat-button revert: the owner asked
        for the stat button's TEXT (not only its figure) in the secondary purple, and core leaves
        `.o_stat_text` uncoloured at an inherited 3.12:1 - so the same declaration satisfies the
        brand request and repairs a genuine AA failure. It reads the same --o-stat-text-color
        property as the value, so both arms below apply to it unchanged and neither can drift.

        >>> OWNER REVISION 2026-08-03: THE ANSWER IS NO PURPLE IN DARK, NOT A DARKER PURPLE. <<<
        The first fix answered the 2.50:1 with a dark arm (#B589B8). The owner rejected the premise:
        the purple accent is LIGHT-ONLY, and in dark these surfaces take the DEFAULT look. So the
        contrast rule below is unchanged - it is the real behaviour and both arms must clear AA - but
        the dark arm now additionally REFUSES both purples, and pins each surface to the default the
        owner named. The two defaults differ because the two surfaces are reached differently:
          * the stat value is OURS, so brand_cascade.scss states it: `--o-stat-text-color` becomes
            $body-color, "the default bright body text tier" verbatim. It cannot simply be dropped -
            core's own fallback is `var(--o-stat-text-color, $o-brand-primary)`, the DECORATIVE teal,
            i.e. still an accent and the wrong one;
          * the mobile form label is CORE'S rule, out of reach of any guard of ours, so it is
            neutralised at the TOKEN: dark_palette.scss re-points $o-brand-secondary itself to the
            dark muted tier. That single re-point also covers core's search-panel divider and the POS
            backend kanban, which read the same token.

        Each surface is resolved on the surface it actually renders on, parametrised over
        {light: assets_backend / white, dark: assets_web_dark / #111B1E}. Because web.assets_web_dark
        includes web.assets_web (-> web.assets_backend), the SAME surfaces recompile in the dark
        bundle, so the resolver reads the real dark value."""
        with open(BRAND_VARIABLES_SCSS, encoding="utf-8") as scss_file:
            expected_light_secondary = _resolve_scss_hex(scss_file.read(), "$o-brand-secondary")
        self.assertIsNotNone(
            expected_light_secondary,
            "$o-brand-secondary must be declared in %s - it is the SSOT for the stat-value / mobile "
            "form-label colour." % os.path.basename(BRAND_VARIABLES_SCSS),
        )
        expected_light_secondary = expected_light_secondary.lower()

        # The two surfaces, as the real element chains the resolver walks (transcribed from core).
        buttonbox = {
            "classes": frozenset({
                "o-form-buttonbox", "d-print-none", "position-relative", "d-flex", "w-md-auto",
                "o_not_full",
            }),
            "ancestors": BUTTONBOX_ANCESTORS, "prev_sibling": frozenset(),
        }
        stat_value_chain = [
            {"classes": frozenset({"o_stat_value"}), "ancestors": STAT_BUTTON_ANCESTORS,
             "prev_sibling": frozenset({"o_stat_text"})},
            buttonbox,
        ]
        # OWNER REVISION 2026-08-03: the stat LABEL joins the value ("font dung mau tim secondary").
        # It is the FIRST child of .o_stat_info (button_box renders text then value, which is why the
        # value above models .o_stat_text as its previous sibling), so it has no preceding sibling.
        # Core gives `.o_stat_text` no colour at all - it inherits the btn-outline-secondary grey,
        # measured at 3.12:1 on the white sheet, a real WCAG SC 1.4.3 failure in core's own light
        # theme. Adding it here means the AA assertion at the bottom of this loop now GUARDS that
        # fix: the purple is simultaneously the brand answer and the accessible one (6.99:1).
        stat_label_chain = [
            {"classes": frozenset({"o_stat_text"}), "ancestors": STAT_BUTTON_ANCESTORS,
             "prev_sibling": frozenset()},
            buttonbox,
        ]
        mobile_label_chain = [
            {"classes": frozenset({"o_form_label"}), "ancestors": XXS_FORM_LABEL_ANCESTORS,
             "prev_sibling": frozenset()},
        ]
        # Each surface names the DARK default the owner asked for. They differ because the stat value
        # is OURS to state (the bright body-text tier) while the mobile label is CORE'S rule,
        # neutralised at the token (the dark muted tier) - see the docstring.
        tokens = (
            ("desktop stat-button value", stat_value_chain, DARK_READABLE_TEXT),
            ("desktop stat-button label", stat_label_chain, DARK_READABLE_TEXT),
            ("mobile (o_xxs_form_view) form label", mobile_label_chain, DARK_MUTED_TIER),
        )
        arms = (
            ("light", BACKEND_BUNDLE, WHITE),
            ("dark", DARK_BUNDLE, DARK_BODY_BG),
        )
        for arm, bundle_name, surface in arms:
            css = self._compiled_css(bundle_name)
            for label, chain, dark_default in tokens:
                colour = self._resolve_colour(
                    css, chain, ("color",), "%s (%s arm)" % (label, arm)
                )
                if arm == "light":
                    # Anchor: on the light sheet the surface is the brand SECONDARY purple (SSOT) -
                    # proves the resolver is reading the right token, not an unrelated label rule.
                    self.assertEqual(
                        colour, expected_light_secondary,
                        "The %s compiled to %s on the light sheet instead of the brand secondary "
                        "%s ($o-brand-secondary). The element model or the token wiring changed."
                        % (label, colour, expected_light_secondary),
                    )
                else:
                    self.assertNotEqual(
                        colour, expected_light_secondary,
                        "The %s compiled the light brand purple %s in the DARK bundle - 2.50:1 on "
                        "%s. The purple accent is light-only from 2026-08-03."
                        % (label, expected_light_secondary, DARK_BODY_BG),
                    )
                    self.assertNotEqual(
                        colour, RETIRED_DARK_PURPLE,
                        "The %s compiled the RETIRED dark purple %s. The owner rejected a darker "
                        "purple as the answer to the dark panel - the answer is NO purple."
                        % (label, RETIRED_DARK_PURPLE),
                    )
                    self.assertEqual(
                        colour, dark_default,
                        "The %s compiled %s in the dark bundle instead of the default the owner "
                        "named for it, %s. For the stat value that default is stated by our own "
                        "`--o-stat-text-color` dark arm (core's fallback is the decorative teal, "
                        "still an accent); for the mobile label it comes from re-pointing "
                        "$o-brand-secondary itself, because that rule is core's."
                        % (label, colour, dark_default),
                    )
                ratio = _contrast_ratio(colour, surface)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "The %s renders %s on the %s surface %s - %.2f:1, below the WCAG AA normal-text "
                    "threshold of %.1f:1. In the dark bundle this is the signature of the light "
                    "$o-brand-secondary recompiling un-neutralised (2.50:1 on %s)."
                    % (label, colour, arm, surface, ratio, WCAG_AA_NORMAL_TEXT, DARK_BODY_BG),
                )

    # ----------------------------------------------------------------------------------------
    # 12. DARK ARM (C-6) - the interactive link token clears AA on BOTH the light and dark panel
    # ----------------------------------------------------------------------------------------
    def test_interactive_link_token_clears_wcag_aa_on_light_and_dark_surfaces(self):
        """The --link-color content-link token must clear WCAG AA against the panel in both schemes.

        Content links resolve their colour from the :root --link-color custom property (Odoo emits
        it from $o-main-link-color / $link-color). On white the AA teal #007F8E clears AA (4.74:1).
        On the dark panel #111B1E that SAME #007F8E measures only 3.69:1 - below AA - so the dark
        arm must retint the link to a lighter teal (owner value #4FD4E2).

        RED BEFORE GREEN: web.assets_web_dark carries the light #007F8E link today (3.69:1 on
        #111B1E), so the dark arm FAILS until the link dark override lands. The light arm passes now
        and must stay green."""
        for arm, bundle_name, surface in (
            ("light", BACKEND_BUNDLE, WHITE),
            ("dark", DARK_BUNDLE, DARK_BODY_BG),
        ):
            css = self._compiled_css(bundle_name)
            raw_values = self._root_custom_prop_values(css, "link-color")
            link_hexes = [c for c in (_normalize_colour(value) for value in raw_values) if c]
            self.assertTrue(
                link_hexes,
                "No concrete --link-color hex was declared on :root in the %s bundle (%s). The "
                "content-link token must resolve to a colour so its readability can be checked."
                % (arm, bundle_name),
            )
            # Equal-specificity :root declarations: the last in source order wins the cascade.
            link_colour = link_hexes[-1]
            ratio = _contrast_ratio(link_colour, surface)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "The content-link colour --link-color=%s renders on the %s panel %s at %.2f:1, "
                "below the WCAG AA normal-text threshold of %.1f:1. In dark mode the link needs its "
                "dark arm (owner value %s) instead of the light AA teal."
                % (link_colour, arm, surface, ratio, WCAG_AA_NORMAL_TEXT, DARK_LINK_REF),
            )

    # ----------------------------------------------------------------------------------------
    # 13. DEF-005 (C-3/C-6) - navbar menu-entry text is OPAQUE so it clears AA on the teal navbar
    # ----------------------------------------------------------------------------------------
    def test_navbar_menu_entry_text_is_opaque_for_aa_on_the_teal_navbar(self):
        """A resting navbar menu-entry must render OPAQUE white text, not a .9-alpha composite.

        The navbar chrome is scheme-INVARIANT teal, so this is not a dark-only defect. Core paints
        the resting entry text `color: var(--NavBar-entry-color, #{$o-navbar-entry-color})` and
        $o-navbar-entry-color is `rgba($o-white, .9)` (navbar.variables.scss:13). At .9 opacity the
        white composites to ~#E6F2F4 over the #007F8E bar - only ~4.15:1, below AA. DEF-005: set the
        entry-text token so it renders as OPAQUE #FFFFFF (4.74:1 on the teal bar).

        The opacity is the whole defect, so it is asserted on the resolved value's ALPHA, not on its
        hue: _normalize_colour deliberately drops alpha, so a contrast check alone would read the
        composite as an AA-passing #FFFFFF and never fail. The teal bar is white-safe only when the
        entry text is fully opaque.

        RED BEFORE GREEN: today the token resolves to `rgba(255,255,255,.9)` (alpha .9), so the
        opacity assertion FAILS; it passes once the entry-text token is made opaque #FFFFFF."""
        css = self._css()
        navbar_root = {
            "classes": frozenset({"o_main_navbar"}), "ancestors": frozenset({"o_web_client"}),
            "prev_sibling": frozenset(),
        }
        entry = {
            "classes": NAVBAR_ENTRY_CLASSES, "ancestors": NAVBAR_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        raw_value = _computed_value(css, [entry, navbar_root], ("color",))
        self.assertIsNotNone(
            raw_value,
            "No compiled `color` declaration applies to a resting navbar menu entry. The entry-text "
            "surface is unstyled, so DEF-005 cannot be verified - re-ground the element model.",
        )
        alpha = _alpha_of(raw_value)
        self.assertEqual(
            alpha, 1.0,
            "The resting navbar menu-entry text compiled to %r (alpha %.2f). DEF-005: at .9 opacity "
            "the white composites to ~#E6F2F4 over the teal bar (~4.15:1, below AA). The entry-text "
            "token must render OPAQUE #FFFFFF so the white text clears AA (4.74:1) on the %s bar."
            % (raw_value, alpha, CHROME_BASE),
        )
        colour = _normalize_colour(raw_value)
        self.assertIsNotNone(
            colour,
            "The navbar menu-entry text %r carries no resolvable colour." % raw_value,
        )
        # Corroborating (not load-bearing): once opaque, the white entry text clears AA on the bar.
        self.assertGreaterEqual(
            _contrast_ratio(colour, CHROME_BASE), WCAG_AA_NORMAL_TEXT,
            "The opaque navbar entry text %s does not clear WCAG AA against the chrome-base bar %s."
            % (colour, CHROME_BASE),
        )

    # ----------------------------------------------------------------------------------------
    # 14. FIX GROUP 1 - secondary SOLID surfaces flip dark (kanban / settings / facet / table-info)
    # ----------------------------------------------------------------------------------------
    def test_secondary_surfaces_flip_dark_in_the_dark_bundle(self):
        """Kanban canvas, settings sidebar+header, facet band and the selected row must be DARK.

        These four secondary surfaces are painted from a compile-time grayscale literal
        ($o-gray-100 #F8F9FA / $o-gray-200 #E9ECEF) or a Bootstrap table-variant - levers the
        surface-neutral $body-*-bg dark overrides never reach, so before this fix they recompiled
        LIGHT in web.assets_web_dark (a dark card floating on a light kanban canvas; a light settings
        sidebar; a ~1.07:1 invisible facet value; a 1.87:1 selected-row checkbox). The fix darkens
        each via a dedicated lever (kanban -> $o-kanban-background in dark_palette.scss; the rest ->
        dark_secondary_surfaces.dark.scss). Each is asserted on the surface it renders on in the DARK
        bundle AND is proven NOT to still be its light value, so the guard is non-vacuous.

        Contrast is asserted where the review flagged it: the facet VALUE text (WCAG AA >=4.5) and the
        selected-row CHECKBOX fill (WCAG non-text >=3.0) must clear on the newly-darkened band.

        RED BEFORE GREEN: on the un-fixed dark bundle every surface below resolves to its light
        grayscale/table-variant value, so both the equality and the "not the light value" assertion
        fail; they pass only once the dark overrides land. The LIGHT arm is asserted too (the same
        surfaces stay light in web.assets_backend - non-regression)."""
        flat_brand_teal = self._assert_flat_teal_available()   # the selected-row checkbox fill #00BBCE
        light_gray_100 = "#f8f9fa"
        light_gray_200 = "#e9ecef"

        dark_css = self._compiled_css(DARK_BUNDLE)
        light_css = self._css()

        # --- Kanban canvas: .o_kanban_renderer --Kanban-background --------------------------------
        kanban_renderer = {
            "classes": frozenset({"o_kanban_renderer"}),
            "ancestors": KANBAN_RENDERER_ANCESTORS, "prev_sibling": frozenset(),
        }
        dark_kanban = self._resolve_colour(
            dark_css, [kanban_renderer], ("--Kanban-background",), "dark kanban canvas"
        )
        self.assertEqual(
            dark_kanban, DARK_KANBAN_CANVAS,
            "The kanban canvas --Kanban-background compiled to %s in the dark bundle instead of the "
            "app-grey %s. $o-kanban-background was not darkened in dark_palette.scss, so the dark "
            "card floats on a light canvas." % (dark_kanban, DARK_KANBAN_CANVAS),
        )
        light_kanban = self._resolve_colour(
            light_css, [kanban_renderer], ("--Kanban-background",), "light kanban canvas"
        )
        self.assertEqual(
            light_kanban, light_gray_100,
            "The kanban canvas must stay the light grayscale %s in web.assets_backend "
            "(non-regression); it compiled to %s." % (light_gray_100, light_kanban),
        )

        # --- Settings sidebar + section-header ---------------------------------------------------
        settings_renderer = {
            "classes": frozenset({"o_form_renderer"}),
            "ancestors": SETTINGS_RENDERER_ANCESTORS, "prev_sibling": frozenset(),
        }
        for token, dark_expected, light_expected, label in (
            ("--settings__tab-bg", DARK_SETTINGS_SIDEBAR, light_gray_100, "settings sidebar"),
            ("--settings__title-bg", DARK_SETTINGS_HEADER, light_gray_200, "settings section header"),
        ):
            dark_val = self._resolve_colour(
                dark_css, [settings_renderer], (token,), "dark %s" % label
            )
            self.assertEqual(
                dark_val, dark_expected,
                "The %s %s compiled to %s in the dark bundle instead of %s - the dark override in "
                "dark_secondary_surfaces.dark.scss did not win core's grayscale literal."
                % (label, token, dark_val, dark_expected),
            )
            light_val = self._resolve_colour(
                light_css, [settings_renderer], (token,), "light %s" % label
            )
            self.assertEqual(
                light_val, light_expected,
                "The %s %s must stay %s in light mode (non-regression); it compiled to %s."
                % (label, token, light_expected, light_val),
            )

        # --- Search facet resting band -----------------------------------------------------------
        facet_band = {
            "classes": frozenset({"o_searchview_facet", "bg-200"}),
            "ancestors": FACET_PILL_ANCESTORS, "prev_sibling": frozenset(),
        }
        dark_facet = self._resolve_colour(
            dark_css, [facet_band], BACKGROUND_PROPS, "dark search-facet band"
        )
        self.assertEqual(
            dark_facet, DARK_FACET_BAND,
            "The search-facet resting band compiled to %s in the dark bundle instead of the raised "
            "tier %s - the value text then sits on a light band at ~1.07:1."
            % (dark_facet, DARK_FACET_BAND),
        )
        self.assertNotEqual(
            dark_facet, light_gray_200,
            "The search-facet band is still the light grayscale %s in dark - the .bg-200 override "
            "was dropped." % light_gray_200,
        )
        self.assertGreaterEqual(
            _contrast_ratio(DARK_READABLE_TEXT, dark_facet), WCAG_AA_NORMAL_TEXT,
            "The facet value text %s on the darkened band %s is %.2f:1, below WCAG AA %.1f:1."
            % (DARK_READABLE_TEXT, dark_facet, _contrast_ratio(DARK_READABLE_TEXT, dark_facet),
               WCAG_AA_NORMAL_TEXT),
        )

        # --- Selected list row (.table-info) + its checkbox --------------------------------------
        table_info_row = {
            "classes": frozenset({"table-info", "o_data_row"}),
            "ancestors": TABLE_INFO_ROW_ANCESTORS, "prev_sibling": frozenset(),
        }
        dark_row = self._resolve_colour(
            dark_css, [table_info_row], ("--bs-table-bg",), "dark selected .table-info row"
        )
        self.assertEqual(
            dark_row, DARK_TABLE_INFO_BAND,
            "The selected .table-info row --bs-table-bg compiled to %s in the dark bundle instead of "
            "the dark info tint %s - the row stayed a light info tint."
            % (dark_row, DARK_TABLE_INFO_BAND),
        )
        self.assertGreaterEqual(
            _contrast_ratio(flat_brand_teal, dark_row), WCAG_NON_TEXT_MIN,
            "The selected-row checkbox fill %s on the darkened band %s is %.2f:1, below the WCAG "
            "non-text threshold %.1f:1."
            % (flat_brand_teal, dark_row, _contrast_ratio(flat_brand_teal, dark_row),
               WCAG_NON_TEXT_MIN),
        )
        self.assertGreaterEqual(
            _contrast_ratio(DARK_READABLE_TEXT, dark_row), WCAG_AA_NORMAL_TEXT,
            "The selected-row text %s on the darkened band %s is %.2f:1, below WCAG AA %.1f:1."
            % (DARK_READABLE_TEXT, dark_row, _contrast_ratio(DARK_READABLE_TEXT, dark_row),
               WCAG_AA_NORMAL_TEXT),
        )

    # ----------------------------------------------------------------------------------------
    # 15. FIX GROUP 1 (PR #658 review-fix) - the selected .table-info row CELL renders dark
    # ----------------------------------------------------------------------------------------
    def test_selected_table_info_row_cells_paint_dark_band_not_light_accent(self):
        """A selected row's CELLS must paint the dark selection band - not a light Bootstrap accent.

        This is the RENDER-LEVEL companion to the --bs-table-bg row-token check in
        test_secondary_surfaces_flip_dark_in_the_dark_bundle. That token check went GREEN while the
        row still RENDERED light - the exact defect a live UI review pinned. The reason is that
        re-pointing only the row's --bs-table-bg makes the ROW variable compute #123037, but
        Bootstrap 5.3 paints a table CELL through `.table > :not(caption) > * > *`
        (web/static/lib/bootstrap/scss/_tables.scss:33-40) as THREE inherited-token layers:
        `background-color: var(--bs-table-bg)`, an opaque inset OVERLAY
        `box-shadow: inset 0 0 0 9999px var(--bs-table-bg-state, var(--bs-table-bg-type,
        var(--bs-table-accent-bg)))`, and `color: var(--bs-table-color-state, ...)`. Core's
        `.table-info` variant fills those with a LIGHT info tint, so the visible cell stayed a light
        band (#CCEBFA) under a light accent overlay (#C1DEEC) with near-black text - the row token was
        green but the pixel was light. The fix overrides the CELL itself in
        dark_secondary_surfaces.dark.scss (background-color + the inset box-shadow + text colour), so
        this guard resolves the CELL's real paint layers, NOT the row variable that let the defect
        slip.

        Both the .o_data_cell and the .o_list_record_selector cell are asserted (the review measured
        both), and each is proven != its light value so the guard is non-vacuous.

        RED BEFORE GREEN: with only the row-token override, the resolver finds no cell-level paint
        declaration (core's cell rule has a universal `*` subject the conservative resolver
        deliberately does not model), so _resolve_colour raises 'no declaration applies'; it passes
        only once the cell override lands. WCAG is asserted where the review flagged it: the light
        row text (>=4.5 AA) and the teal selection checkbox (>=3.0 non-text) on the darkened band."""
        flat_brand_teal = self._assert_flat_teal_available()   # selected-row checkbox fill #00BBCE

        dark_css = self._compiled_css(DARK_BUNDLE)
        light_css = self._css()

        # A cell is a direct child of the selected row, so the row's classes (o_data_row, table-info)
        # are ANCESTORS of the cell - added to the shared row ancestor pool.
        cell_ancestors = TABLE_INFO_ROW_ANCESTORS | {"o_data_row", "table-info"}
        for label, cell_class in (
            ("data cell", "o_data_cell"),
            ("record-selector cell", "o_list_record_selector"),
        ):
            cell = {
                "classes": frozenset({cell_class}),
                "ancestors": cell_ancestors, "prev_sibling": frozenset(),
            }

            band = self._resolve_colour(
                dark_css, [cell], BACKGROUND_PROPS, "dark selected-row %s background" % label
            )
            self.assertEqual(
                band, DARK_TABLE_INFO_BAND,
                "The selected-row %s background-color compiled to %s in the dark bundle instead of "
                "the dark info band %s - the cell override in dark_secondary_surfaces.dark.scss did "
                "not win Bootstrap's `.table-info` cell paint." % (label, band, DARK_TABLE_INFO_BAND),
            )
            self.assertNotEqual(
                band, LIGHT_TABLE_INFO_BAND,
                "The selected-row %s still paints the LIGHT info band %s in dark mode - overriding "
                "only the row --bs-table-bg is not enough; the CELL background-color must darken."
                % (label, LIGHT_TABLE_INFO_BAND),
            )

            # The inset box-shadow overlay is the layer painted ON TOP of the background, so it is
            # what a light accent actually shows through. Resolve it as a colour and require the dark
            # band - this is the neutralization the --bs-table-bg row-var check could never see.
            overlay = self._resolve_colour(
                dark_css, [cell], ("box-shadow",), "dark selected-row %s inset accent overlay" % label
            )
            self.assertEqual(
                overlay, DARK_TABLE_INFO_BAND,
                "The selected-row %s inset box-shadow overlay compiled to %s instead of the dark band "
                "%s - Bootstrap's `inset 0 0 0 9999px var(--bs-table-accent-bg)` light accent was not "
                "neutralized, so a light overlay repaints the darkened cell."
                % (label, overlay, DARK_TABLE_INFO_BAND),
            )
            self.assertNotEqual(
                overlay, LIGHT_TABLE_INFO_ACCENT,
                "The selected-row %s still carries the LIGHT inset accent overlay %s in dark mode - "
                "the box-shadow (or --bs-table-accent-bg / --bs-table-bg-state) was not neutralized."
                % (label, LIGHT_TABLE_INFO_ACCENT),
            )

            text = self._resolve_colour(
                dark_css, [cell], ("color",), "dark selected-row %s text" % label
            )
            self.assertGreaterEqual(
                _contrast_ratio(text, band), WCAG_AA_NORMAL_TEXT,
                "The selected-row %s text %s on the dark band %s is %.2f:1, below WCAG AA %.1f:1 - "
                "the cell kept core's near-black color-contrast text on the darkened band."
                % (label, text, band, _contrast_ratio(text, band), WCAG_AA_NORMAL_TEXT),
            )
            self.assertGreaterEqual(
                _contrast_ratio(flat_brand_teal, band), WCAG_NON_TEXT_MIN,
                "The selection checkbox fill %s on the %s dark band %s is %.2f:1, below the WCAG "
                "non-text threshold %.1f:1." % (flat_brand_teal, label, band,
                                                _contrast_ratio(flat_brand_teal, band), WCAG_NON_TEXT_MIN),
            )

            # Non-leak: this dark-only cell override must never paint the LIGHT web.assets_backend
            # bundle. The resolver cannot see core's universal-subject cell rule, so the light bundle
            # resolves to None here; the guard fires only if the dark band ever leaks into light.
            light_value = _computed_value(light_css, [cell], BACKGROUND_PROPS)
            light_band = _normalize_colour(light_value) if light_value else None
            self.assertNotEqual(
                light_band, DARK_TABLE_INFO_BAND,
                "The dark selected-row %s band %s leaked into the LIGHT web.assets_backend bundle - "
                "dark_secondary_surfaces.dark.scss must stay dark-bundle only."
                % (label, DARK_TABLE_INFO_BAND),
            )

    # ----------------------------------------------------------------------------------------
    # 16. batch-3 item 6a - dark faded form label lifted above core's dim default (legibility)
    # ----------------------------------------------------------------------------------------
    def test_dark_faded_form_label_is_lifted_above_core_dim_default(self):
        """A faded (empty/readonly) form label must be lifted above core's 0.66 default in dark.

        GROUNDING (corrected). The faded-label BASE colour is #EDF4F5 only BECAUSE the module gives the
        general `.o_form_label` its own `color: var(--body-color)` in dark_secondary_surfaces.dark.scss
        (FIX 1) - NOT because it "inherits the dark body text", as an earlier note wrongly claimed. A
        bare label inherits #212529 from its `.text-900` cell; the direct override is what makes #EDF4F5
        the accurate base the composite below is measured on. Core then fades the empty/readonly/false
        variant with `.o_form_view .o_form_label.o_form_label_readonly { opacity: 0.66 }`
        (form_controller.scss:606). #EDF4F5 at 0.66 over the #111B1E sheet composites to #A2AAAC =
        7.41:1 - which already CLEARS WCAG AA (4.5) AND AAA (7.0). So on the CORRECTED base the faded
        label is not an AA defect; it is PERCEPTUALLY dim (a filled label reads 15.72:1, a full step
        brighter). Owner 2026-08-02 asked to lift the fade; at 0.85 the composite is #CCD3D5 = 11.54:1,
        closer to the filled tier. (Before FIX 1 the faded base was #212529-on-dark regardless of
        opacity, so this polish alone never fixed the real contrast defect - the colour fix does.)

        What this guard protects (behaviour, red-before-green):
        (a) LOAD-BEARING - the dark bundle lifts the faded-label opacity STRICTLY above core's dim
            0.66 default (grounded literal CORE_FADED_LABEL_OPACITY, never the fix's own 0.85), so the
            module's dark override is present and effective. RED on the un-fixed bundle (effective
            opacity IS 0.66); GREEN once the lift lands.
        (b) FLOOR (corroborating, green both ways) - the composited faded label still clears WCAG AA
            on the dark sheet, so the polish never pushes legibility the wrong way.
        (c) NON-REGRESSION - light mode keeps core's 0.66 (the polish is dark-bundle only)."""
        faded_label = {
            "classes": frozenset({"o_form_label", "o_form_label_readonly"}),
            "ancestors": FORM_LABEL_ANCESTORS, "prev_sibling": frozenset(),
        }
        dark_css = self._compiled_css(DARK_BUNDLE)
        raw_opacity = _winning_declaration(dark_css, faded_label, ("opacity",))
        self.assertIsNotNone(
            raw_opacity,
            "No compiled `opacity` declaration applies to a faded (readonly) form label in the dark "
            "bundle - core's form_controller.scss:606 rule or the element model changed; re-ground.",
        )
        opacity = float(raw_opacity.strip())
        # (a) load-bearing: lifted above core's dim default.
        self.assertGreater(
            opacity, CORE_FADED_LABEL_OPACITY,
            "The faded form-label opacity in web.assets_web_dark is %.2f - core's dim %.2f default, "
            "not lifted. dark_secondary_surfaces.dark.scss must raise it so empty/readonly labels do "
            "not read a full step dimmer than filled labels on the dark sheet."
            % (opacity, CORE_FADED_LABEL_OPACITY),
        )
        # (b) floor: the composited faded label still clears AA on the dark sheet.
        composite = _composite_over(DARK_READABLE_TEXT, DARK_BODY_BG, opacity)
        ratio = _contrast_ratio(composite, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The faded form label composites to %s at opacity %.2f over the dark sheet %s - %.2f:1, "
            "below WCAG AA %.1f:1."
            % (composite, opacity, DARK_BODY_BG, ratio, WCAG_AA_NORMAL_TEXT),
        )
        # (c) non-regression: light mode keeps core's 0.66 (the lift is dark-only).
        light_css = self._css()
        light_opacity = _winning_declaration(light_css, faded_label, ("opacity",))
        self.assertIsNotNone(
            light_opacity,
            "No `opacity` declaration applies to a faded form label in web.assets_backend - core's "
            "0.66 default is missing; re-ground.",
        )
        self.assertEqual(
            float(light_opacity.strip()), CORE_FADED_LABEL_OPACITY,
            "The faded form-label opacity in the LIGHT bundle is %s, not core's %.2f - the dark-only "
            "legibility lift leaked into web.assets_backend."
            % (light_opacity, CORE_FADED_LABEL_OPACITY),
        )

    # ----------------------------------------------------------------------------------------
    # 16b. batch-3 item 6a (base tier) - GENERAL dark form label resolves readable, not light #212529
    # ----------------------------------------------------------------------------------------
    def _resolve_colour_value(self, css, chain, raw):
        """Resolve a raw ``color`` / custom-property value to a normalised #rrggbb, or None.

        Follows ``var()`` FIRST through the ancestor ``chain`` (CSS custom properties inherit, so
        ``--color`` set on the ``.text-900`` cell is found there) and FINALLY through ``:root`` -
        which the class-only cascade model (:func:`_matches_element`) deliberately does not represent,
        so ``--body-color`` set on ``:root`` is resolved via :meth:`_root_custom_prop_values`. Bounded
        so a malformed self-referential var can never spin. Returns None when it resolves to no
        colour."""
        value = raw
        for _ in range(8):
            if value is None:
                return None
            var_match = _VAR_RE.match(value.strip())
            if not var_match:
                return _normalize_colour(value)
            name, fallback = var_match.group(1), var_match.group(2)
            resolved = None
            for ancestor in chain:
                candidate = _winning_declaration(css, ancestor, (name,))
                if candidate is not None:
                    resolved = candidate
                    break
            if resolved is None:
                root_values = self._root_custom_prop_values(css, name[2:])
                if root_values:
                    resolved = root_values[-1]
            value = resolved if resolved is not None else fallback
        return _normalize_colour(value) if value else None

    def _effective_label_colour(self, css, chain, surface):
        """Resolve the ``color`` an element COMPUTES, honouring real CSS inheritance through ``chain``.

        ``color`` is an INHERITED property: an element with no winning ``color`` of its own takes the
        computed ``color`` of its nearest ancestor that has one. Crucially, a DIRECT declaration on
        the element - even a normal (non-!important) one - beats any inherited value, because
        ``!important`` on an ancestor governs only THAT ancestor's own cascade, never what a descendant
        inherits. So walk ``chain`` innermost-first and return the first element that carries a winning
        ``color``, resolving ``var()`` through the chain then ``:root``; if nothing in the chain
        declares ``color``, inherit the ``:root --body-color`` the bundle emits.

        WHY A CHAIN (this is the fix for the earlier VACUOUS resolver). The previous version took a
        SINGLE element and read only the label's OWN rules; finding none, it jumped straight to
        ``:root --body-color`` and reported the dark body text #EDF4F5 - staying green even though the
        live label inherits #212529 from its ``.o_cell.o_wrap_label.text-900`` parent cell. Passing the
        cell in ``chain`` is what makes that dark-on-dark reversion observable: with no fix the label
        has no own ``color`` and the resolver reaches the ``.text-900`` cell's compile-time #212529."""
        for index, element in enumerate(chain):
            raw = _winning_declaration(css, element, ("color",))
            if raw is None:
                continue
            colour = self._resolve_colour_value(css, chain[index:], raw)
            self.assertIsNotNone(
                colour,
                "A `color` rule wins on %s but %r resolves to no colour - the token was dropped or "
                "core moved the surface to a different lever; re-ground." % (surface, raw),
            )
            return colour
        body_colours = self._root_custom_prop_values(css, "body-color")
        self.assertTrue(
            body_colours,
            "Nothing in the cascade chain declares `color` for %s and no :root --body-color exists - "
            "the inherited body-text chain the element relies on is gone; re-ground." % surface,
        )
        return _normalize_colour(body_colours[-1])

    def _general_form_label_chain(self):
        """The desktop general form label modelled WITH its real ``.text-900`` cell parent.

        chain[0] is the bare `<label class="o_form_label">`; chain[1] is its
        `.o_cell.o_wrap_label.text-break.text-900` parent cell (form_group.xml:46). The label's
        ancestor pool includes the cell classes because the cell IS an ancestor - a generous pool can
        only ADD a competitor and fail loudly, never hide one."""
        return [
            {
                "classes": frozenset({"o_form_label"}),
                "ancestors": FORM_LABEL_ANCESTORS | FORM_LABEL_CELL_CLASSES,
                "prev_sibling": frozenset(),
            },
            {
                "classes": FORM_LABEL_CELL_CLASSES,
                "ancestors": FORM_LABEL_ANCESTORS,
                "prev_sibling": frozenset(),
            },
        ]

    def test_dark_general_form_label_resolves_readable_body_color_not_light_default(self):
        """The GENERAL (non-faded) form label must resolve a WCAG-AA colour in dark, never light #212529.

        Base-tier companion to test_dark_faded_form_label_* (which guards the empty/readonly OPACITY).
        That test composites a HARDCODED #EDF4F5, so it structurally cannot notice the base colour
        reverting; this guard resolves the ACTUAL colour a plain `.o_form_label` COMPUTES through the
        real cascade in web.assets_web_dark and asserts the readability contract.

        WHY THE EARLIER VERSION OF THIS GUARD WAS VACUOUS (and how this one is not). It resolved the
        label as a SINGLE element - reading only rules ON `.o_form_label`, finding none, and inheriting
        `:root --body-color` = #EDF4F5 - so it stayed green even though the LIVE label renders #212529.
        The label is a bare `<label class="o_form_label">` (form_label.xml:5) whose parent CELL carries
        `text-900` (form_group.xml:46). `.text-900` compiles to `color: var(--color) !important` with
        `--color` = the compile-time literal #212529 ($o-gray-900), which the dark palette does NOT flip
        (it re-points $body-color, not the $o-gray-* scale). `color` inherits, so with no colour of its
        own the label inherits #212529 from the cell = 1.14:1 on the dark sheet #111B1E - a PROVEN
        dark-on-dark failure (live confirm-by-toggle, 2026-08-02). This guard now models that cell in
        the chain, so the reversion is observable.

        The fix gives the label its own `.o_form_view .o_form_label { color: var(--body-color) }`
        (#EDF4F5, 15.72:1) - a direct declaration that beats the inherited #212529 WITHOUT !important,
        because the cell's !important governs only the cell's own cascade, not what the child inherits.
        The effective colour is resolved cascade-faithfully (direct label colour if one wins, else the
        nearest ancestor that declares colour - here the .text-900 cell - else :root --body-color), so a
        future hierarchy refinement that gives labels their own muted tier still passes as long as it
        clears AA and is not the light #212529: the guard protects the CONTRACT, not a literal.

        RED BEFORE GREEN: with the fix removed the label has no own colour and the resolver reaches the
        .text-900 cell's #212529 - 1.14:1 - so BOTH the AA and the not-#212529 assertions fire. The
        LIGHT arm asserts the label stays #212529 in web.assets_backend, where the fix file is absent
        and #212529-on-white is correct (dark-only override; light mode untouched)."""
        chain = self._general_form_label_chain()
        dark_css = self._compiled_css(DARK_BUNDLE)
        light_css = self._css()

        dark_eff = self._effective_label_colour(dark_css, chain, "dark general form label")
        dark_ratio = _contrast_ratio(dark_eff, DARK_BODY_BG)
        self.assertGreaterEqual(
            dark_ratio, WCAG_AA_NORMAL_TEXT,
            "The general form label resolves %s in web.assets_web_dark - %.2f:1 on the dark sheet %s, "
            "below WCAG AA %.1f:1. Its own `.o_form_label { color: var(--body-color) }` override is "
            "missing, so it inherits the .text-900 cell's near-black #212529 on the dark sheet."
            % (dark_eff, dark_ratio, DARK_BODY_BG, WCAG_AA_NORMAL_TEXT),
        )
        self.assertNotEqual(
            dark_eff, LIGHT_BODY_TEXT,
            "The general form label resolves the LIGHT near-black %s in the dark bundle (1.14:1 on %s) - "
            "the dark-on-dark reversion inherited from its .text-900 parent cell. "
            "dark_secondary_surfaces.dark.scss must give .o_form_label its own dark body colour."
            % (LIGHT_BODY_TEXT, DARK_BODY_BG),
        )

        light_eff = self._effective_label_colour(light_css, chain, "light general form label")
        self.assertEqual(
            light_eff, LIGHT_BODY_TEXT,
            "The general form label must keep core's near-black %s in web.assets_backend (the label "
            "inherits its .text-900 cell there, and #212529-on-white is correct - the dark readability "
            "fix is dark-bundle only); it resolved %s." % (LIGHT_BODY_TEXT, light_eff),
        )

    def test_dark_text_900_emphasis_surfaces_resolve_readable_not_light_default(self):
        """Every `.text-900` near-black emphasis surface must read light-on-dark in the dark bundle.

        Companion to the general-form-label guard, proving FIX 2 (the class-wide `--color` re-point)
        reaches beyond form labels. `.text-900` (bootstrap_review_backend.scss via text-emphasis-variant
        -> o-print-color) bakes `--color: RGBA(33,37,41,...); color: var(--color) !important` =
        $o-gray-900 #212529, a compile-time literal the dark palette does NOT flip. It is applied not
        only to form-label cells but to navbar apps-menu section titles (navbar.xml:51/:67), property
        labels/definitions, kanban column titles (kanban_header.xml:13) and animated numbers - all
        dark-on-dark on the dark app surface. dark_secondary_surfaces.dark.scss re-points `--color` to
        the dark body tier on `.text-900` for the whole backend dark bundle, so core's own
        `color: var(--color) !important` then paints the readable tier.

        This guards the kanban column title as a representative NON-form-label surface: it carries
        `.text-900` DIRECTLY, so its resolved `color` must clear WCAG AA on the dark kanban header and
        must not be the light #212529.

        RED BEFORE GREEN: drop the `.text-900 { --color: #{$body-color} }` re-point and core's --color
        RGBA(33,37,41) wins, so the title resolves #212529 = dark-on-dark and both assertions fire. The
        LIGHT arm asserts the utility stays #212529 in web.assets_backend (dark-only fix)."""
        kanban_title = {
            "classes": KANBAN_TITLE_CLASSES, "ancestors": KANBAN_HEADER_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        dark_css = self._compiled_css(DARK_BUNDLE)
        light_css = self._css()

        dark_eff = self._effective_label_colour(
            dark_css, [kanban_title], "dark kanban column title"
        )
        dark_ratio = _contrast_ratio(dark_eff, DARK_KANBAN_CANVAS)
        self.assertGreaterEqual(
            dark_ratio, WCAG_AA_NORMAL_TEXT,
            "The .text-900 kanban column title resolves %s in web.assets_web_dark - %.2f:1 on the dark "
            "kanban header %s, below WCAG AA %.1f:1. The `.text-900 { --color }` dark re-point is "
            "missing, so the near-black $o-gray-900 literal paints dark-on-dark."
            % (dark_eff, dark_ratio, DARK_KANBAN_CANVAS, WCAG_AA_NORMAL_TEXT),
        )
        self.assertNotEqual(
            dark_eff, LIGHT_BODY_TEXT,
            "The .text-900 kanban column title resolves the light near-black %s in the dark bundle - "
            "the .text-900 emphasis utility was not re-pointed for the backend dark context, so every "
            "navbar/property/kanban/animated-number .text-900 surface stays dark-on-dark."
            % LIGHT_BODY_TEXT,
        )

        light_eff = self._effective_label_colour(
            light_css, [kanban_title], "light kanban column title"
        )
        self.assertEqual(
            light_eff, LIGHT_BODY_TEXT,
            "The .text-900 kanban column title must keep core's near-black %s in web.assets_backend "
            "(the emphasis re-point is dark-bundle only); it resolved %s."
            % (LIGHT_BODY_TEXT, light_eff),
        )

    # ----------------------------------------------------------------------------------------
    # 17. batch-3 item 6b - debug database name readable (opaque white) on the teal navbar
    # ----------------------------------------------------------------------------------------
    def test_debug_database_name_is_readable_on_the_teal_navbar(self):
        """The debug-mode database name must render readable on the teal navbar, not a dim <mark>.

        With env.debug on, core shows the DB name in the user-menu toggle as a bare `<mark>` inside
        `.o_user_menu .oe_topbar_name` (user_menu.xml:12). Bootstrap's <mark> paints a pale highlight
        fill (--bs-highlight-bg) and the text only inherits, so the db name reads dim on the teal
        navbar ($o-navbar-background #007F8E) - the owner's "database name sinks" report (it is NOT
        .o_debug_manager, which is only the bug icon). The navbar is scheme-INVARIANT teal, so the
        restore lives in web.assets_backend and is verified there.

        Behaviour protected: the db-name <mark> drops the highlight fill (so the text sits on the teal
        bar) and paints an AA-clearing colour on that bar (opaque #FFFFFF is 4.74:1 on #007F8E).

        RED BEFORE GREEN: with no `.oe_topbar_name mark` rule the reader returns None for both the
        colour and the background, so the colour assertion fires; it passes once brand_cascade.scss's
        mark rule lands."""
        css = self._css()
        raw_colour = _winning_topbar_mark_declaration(css, ("color",))
        self.assertIsNotNone(
            raw_colour,
            "No `.oe_topbar_name mark` colour rule compiled into web.assets_backend - the debug "
            "db-name <mark> is unstyled, so it inherits a dim colour on the teal navbar. "
            "brand_cascade.scss must paint it (item 6b).",
        )
        # The <mark> highlight fill must be dropped so the text truly sits on the teal navbar.
        raw_background = _winning_topbar_mark_declaration(css, BACKGROUND_PROPS)
        self.assertIsNotNone(
            raw_background,
            "The `.oe_topbar_name mark` rule sets a colour but no background - Bootstrap's pale "
            "--bs-highlight-bg fill survives, so the db name does not sit on the teal bar.",
        )
        self.assertEqual(
            raw_background.strip().lower(), "transparent",
            "The debug db-name <mark> background compiled to %r, not `transparent` - Bootstrap's "
            "highlight fill is not dropped, so the text is not on the teal navbar." % raw_background,
        )
        mark_colour = _normalize_colour(raw_colour)
        self.assertIsNotNone(
            mark_colour,
            "The `.oe_topbar_name mark` colour %r carries no resolvable colour." % raw_colour,
        )
        ratio = _contrast_ratio(mark_colour, CHROME_BASE)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The debug db-name colour %s renders %.2f:1 on the teal navbar %s, below WCAG AA %.1f:1 - "
            "it must be an opaque high-contrast colour (e.g. #FFFFFF, 4.74:1)."
            % (mark_colour, ratio, CHROME_BASE, WCAG_AA_NORMAL_TEXT),
        )

    # ----------------------------------------------------------------------------------------
    # 18. batch-3 - the MOBILE burger / app-menu sidebar is a DARK surface in dark mode
    # ----------------------------------------------------------------------------------------
    def test_dark_mobile_burger_sidebar_is_a_dark_surface_so_its_text_clears_aa(self):
        """The mobile burger / app-menu sidebar must be a DARK panel in dark mode, not a white island.

        THE DEFECT THIS GUARDS (live-measured, dark mode, 375px). Core hardcodes every colour of this
        component as an `!default` LIGHT literal in burger_menu.variables.scss and consumes them
        directly in burger_menu.scss - panel `$o-burger-base-bg: $o-white` (:3 -> :34), topbar
        `$o-burger-topbar-bg: $o-gray-100` (:6 -> :21), entry text `$o-burger-base-color: $o-gray-800`
        at .8 alpha (:4 -> :60), topbar text `$o-burger-topbar-color: $o-black` (:7 -> :22). Not one is
        reachable from the $body-*-bg surface neutrals, so the panel recompiled WHITE in
        web.assets_web_dark while everything drawn ON it recompiled for a dark backdrop. The
        `web.SectionMenu` section titles (navbar.xml:51/:67, `fw-bolder text-900 pt-3 pb-2`) computed
        the dark #EDF4F5 on that white panel = 1.11:1, invisible.

        WHY THE PANEL, NOT THE TITLE, IS THE ASSERTION SUBJECT. Contrast alone is satisfiable two
        ways: darken the panel, or revert the title to core's near-black. The second re-creates the
        half-dark bug this cluster exists to close (a WHITE panel in dark mode) and leaves the panel's
        NON-.text-900 text - the `.text-body` user-menu links, the li/button menu rows - broken. So
        each surface is asserted to be its DARK tier AND proven not to be core's light literal, and
        the readability assertions are measured against the RESOLVED panel, never a hardcoded backdrop.

        RED BEFORE GREEN (proven by reverting the $o-burger-* block at the end of dark_palette.scss):
        the panel resolves #ffffff, so the not-light assertion fires; the section title resolves
        #EDF4F5 on it at 1.11:1, so the AA assertion fires; the topbar resolves #f8f9fa with #000000
        text, so its not-light assertions fire. All pass only once the surface is darkened.

        The entry-row composite is the third leg and is deliberately green in BOTH the fully-light and
        the fully-dark state (core's light island is internally consistent at 6.23:1). It is the guard
        for the DANGEROUS PARTIAL fix - darkening the panel while leaving `$o-burger-base-color` at
        $o-gray-800, which composites rgba(52,58,64,.8) to #3E454C on #111B1E = 1.80:1.

        The LIGHT arm asserts all four tokens keep core's values in web.assets_backend: this is a
        dark-bundle-only change (dark_palette.scss is contributed to web.assets_web_dark alone), and
        the burger panel must stay white-with-dark-text in light mode.

        MODEL SCOPE (stated, not hidden): the panels are `t-portal="'body'"` so their ancestor pool is
        the panel root alone; the app-menu sidebar is modelled because it is what the review measured,
        and the user-burger panel compiles from the same nested selector group. Menu rows are bare
        `<li>`/`<button>`, which the class-only cascade model cannot address, so they are read through
        the focused :func:`_winning_burger_entry_declaration`."""
        dark_css = self._compiled_css(DARK_BUNDLE)
        light_css = self._css()

        panel = {
            "classes": BURGER_PANEL_CLASSES, "ancestors": BURGER_SIDEBAR_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        topbar = {
            "classes": BURGER_TOPBAR_CLASSES, "ancestors": BURGER_SIDEBAR_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        section_title = {
            "classes": BURGER_SECTION_TITLE_CLASSES,
            "ancestors": BURGER_SECTION_TITLE_ANCESTORS, "prev_sibling": frozenset(),
        }

        # --- 1. The panel surface itself ---------------------------------------------------------
        dark_panel = self._resolve_colour(
            dark_css, [panel], BACKGROUND_PROPS, "dark burger/app-menu sidebar panel"
        )
        self.assertNotEqual(
            dark_panel, CORE_BURGER_PANEL_BG,
            "The mobile burger / app-menu sidebar panel is still core's %s in web.assets_web_dark - "
            "an unthemed WHITE island in dark mode. $o-burger-base-bg was not re-pointed in "
            "dark_palette.scss, so every dark-tier colour drawn on this panel is dark-on-white."
            % CORE_BURGER_PANEL_BG,
        )
        self.assertEqual(
            dark_panel, DARK_BURGER_PANEL,
            "The dark burger/app-menu sidebar panel compiled to %s instead of the panel tier %s (the "
            "same tier as the form sheet and card, so the sidebar reads as part of the dark app)."
            % (dark_panel, DARK_BURGER_PANEL),
        )

        # --- 2. The section title that failed - measured on the RESOLVED panel --------------------
        dark_title = self._effective_label_colour(
            dark_css, [section_title, panel], "dark burger sidebar section title"
        )
        title_ratio = _contrast_ratio(dark_title, dark_panel)
        self.assertGreaterEqual(
            title_ratio, WCAG_AA_NORMAL_TEXT,
            "The `web.SectionMenu` sidebar section title resolves %s on the burger panel %s = "
            "%.2f:1, below WCAG AA %.1f:1. This is the live-measured 1.11:1 defect: the `.text-900` "
            "emphasis re-point gives the title the dark body tier while core keeps the panel white."
            % (dark_title, dark_panel, title_ratio, WCAG_AA_NORMAL_TEXT),
        )

        # --- 3. The panel's own menu rows (li/button), at core's .8 alpha -------------------------
        raw_entry = _winning_burger_entry_declaration(dark_css, ("color",))
        self.assertIsNotNone(
            raw_entry,
            "No compiled `.o_burger_menu_content li/button` colour rule applies in the dark bundle - "
            "core moved or renamed the burger menu rows; re-ground this guard.",
        )
        dark_entry = _normalize_colour(raw_entry)
        self.assertIsNotNone(
            dark_entry,
            "The dark burger menu-row colour %r carries no resolvable colour." % raw_entry,
        )
        dark_entry_composite = _composite_over(
            dark_entry, dark_panel, _alpha_of(raw_entry)
        )
        entry_ratio = _contrast_ratio(dark_entry_composite, dark_panel)
        self.assertGreaterEqual(
            entry_ratio, WCAG_AA_NORMAL_TEXT,
            "A burger sidebar menu row composites to %s on the darkened panel %s = %.2f:1, below "
            "WCAG AA %.1f:1. The panel was darkened but $o-burger-base-color still carries core's "
            "%s, so the rows are dark-on-dark - darken the text token too, do not leave the fix half "
            "done." % (dark_entry_composite, dark_panel, entry_ratio, WCAG_AA_NORMAL_TEXT,
                        CORE_BURGER_ENTRY_TEXT),
        )

        # --- 4. The topbar band above the panel ---------------------------------------------------
        dark_topbar = self._resolve_colour(
            dark_css, [topbar], BACKGROUND_PROPS, "dark burger sidebar topbar"
        )
        self.assertNotEqual(
            dark_topbar, CORE_BURGER_TOPBAR_BG,
            "The burger sidebar topbar is still core's light %s in the dark bundle - the panel was "
            "darkened but its topbar was left behind." % CORE_BURGER_TOPBAR_BG,
        )
        self.assertEqual(
            dark_topbar, DARK_BURGER_TOPBAR,
            "The dark burger sidebar topbar compiled to %s instead of the raised tier %s."
            % (dark_topbar, DARK_BURGER_TOPBAR),
        )
        dark_topbar_text = self._effective_label_colour(
            dark_css, [topbar], "dark burger sidebar topbar text"
        )
        topbar_ratio = _contrast_ratio(dark_topbar_text, dark_topbar)
        self.assertGreaterEqual(
            topbar_ratio, WCAG_AA_NORMAL_TEXT,
            "The burger sidebar topbar text resolves %s on the darkened topbar %s = %.2f:1, below "
            "WCAG AA %.1f:1 - $o-burger-topbar-color still carries core's %s (the `.o_sidebar_close` "
            "close button inherits it through `.text-reset`)."
            % (dark_topbar_text, dark_topbar, topbar_ratio, WCAG_AA_NORMAL_TEXT,
               CORE_BURGER_TOPBAR_TEXT),
        )

        # --- 5. LIGHT arm: the panel stays white-with-dark-text (dark-bundle-only change) ---------
        light_panel = self._resolve_colour(
            light_css, [panel], BACKGROUND_PROPS, "light burger/app-menu sidebar panel"
        )
        self.assertEqual(
            light_panel, CORE_BURGER_PANEL_BG,
            "The burger sidebar panel must keep core's %s in web.assets_backend - the dark surface "
            "override leaked out of web.assets_web_dark; it compiled to %s."
            % (CORE_BURGER_PANEL_BG, light_panel),
        )
        light_title = self._effective_label_colour(
            light_css, [section_title, panel], "light burger sidebar section title"
        )
        self.assertEqual(
            light_title, LIGHT_BODY_TEXT,
            "The light burger sidebar section title must keep core's near-black %s on the white "
            "panel; it resolved %s." % (LIGHT_BODY_TEXT, light_title),
        )
        light_topbar = self._resolve_colour(
            light_css, [topbar], BACKGROUND_PROPS, "light burger sidebar topbar"
        )
        self.assertEqual(
            light_topbar, CORE_BURGER_TOPBAR_BG,
            "The burger sidebar topbar must keep core's %s in light mode; it compiled to %s."
            % (CORE_BURGER_TOPBAR_BG, light_topbar),
        )
        light_entry_raw = _winning_burger_entry_declaration(light_css, ("color",))
        self.assertEqual(
            _normalize_colour(light_entry_raw or ""), CORE_BURGER_ENTRY_TEXT,
            "The light burger menu rows must keep core's %s; they compiled to %r."
            % (CORE_BURGER_ENTRY_TEXT, light_entry_raw),
        )
        self.assertAlmostEqual(
            _alpha_of(light_entry_raw), CORE_BURGER_ENTRY_TEXT_ALPHA, places=3,
            msg="The light burger menu rows must keep core's .8 alpha arm (burger_menu.scss:60); "
                "%r carries a different opacity." % light_entry_raw,
        )

    # ----------------------------------------------------------------------------------------
    # 20. `.text-secondary` - the invisible-text a11y landmine (2026-08-03)
    # ----------------------------------------------------------------------------------------
    def test_text_secondary_utility_is_readable_in_both_schemes(self):
        """`.text-secondary` must clear WCAG AA in BOTH schemes - and move NOTHING else.

        THE DEFECT. Bootstrap derives the TEXT utility from $theme-colors (_maps.scss:99-111), and
        Odoo's BACKEND re-declares `$secondary: $gray-300` (bootstrap_overridden.scss:32) because the
        same token also paints the SURFACE tier. So `.text-secondary` compiles to #DEE2E6 - 1.30:1 on
        white, INVISIBLE. It is a latent landmine rather than a visible bug: core barely uses the
        class, but every addon author and every Studio user who types it gets unreadable text.
        Odoo's own FRONTEND does not have it (pre_variables.scss:64 keeps stock $gray-600).

        WHY THIS ALSO ASSERTS THAT NOTHING MOVED. The obvious fix - flipping the shared `$secondary`
        to $gray-600 - would repaint the whole SURFACE tier with it: ~30 `border-secondary` hairlines
        across mail/Discuss (sidebar divider, DiscussContent header, chat-window header rule, chat
        bubble, quick-reaction menu, notification items, thread panels) plus every `.bg-secondary` /
        `.text-bg-secondary` chip, whose color-contrast() foreground would additionally flip from
        black to white. That is a restyle of unrelated components, not an a11y fix. The BUSINESS RULE
        under guard is therefore two-sided: the TEXT tier becomes readable AND the shared
        `--secondary-rgb` surface token stays exactly where core put it. The second half is what
        makes this test able to fail a well-meant "just change $secondary" regression.

        DARK IS NOT FREE. #6C757D is only 3.73:1 on the dark panel, so the fix cannot be a single
        literal recompiled into both bundles - hence the token's dark arm (#8EA5A8, 6.75:1).

        WOULD FAIL IF REVERTED: dropping the `.text-secondary` rule returns 1.30:1 in light;
        dropping only its dark arm returns 3.73:1 in dark; "fixing" it by flipping $secondary
        instead trips the --secondary-rgb non-regression assertion."""
        element = {
            "classes": TEXT_SECONDARY_CLASSES, "ancestors": TEXT_SECONDARY_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        arms = (
            ("light", BACKEND_BUNDLE, WHITE),
            ("dark", DARK_BUNDLE, DARK_BODY_BG),
        )
        for arm, bundle_name, surface in arms:
            css = self._compiled_css(bundle_name)
            colour = self._resolve_colour(
                css, [element], ("color",), ".text-secondary (%s arm)" % arm
            )
            if arm == "light":
                self.assertNotEqual(
                    colour, CORE_INVISIBLE_TEXT_SECONDARY,
                    "`.text-secondary` still compiles to core's surface grey %s in the light "
                    "bundle - 1.30:1 on white, i.e. invisible. Bootstrap's utility ships "
                    "`!important`, so an un-flagged override is dead however specific it is."
                    % CORE_INVISIBLE_TEXT_SECONDARY,
                )
            ratio = _contrast_ratio(colour, surface)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "`.text-secondary` renders %s on the %s surface %s - %.2f:1, below the WCAG AA "
                "normal-text threshold of %.1f:1."
                % (colour, arm, surface, ratio, WCAG_AA_NORMAL_TEXT),
            )

            # ... and the SURFACE tier must not have moved with it. `--secondary-rgb` is the shared
            # :root token .bg-secondary / .border-secondary / .text-bg-secondary all read.
            surface_tokens = [
                value.replace(" ", "")
                for value in self._root_custom_prop_values(css, "secondary-rgb")
            ]
            self.assertTrue(
                surface_tokens,
                "No :root --secondary-rgb is emitted in %s, so this guard cannot prove the surface "
                "tier is untouched. Re-ground it against the token Bootstrap now uses."
                % bundle_name,
            )
            self.assertEqual(
                surface_tokens[-1], CORE_SECONDARY_RGB,
                "The shared --secondary-rgb surface token compiled to %r instead of core's %r in "
                "%s. Someone flipped `$secondary` itself: that fixes the text but ALSO repaints "
                "every .bg-secondary chip and ~30 .border-secondary hairlines across mail/Discuss, "
                "and flips .text-bg-secondary's color-contrast() foreground. Correct the TEXT tier "
                "only (the $o-viin-text-secondary token)."
                % (surface_tokens[-1], CORE_SECONDARY_RGB, bundle_name),
            )

    # ----------------------------------------------------------------------------------------
    # 21. `.btn-secondary` - the missing DARK arm of the neutral button (2026-08-03)
    # ----------------------------------------------------------------------------------------
    def test_dark_neutral_button_is_a_dark_pill_and_the_light_one_is_untouched(self):
        """In dark mode `.btn-secondary` must be a DARK pill, and light mode must not move.

        THE DEFECT. Core keys the neutral button off the fixed grayscale ramp
        (primary_variables.scss:247-250: $o-gray-300 fill, $o-gray-900 label). dark_palette.scss
        deliberately does not re-point $o-gray-* (compile-time literals depend on it), so in the
        recompiled web.assets_web_dark every `.btn-secondary` stayed #212529 on #DEE2E6 - light-grey
        pills floating on the #0B1315 canvas: the pager arrows, the RESTING chatter "Log note" /
        "Activity" toggles, the control-panel custom buttons.

        WHAT IS ASSERTED, AND WHY NOT AN EXACT HEX. The behaviour is "the pill became a DARK surface
        carrying a readable LIGHT label", so the guard measures exactly that - the fill is darker
        than its own label, and the pair clears AA - rather than pinning one design hex that a later
        tuning pass would have to edit. The pre-fix state fails BOTH halves: #DEE2E6 is far LIGHTER
        than its #212529 label.

        THE NON-REGRESSION HALF IS THE REAL RISK. The fix merges one key into $o-btns-bs-override,
        and that map is read by more than `.btn-secondary`: a plain assignment (instead of
        map-merge) would wipe the cluster's AA-teal "primary" entry and hand `.btn-primary` back to
        the flat 2.33:1 decorative teal - asserted below, in BOTH bundles.

        SCOPE CHANGE 2026-08-03 - THE ACTIVE TRIO LEFT THIS GUARD, AND THAT IS THE POINT.
        This test used to also assert that `--o-statusbar-background-active` and
        `--o-statusbar-border-active` were byte-IDENTICAL in the two bundles, on the theory that the
        ACTIVE keys must never differ by scheme. The owner's defect report retired that theory: the
        value being forwarded is core's LIGHT #C6EDF1, and forwarding it into dark is exactly what
        put a glaring cyan slab carrying a 1.25:1 WHITE label on the dark form header. A parity
        assertion structurally cannot see that - it compares the two bundles to each other and never
        to a surface. The current-step requirement now lives in
        test_dark_statusbar_current_step_is_a_dark_surface_with_a_readable_label, which measures the
        label against the fill in each scheme and separately pins light to core's value. The HOVER
        key stays here: it is this map's own hover state, not the active trio.
        (The stat-button border/hover and the mobile stat-strip divider read
        $o-btns-bs-OUTLINE-override - a different map, with its own dark arm since the same date and
        its own guards below.)

        WOULD FAIL IF REVERTED: dropping dark_buttons.scss restores the light-grey pill and fails
        the "fill darker than label" assertion; using `$o-btns-bs-override: (...)` instead of
        map-merge fails the .btn-primary assertion."""
        dark_css = self._compiled_css(DARK_BUNDLE)
        light_css = self._compiled_css(BACKEND_BUNDLE)
        pager = {
            "classes": PAGER_PREVIOUS_CLASSES, "ancestors": PAGER_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        # --- light arm: unchanged, so the dark assertions below are a real DELTA, not a rewrite.
        light_fill = self._resolve_colour(
            light_css, [pager], BACKGROUND_PROPS, "light .btn-secondary fill"
        )
        self.assertEqual(
            light_fill, CORE_LIGHT_BTN_SECONDARY_BG,
            "The LIGHT `.btn-secondary` compiled to %s instead of core's %s. The dark arm must not "
            "leak into web.assets_backend - dark_buttons.scss is contributed to the dark bundle "
            "ONLY." % (light_fill, CORE_LIGHT_BTN_SECONDARY_BG),
        )

        # --- dark arm: a dark pill with a readable light label.
        dark_fill = self._resolve_colour(
            dark_css, [pager], BACKGROUND_PROPS, "dark .btn-secondary fill"
        )
        dark_label = self._resolve_colour(
            dark_css, [pager], ("color",), "dark .btn-secondary label"
        )
        self.assertNotEqual(
            dark_fill, CORE_LIGHT_BTN_SECONDARY_BG,
            "The dark `.btn-secondary` still compiles core's light grey %s - a light-grey pill on "
            "the %s dark canvas. $o-btns-bs-override needs its dark 'secondary' entry."
            % (CORE_LIGHT_BTN_SECONDARY_BG, DARK_APP_BG),
        )
        self.assertLess(
            _relative_luminance(dark_fill), _relative_luminance(dark_label),
            "The dark `.btn-secondary` renders the label %s on the LIGHTER fill %s - it is still a "
            "light chip, not a dark pill. In dark mode the control surface must be darker than the "
            "text it carries." % (dark_label, dark_fill),
        )
        ratio = _contrast_ratio(dark_label, dark_fill)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The dark `.btn-secondary` renders %s on %s - %.2f:1, below the WCAG AA normal-text "
            "threshold of %.1f:1." % (dark_label, dark_fill, ratio, WCAG_AA_NORMAL_TEXT),
        )

        # --- non-regression 1: the AA-teal primary button survived the map-merge.
        primary_button = {
            "classes": frozenset({"btn", "btn-primary"}),
            "ancestors": frozenset({"o_web_client", "o_action_manager", "o_view_controller"}),
            "prev_sibling": frozenset(),
        }
        for arm, css in (("light", light_css), ("dark", dark_css)):
            primary_fill = self._resolve_colour(
                css, [primary_button], BACKGROUND_PROPS, ".btn-primary fill (%s arm)" % arm
            )
            self.assertEqual(
                primary_fill, CHROME_BASE,
                "`.btn-primary` compiled to %s instead of the AA chrome base %s in the %s bundle. "
                "dark_buttons.scss must map-merge INTO $o-btns-bs-override; a plain assignment "
                "wipes the cluster's 'primary' entry and core's flat decorative teal takes over."
                % (primary_fill, CHROME_BASE, arm),
            )

        status_root = {
            "classes": frozenset({"o_statusbar_status"}), "ancestors": STATUSBAR_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        # --- the HOVER key DELIBERATELY moves. statusbar_field.scss:16 also reads
        # `hover-background` from the same entry, so re-tinting the neutral pill re-tints the
        # statusbar's hovered step too - which is a SECOND dark defect being closed, not collateral
        # damage: core's $o-gray-400 #CED4DA is a near-white flash on a dark statusbar, and the dark
        # step label (#EDF4F5) on it measures ~1.25:1. The rule under guard is therefore "the hovered
        # step is a DARK surface in the dark bundle, and stays core's light grey in the light one".
        light_hover = _computed_value(light_css, [status_root], ("--o-statusbar-background-hover",))
        dark_hover = _computed_value(dark_css, [status_root], ("--o-statusbar-background-hover",))
        light_hover_colour = _normalize_colour(light_hover or "")
        dark_hover_colour = _normalize_colour(dark_hover or "")
        self.assertIsNotNone(
            light_hover_colour,
            "--o-statusbar-background-hover carries no resolvable colour in the light bundle (%r) - "
            "core moved the statusbar hover to a different lever." % light_hover,
        )
        self.assertIsNotNone(
            dark_hover_colour,
            "--o-statusbar-background-hover carries no resolvable colour in the dark bundle (%r)."
            % dark_hover,
        )
        self.assertLess(
            _relative_luminance(dark_hover_colour), _relative_luminance(light_hover_colour),
            "The dark statusbar HOVER fill (%s) is not darker than the light one (%s). It is seeded "
            "from the neutral button map's `hover-background`, so the dark arm must darken it - "
            "core's light grey is a near-white flash on a dark statusbar (~1.25:1 under the dark "
            "step label)." % (dark_hover_colour, light_hover_colour),
        )
        self.assertGreaterEqual(
            _contrast_ratio(DARK_READABLE_TEXT, dark_hover_colour), WCAG_AA_NORMAL_TEXT,
            "The dark statusbar step label %s on the hovered fill %s is %.2f:1, below the WCAG AA "
            "normal-text threshold of %.1f:1."
            % (DARK_READABLE_TEXT, dark_hover_colour,
               _contrast_ratio(DARK_READABLE_TEXT, dark_hover_colour), WCAG_AA_NORMAL_TEXT),
        )

    # ----------------------------------------------------------------------------------------
    # 22. List GROUP HEADER - grouping is STRUCTURE, so the group name is purple (2026-08-03)
    # ----------------------------------------------------------------------------------------
    def test_list_group_header_name_renders_the_structure_purple_in_both_schemes(self):
        """A grouped-list group name must render the STRUCTURE purple, readably, in both schemes.

        OWNER DECISION 2026-08-03. Under the colour law a group header is not an action - it is the
        structure the records were re-organised into - so it is the list-view counterpart of the
        purple group-by facet and reads as the same idea.

        THE TRAP IS IMPORTANCE, TWICE OVER. Core stamps the name cell with one of two Bootstrap
        colour utilities depending on fold state (list_renderer.xml:215): `.text-black` when open,
        `.text-body` when folded - and BOTH are `!important` (Odoo's o-print-color emits
        `color: var(--color) !important`; Bootstrap's utility emits
        `color: rgba(var(--body-color-rgb), ...) !important`). Importance beats specificity, so an
        un-flagged declaration is dead at ANY specificity, and the two shapes resolve through
        DIFFERENT levers - a fix that beats only one of them is a latent half-fix that shows up the
        moment a user folds a group. Both are therefore asserted separately.

        Re-pointing either underlying token instead was rejected as far too broad: `--color` is
        shared by every o-print-color utility and `--body-color-rgb` by the whole body text tier.

        WOULD FAIL IF REVERTED: dropping `!important` leaves core's utility winning and the cell
        resolves to #000000 (open) / the body colour (folded); styling only `.o_group_header`
        instead of the `.o_group_name` cell never beats the utility on the cell itself."""
        expected_light_purple = self._brand_secondary_ssot()
        flat_brand_teal = self._assert_flat_teal_available()
        shapes = (
            ("open group (core adds .text-black)", LIST_GROUP_NAME_OPEN),
            ("folded group (core adds .text-body)", LIST_GROUP_NAME_FOLDED),
        )
        arms = (
            ("light", BACKEND_BUNDLE, LIST_SURFACE_LIGHT),
            ("dark", DARK_BUNDLE, LIST_SURFACE_DARK),
        )
        for arm, bundle_name, surface in arms:
            css = self._compiled_css(bundle_name)
            for shape, classes in shapes:
                label = "%s [%s arm]" % (shape, arm)
                element = {
                    "classes": classes, "ancestors": LIST_GROUP_NAME_ANCESTORS,
                    "prev_sibling": frozenset(),
                }
                colour = self._resolve_colour(css, [element], ("color",), label)
                self.assertNotEqual(
                    colour, BLACK,
                    "The %s group name compiled to plain black - core's `.text-black` utility is "
                    "still winning, so the declaration is missing its `!important` (or is on the row "
                    "instead of the .o_group_name cell). In the DARK bundle that is 1.16:1 on the "
                    "#111B1E list surface, i.e. invisible. (`.text-black` is a compile-time grayscale "
                    "literal; RC-4 on 2026-08-03 gave it a class-wide dark re-point alongside "
                    "`.text-900`, but that one is (0,1,0) - this cell's own rule still has to win on "
                    "its own terms, which is what this assertion checks.)" % label,
                )
                self.assertNotIn(
                    colour, (CHROME_BASE, CHROME_DEEP, flat_brand_teal),
                    "The %s group name compiled the teal %s. Grouping is STRUCTURE, not an ACT - "
                    "see the colour law in brand_variables.scss." % (label, colour),
                )
                if arm == "light":
                    self.assertEqual(
                        colour, expected_light_purple,
                        "The %s group name compiled to %s instead of the brand secondary %s "
                        "($o-brand-secondary)." % (label, colour, expected_light_purple),
                    )
                else:
                    # OWNER REVISION 2026-08-03: no purple in dark. Unlike the group-by FACET, this
                    # rule is not simply dropped in dark - dropping it hands the cell back to core's
                    # black-on-dark `.text-black`. The dark arm re-aims it at the bright body tier,
                    # which is both "the default look" the owner named and a fix for that
                    # pre-existing failure. Asserted positively so a future "simplification" that
                    # deletes the @else arm is caught by more than the black refusal above.
                    self.assertNotIn(
                        colour, (expected_light_purple, RETIRED_DARK_PURPLE),
                        "The %s group name compiled the purple %s in the DARK bundle. The purple "
                        "accent is light-only from 2026-08-03." % (label, colour),
                    )
                    self.assertEqual(
                        colour, DARK_READABLE_TEXT,
                        "The %s group name compiled %s in the dark bundle instead of the bright "
                        "body-text tier %s. That is the default the owner asked for, and it is the "
                        "only value that also beats core's black-on-dark `.text-black`."
                        % (label, colour, DARK_READABLE_TEXT),
                    )
                ratio = _contrast_ratio(colour, surface)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "The %s group name renders %s on the %s list surface %s - %.2f:1, below the "
                    "WCAG AA normal-text threshold of %.1f:1."
                    % (label, colour, arm, surface, ratio, WCAG_AA_NORMAL_TEXT),
                )

    # ----------------------------------------------------------------------------------------
    # 23. NO BRAND PURPLE ANYWHERE IN THE DARK BUNDLE (owner revision 2026-08-03)
    # ----------------------------------------------------------------------------------------
    def test_no_brand_purple_survives_anywhere_in_the_dark_bundle(self):
        """web.assets_web_dark must contain NO occurrence of either brand purple. At all.

        WHY A WHOLE-BUNDLE SCAN ON TOP OF THE PER-SURFACE GUARDS. The per-surface tests above prove
        that the FOUR named surfaces are purple-free in dark. They cannot prove the RULE the owner
        actually stated - "no purple in dark mode at all" - because they only look where someone
        already thought to look. This one is the rule itself, and it is the guard that catches the
        NEXT purple rule somebody adds without the `@if not $o-viin-dark-bundle` wrapper, and the
        core consumers nobody in this repo owns (form_controller.scss's mobile form label,
        search_view.scss's section divider, POS's backend kanban) if the token re-point were ever
        reverted.

        It is cheap and it is exact: the purple is a brand hex, so it either appears in the compiled
        text or it does not. Both spellings the compiler can emit are searched - the `#rrggbb`
        literal and the `r,g,b` triplet Odoo's `to-rgb()` produces for the o-print-color mixin - and
        BOTH purples are searched, the light #7F4282 (which would mean a rule was not guarded) and
        the retired dark #B589B8 (which would mean the deleted dark arm came back).

        NON-VACUOUS BY CONSTRUCTION: the same scan is run against the LIGHT bundle and asserted to
        FIND the purple there. A typo in the needle, a bundle that failed to build, or a purple that
        silently disappeared from light too would all make the dark half pass for the wrong reason;
        the light half turns each of those into a failure.

        WOULD FAIL IF REVERTED: giving $o-brand-secondary a dark arm again, or adding an unguarded
        purple rule to brand_cascade.scss / home_menu.scss / the mail SCSS."""
        light_purple = self._brand_secondary_ssot()
        needles = {
            "the LIGHT brand purple %s (an unguarded rule reached the dark bundle)" % light_purple:
                _colour_spellings(light_purple),
            "the RETIRED dark purple %s (the deleted dark arm is back)" % RETIRED_DARK_PURPLE:
                _colour_spellings(RETIRED_DARK_PURPLE),
        }

        # Control: the light bundle MUST still contain the light purple, or this scan proves nothing.
        light_css = self._compiled_css(BACKEND_BUNDLE).lower()
        self.assertTrue(
            any(spelling in light_css for spelling in _colour_spellings(light_purple)),
            "The brand purple %s does not appear in the compiled LIGHT bundle at all. Either the "
            "purple accent was removed from light too - which the owner did NOT ask for; it is the "
            "group-by facet, the list group header, the home-menu section label and the stat value - "
            "or this scan's needles are wrong, in which case the dark half below is vacuous."
            % light_purple,
        )

        dark_css = self._compiled_css(DARK_BUNDLE).lower()
        for description, spellings in needles.items():
            for spelling in spellings:
                index = dark_css.find(spelling)
                if index == -1:
                    continue
                # Report the offending rule, not just "found it", so the fix is locatable.
                start = dark_css.rfind("}", 0, index) + 1
                self.fail(
                    "web.assets_web_dark contains %s, spelled %r. The purple accent is LIGHT-MODE "
                    "ONLY (owner revision 2026-08-03): every rule painting it must sit inside "
                    "`@if not $o-viin-dark-bundle`, and $o-brand-secondary itself is re-pointed to "
                    "the neutral muted tier in dark_palette.scss for the core rules we cannot guard. "
                    "Offending rule: %s"
                    % (description, spelling, dark_css[start:index + 40].strip()),
                )

    # ----------------------------------------------------------------------------------------
    # 24. OWNER DEFECT 2026-08-03 - the dark CURRENT statusbar step (glaring slab, sunken label)
    # ----------------------------------------------------------------------------------------
    def test_dark_statusbar_current_step_is_a_dark_surface_with_a_readable_label(self):
        """The current statusbar step must carry a readable label on a scheme-appropriate fill.

        THE DEFECT, AS THE OWNER SAW IT: on a dark sale order the current step was "a very bright
        near-white/cyan slab with WHITE text on it" - both painfully bright against the #0B1315
        canvas and unreadable. Live-measured before the fix: #FFFFFF on #C6EDF1 = 1.25:1.

        WHERE THE TWO HALVES COME FROM, because they have different causes and the guard has to see
        both. The FILL is core's $o-component-active-bg = `mix($o-action, $o-gray-100, 20%)`
        (primary_variables.scss:133), reaching the step through statusbar_field.scss:14 - a light
        cyan tint that no $body-*-bg override touches, so it recompiled verbatim into the dark
        bundle. The LABEL is not the button map's `color` key at all: core renders the current step
        `disabled` (statusbar_field.xml:40), and Bootstrap's `button-variant` defaults
        --btn-disabled-color to `color-contrast($background)` - white, once dark_buttons.scss made
        the resting fill dark. So the fix moved BOTH tokens toward each other and the guard measures
        the pair, not either one.

        WHAT IS ASSERTED, AND WHY NOT A PINNED HEX. The requirement is "readable, and a surface
        rather than a light slab", so the dark arm is held to three measured properties - AA against
        its own label, lighter than the panel it sits on (it is a raised surface, not a hole), and
        within a modest contrast band of that panel (it is a surface tier, not a white slab). A hex
        would have to be edited by the next tuning pass; these would not.

        LIGHT IS PINNED, NOT MEASURED. The owner is happy with light mode, so the light fill is
        asserted EQUAL to core's #C6EDF1: any change there is a regression by definition, and
        pinning it also makes the dark half a real DELTA rather than a rewrite of both arms.

        WOULD FAIL IF REVERTED: dropping the $o-component-active-* dark arm from dark_palette.scss
        puts #C6EDF1 back in the dark bundle, which fails the "not core's light fill" assertion
        first and the 1.25:1 AA assertion immediately after."""
        light_css = self._compiled_css(BACKEND_BUNDLE)
        dark_css = self._compiled_css(DARK_BUNDLE)
        status_root = {
            "classes": frozenset({"o_statusbar_status"}), "ancestors": STATUSBAR_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        # --- light arm: pinned to core, so the dark assertions below are a delta.
        light_fill = self._resolve_colour(
            light_css, [status_root], ("--o-statusbar-background-active",),
            "light statusbar current-step fill",
        )
        self.assertEqual(
            light_fill, CORE_LIGHT_STATUSBAR_ACTIVE_BG,
            "The LIGHT statusbar current-step fill compiled to %s instead of core's %s. Light mode "
            "is the arm the owner signed off on; the dark arm belongs in dark_palette.scss, which "
            "is contributed to web.assets_web_dark ONLY." % (light_fill, CORE_LIGHT_STATUSBAR_ACTIVE_BG),
        )

        for arm, css, panel in (
            ("light", light_css, WHITE),
            ("dark", dark_css, DARK_BODY_BG),
        ):
            fill = self._resolve_colour(
                css, [status_root], ("--o-statusbar-background-active",),
                "%s statusbar current-step fill" % arm,
            )
            label = self._resolve_colour(
                css, [STATUSBAR_CURRENT_STEP, status_root], ("color",),
                "%s statusbar current-step label" % arm,
            )
            ratio = _contrast_ratio(label, fill)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "The %s statusbar current step renders its label %s on the fill %s - %.2f:1, below "
                "the WCAG AA normal-text threshold of %.1f:1. Core paints a DISABLED button from "
                "--btn-disabled-color (color-contrast of the resting fill), so the label follows the "
                "neutral button map while the fill follows $o-component-active-bg: the two must be "
                "moved together." % (arm, label, fill, ratio, WCAG_AA_NORMAL_TEXT),
            )

        # --- dark arm: a raised dark SURFACE, not the light slab forwarded from core.
        dark_fill = self._resolve_colour(
            dark_css, [status_root], ("--o-statusbar-background-active",),
            "dark statusbar current-step fill",
        )
        self.assertNotEqual(
            dark_fill, CORE_LIGHT_STATUSBAR_ACTIVE_BG,
            "The dark statusbar current step still compiles core's LIGHT fill %s. That is the cyan "
            "slab the owner reported: 14.0:1 against the %s panel, with a 1.25:1 white label on it."
            % (CORE_LIGHT_STATUSBAR_ACTIVE_BG, DARK_BODY_BG),
        )
        self.assertGreater(
            _relative_luminance(dark_fill), _relative_luminance(DARK_BODY_BG),
            "The dark statusbar current-step fill %s is DARKER than the %s panel it sits on. The "
            "current step must read as raised above the bar, like every other dark surface tier in "
            "this palette - not as a hole punched in it." % (dark_fill, DARK_BODY_BG),
        )
        glare = _contrast_ratio(dark_fill, DARK_BODY_BG)
        self.assertLessEqual(
            glare, DARK_ACTIVE_FILL_MAX_GLARE,
            "The dark statusbar current-step fill %s is %.2f:1 against the %s panel - a light slab, "
            "not a surface tier. Light mode's own active fill sits only 1.25:1 from its white sheet; "
            "the dark arm is held to the same order of magnitude (ceiling %.1f:1) so the current "
            "step is marked by its outline and its fill TIER, not by brightness."
            % (dark_fill, glare, DARK_BODY_BG, DARK_ACTIVE_FILL_MAX_GLARE),
        )

    # ----------------------------------------------------------------------------------------
    # 25. OWNER DEFECT 2026-08-03 - the stat-button BORDER (a white hairline on the dark sheet)
    # ----------------------------------------------------------------------------------------
    def test_stat_button_border_is_a_subtle_hairline_and_its_label_is_readable_in_both_schemes(self):
        """A smart button's border must separate it without glaring, in both schemes.

        THE DEFECT. form_compiler.js:157-164 compiles every smart button as
        `oe_stat_button btn btn-outline-secondary`, and Odoo expands
        $o-btns-bs-outline-override through the SAME `button-variant` mixin as the filled map
        (bootstrap_review_backend.scss:32-45 - NOT Bootstrap's `button-outline-variant`), so its
        `border` key is a literal border colour. Core keys it to $o-gray-300 #DEE2E6, a fixed
        grayscale the dark palette deliberately does not re-point: live-measured at 13.45:1 against
        the #111B1E form sheet, i.e. a pure-white hairline round every stat button. The same map's
        `color` key (#212529) is what a stat button WITHOUT the StatInfo template renders its bare
        `<span>` in (button_box.scss:65) - 1.14:1 on that sheet, invisible.

        A CONTRAST BAND, NOT A HEX. "Subtle hairline" is a relationship, not a value: light mode's
        own border is 1.30:1 on white. Both arms are held to the same band, so the guard states the
        design rule once and neither arm can drift into the other's failure mode - too faint to
        separate the buttons, or bright enough to glare.

        THE LABEL HALF IS NOT A SEPARATE CONCERN. Both values come from the same map entry, and
        fixing only the border would leave a dark-on-dark label; asserting them together is what
        makes a partial fix fail.

        WOULD FAIL IF REVERTED: dropping the $o-btns-bs-outline-override dark arm from
        dark_buttons.scss restores #DEE2E6/#212529, failing the band and the AA assertion."""
        light_css = self._compiled_css(BACKEND_BUNDLE)
        dark_css = self._compiled_css(DARK_BUNDLE)

        # Light is pinned to core's own values: the owner asked for no change there.
        light_border = self._resolve_colour(
            light_css, [STAT_BUTTON], ("--btn-border-color",), "light stat-button border"
        )
        self.assertEqual(
            light_border, CORE_LIGHT_BTN_OUTLINE_BORDER,
            "The LIGHT stat-button border compiled to %s instead of core's %s - the dark arm leaked "
            "into web.assets_backend." % (light_border, CORE_LIGHT_BTN_OUTLINE_BORDER),
        )

        for arm, css, panel in (
            ("light", light_css, WHITE),
            ("dark", dark_css, DARK_BODY_BG),
        ):
            border = self._resolve_colour(
                css, [STAT_BUTTON], ("--btn-border-color",), "%s stat-button border" % arm
            )
            ratio = _contrast_ratio(border, panel)
            self.assertGreaterEqual(
                ratio, SUBTLE_BORDER_MIN_CONTRAST,
                "The %s stat-button border %s is only %.2f:1 against the %s form sheet - it no "
                "longer separates one smart button from the next."
                % (arm, border, ratio, panel),
            )
            self.assertLessEqual(
                ratio, SUBTLE_BORDER_MAX_CONTRAST,
                "The %s stat-button border %s is %.2f:1 against the %s form sheet - a glaring "
                "hairline, not a subtle one (light mode's own border is 1.30:1 on white). This is "
                "the border the owner reported as 'too much contrast/glare'; point it at the dark "
                "$border-color tier, never at core's $o-gray-300."
                % (arm, border, ratio, panel),
            )

            label = self._resolve_colour(
                css, [STAT_BUTTON], ("--btn-color",), "%s stat-button label" % arm
            )
            label_ratio = _contrast_ratio(label, panel)
            self.assertGreaterEqual(
                label_ratio, WCAG_AA_NORMAL_TEXT,
                "The %s stat-button label %s is %.2f:1 on the %s form sheet, below the WCAG AA "
                "normal-text threshold of %.1f:1. The outline map's `color` key is what a stat "
                "button without the StatInfo template renders its bare <span> in."
                % (arm, label, label_ratio, panel, WCAG_AA_NORMAL_TEXT),
            )

        dark_border = self._resolve_colour(
            dark_css, [STAT_BUTTON], ("--btn-border-color",), "dark stat-button border"
        )
        self.assertNotEqual(
            dark_border, CORE_LIGHT_BTN_OUTLINE_BORDER,
            "The dark stat-button border still compiles core's light grey %s."
            % CORE_LIGHT_BTN_OUTLINE_BORDER,
        )

    # ----------------------------------------------------------------------------------------
    # 26. OWNER DEFECT 2026-08-03 - hovering a stat button made its text white-on-white
    # ----------------------------------------------------------------------------------------
    def test_stat_button_hover_keeps_every_label_it_carries_readable_in_both_schemes(self):
        """Hovering a smart button must not hide the text it carries - in either scheme.

        THE DEFECT, AND WHY IT IS A COLLISION RATHER THAN ONE WRONG VALUE. The hover FILL is core's
        $o-gray-200 #E9ECEF, recompiled unchanged into the dark bundle. The text on it is NOT the
        button's own --btn-hover-color: `.o_stat_text` and `.o_stat_value` both read
        --o-stat-text-color, which brand_cascade.scss correctly pins to the dark body tier #EDF4F5
        in dark. Correct dark text, light hover fill, same pixel: 1.06:1 - the "text white on a
        white background" the owner reported. Neither declaration is wrong on its own, which is
        exactly why the guard resolves every text token that can ride the hover fill and measures
        each against it, rather than asserting a value.

        THREE TOKENS, ON PURPOSE. --btn-hover-color covers a plain `.btn-outline-secondary`
        elsewhere in the backend; --o-stat-text-color covers the stat VALUE and (since the
        2026-08-03 label revision) the stat LABEL as well, because brand_cascade.scss deliberately
        routes both through the one property so they can never drift apart.

        WOULD FAIL IF REVERTED: dropping the $o-btns-bs-outline-override dark arm restores the
        #E9ECEF hover fill and the stat text collapses to 1.06:1 on it."""
        light_css = self._compiled_css(BACKEND_BUNDLE)
        dark_css = self._compiled_css(DARK_BUNDLE)
        buttonbox = {
            "classes": frozenset({"o-form-buttonbox"}), "ancestors": BUTTONBOX_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        light_hover = self._resolve_colour(
            light_css, [STAT_BUTTON], ("--btn-hover-bg",), "light stat-button hover fill"
        )
        self.assertEqual(
            light_hover, CORE_LIGHT_BTN_OUTLINE_HOVER_BG,
            "The LIGHT stat-button hover fill compiled to %s instead of core's %s - the dark arm "
            "leaked into web.assets_backend."
            % (light_hover, CORE_LIGHT_BTN_OUTLINE_HOVER_BG),
        )

        for arm, css in (("light", light_css), ("dark", dark_css)):
            hover_fill = self._resolve_colour(
                css, [STAT_BUTTON], ("--btn-hover-bg",), "%s stat-button hover fill" % arm
            )
            riders = {
                "the button's own hover label (--btn-hover-color)": self._resolve_colour(
                    css, [STAT_BUTTON], ("--btn-hover-color",),
                    "%s stat-button hover label" % arm,
                ),
                "the stat label AND value (--o-stat-text-color)": self._resolve_colour(
                    css, [buttonbox], ("--o-stat-text-color",),
                    "%s stat text colour" % arm,
                ),
            }
            for description, colour in riders.items():
                ratio = _contrast_ratio(colour, hover_fill)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "In the %s bundle, %s compiles to %s and the hovered stat button fills with "
                    "%s - %.2f:1, below the WCAG AA normal-text threshold of %.1f:1. A hover state "
                    "must not hide the text it is highlighting."
                    % (arm, description, colour, hover_fill, ratio, WCAG_AA_NORMAL_TEXT),
                )

        dark_hover = self._resolve_colour(
            dark_css, [STAT_BUTTON], ("--btn-hover-bg",), "dark stat-button hover fill"
        )
        self.assertNotEqual(
            dark_hover, CORE_LIGHT_BTN_OUTLINE_HOVER_BG,
            "The dark stat-button hover still fills with core's near-white %s."
            % CORE_LIGHT_BTN_OUTLINE_HOVER_BG,
        )

    # ----------------------------------------------------------------------------------------
    # 27. OWNER REQUEST 2026-08-03 - the statusbar STEP NUMBERS, on core's arrow steps
    # ----------------------------------------------------------------------------------------
    def test_statusbar_steps_render_a_numbered_marker_that_inherits_its_step_label_colour(self):
        """Every statusbar step must render its ordinal, readably, in both schemes.

        THE REQUEST. "Cả 2 chế độ đều mất các số step ở status bar rồi" - both schemes lost the
        statusbar step numbers when the D6 stepper was reverted - together with the constraint that
        core's chevrons stay ("vẫn muốn giữ cái mũi tên như mặc định"). So the behaviour is: a number
        per step, ON core's arrow geometry.

        WHY THE COLOUR ASSERTION IS AN ABSENCE. statusbar_steps.scss paints the digit
        `currentColor`, so it INHERITS whatever the step's own label resolves to - per step state,
        per scheme, for free. That is the whole colour design, and the way to protect it is to
        assert that the marker declares no colour of its OWN (the moment it does, it can drift from
        its label and needs its own contrast budget and dark arm) and then to measure the label
        pairs the digit therefore inherits. Both step STATES are measured, because they resolve
        through different tokens: the current step is `disabled` (--btn-disabled-color on the active
        fill) and every other step is a resting `.btn-secondary` (--btn-color on --btn-bg).

        THE GEOMETRY HALF IS NOT OPTIONAL. `clip-path: none` on an arrow button is precisely what
        turned core's chevron chain into the rectangles the owner reverted, so this guard also
        proves the polygon is still compiled and is never unset - in both bundles, scanned on the
        RAW rules so no selector shape can slip past a resolver that does not model it. It overlaps
        viin_backend_theme's test_statusbar_steps_keep_cores_arrow_geometry on purpose: that one
        guards the THEME, this one guards the module that now actually ships a statusbar rule.

        WOULD FAIL IF REVERTED: deleting statusbar_steps.scss removes the `attr(data-viin-step)`
        marker rule; giving the marker its own `color` fails the inheritance assertion; adding
        `clip-path: none` back fails the geometry assertion."""
        for bundle_name in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle_name)

            # --- the marker renders the ordinal from the data attribute.
            marker_rules = [
                selector
                for _order, selector, body in _iter_rules(css)
                if "o_viin_numbered_step" in selector
                for value, _important in _declarations(body, {"content"})
                if "attr(data-viin-step)" in value.replace(" ", "")
            ]
            self.assertTrue(
                marker_rules,
                "No rule in %s renders a statusbar step ordinal - nothing declares "
                "`content: attr(data-viin-step)` on an `.o_viin_numbered_step` marker. The step "
                "numbers the owner asked for are simply not in the bundle."
                % bundle_name,
            )

            # --- ... and it carries no colour of its own, so it inherits its step's label.
            for state, element in (
                ("current", STATUSBAR_CURRENT_STEP), ("clickable", STATUSBAR_STEP),
            ):
                marker = dict(element, pseudo_element="after")
                own_colour = _winning_declaration(css, marker, ("color",))
                self.assertIsNone(
                    own_colour,
                    "In %s the %s step's number marker declares its own colour (%r). It must stay "
                    "`currentColor`: that is what guarantees the digit is exactly as readable as "
                    "the label beside it, in every step state and both schemes, without a second "
                    "contrast budget or a dark arm." % (bundle_name, state, own_colour),
                )

            # --- ... and what it inherits clears AA on the step it sits in.
            status_root = {
                "classes": frozenset({"o_statusbar_status"}), "ancestors": STATUSBAR_ANCESTORS,
                "prev_sibling": frozenset(),
            }
            pairs = (
                ("current", STATUSBAR_CURRENT_STEP, ("--o-statusbar-background-active",),
                 [status_root]),
                ("clickable", STATUSBAR_STEP, ("--btn-bg",), [STATUSBAR_STEP]),
            )
            for state, element, fill_props, fill_chain in pairs:
                label = self._resolve_colour(
                    css, [element, status_root], ("color",),
                    "%s %s statusbar step label" % (bundle_name, state),
                )
                fill = self._resolve_colour(
                    css, fill_chain, fill_props,
                    "%s %s statusbar step fill" % (bundle_name, state),
                )
                ratio = _contrast_ratio(label, fill)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "In %s the %s statusbar step renders %s on %s - %.2f:1, below the WCAG AA "
                    "normal-text threshold of %.1f:1. The step NUMBER inherits that same pair, so "
                    "an unreadable label is an unreadable number."
                    % (bundle_name, state, label, fill, ratio, WCAG_AA_NORMAL_TEXT),
                )

            # --- the READONLY statusbar, held to the VISIBILITY floor rather than to AA.
            # sale.order / account.move / purchase.order render every step `disabled`, and core
            # swaps the label onto $text-muted - an ALPHA colour, so it is composited against the
            # step fill before measuring. Formally these are inactive components, which WCAG SC
            # 1.4.3 exempts, so the threshold here is the 3:1 non-text floor rather than 4.5:1;
            # that is also, not coincidentally, what light mode already delivers (3.69:1). The
            # floor is what makes the pre-fix dark value fail: $o-main-color-muted is built from
            # the fixed grayscale ramp, so `rgba(73,80,87,.76)` composited over the dark step
            # #25383C is 1.35:1 - the upcoming stages, and therefore their numbers, simply vanish.
            raw_muted = _winning_declaration(css, STATUSBAR_STEP_DISABLED, ("color",))
            self.assertIsNotNone(
                raw_muted,
                "Nothing in %s gives a DISABLED, non-current statusbar step a colour - core's "
                "`&:disabled &:not(.o_arrow_button_current) { color: $text-muted }` moved, so this "
                "guard needs re-grounding rather than deleting." % bundle_name,
            )
            disabled_fill = self._resolve_colour(
                css, [STATUSBAR_STEP_DISABLED], BACKGROUND_PROPS,
                "%s readonly statusbar step fill" % bundle_name,
            )
            muted = _normalize_colour(raw_muted)
            self.assertIsNotNone(
                muted,
                "The disabled statusbar step label resolves %r in %s, which carries no colour."
                % (raw_muted, bundle_name),
            )
            effective = _composite_over(muted, disabled_fill, _alpha_of(raw_muted))
            muted_ratio = _contrast_ratio(effective, disabled_fill)
            self.assertGreaterEqual(
                muted_ratio, WCAG_NON_TEXT_MIN,
                "In %s a READONLY statusbar renders its upcoming steps %s (composited to %s) on %s "
                "- %.2f:1, under the %.1f:1 visibility floor. An inactive control is exempt from "
                "the 4.5:1 text rule, but not from being visible at all: at this ratio the stages "
                "and their step numbers disappear. $o-main-color-muted is a $o-gray-700 alpha with "
                "no dark arm - give it one in dark_palette.scss, do not patch the statusbar."
                % (bundle_name, raw_muted, effective, disabled_fill, muted_ratio,
                   WCAG_NON_TEXT_MIN),
            )

            # --- and core's chevron geometry is untouched.
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
                "The numbering layer unset core's arrow clip-path in %s, which squares the chevron "
                "into the rectangle the owner reverted on 2026-08-03:\n  %s"
                % (bundle_name, "\n  ".join(unset)),
            )
            self.assertTrue(
                polygons,
                "No compiled rule in %s clips `.o_arrow_button` into a polygon, so the statusbar no "
                "longer renders Odoo CE's chevron steps at all." % bundle_name,
            )

    # ----------------------------------------------------------------------------------------
    # 28. T-2 NON-REGRESSION - the numbering layer touches no statusbar geometry, in source
    # ----------------------------------------------------------------------------------------
    def test_the_statusbar_numbering_layer_declares_no_step_or_container_geometry(self):
        """statusbar_steps.scss must add a marker and nothing that can move the widget's boxes.

        WHY A SOURCE SCAN ON TOP OF THE COMPILED GUARDS. The compiled half above proves the chevron
        is still clipped. It cannot prove the OTHER half of the reverted stepper, because that one
        was invisible in colour and in clip-path: the D6 rule put `padding: 0` + `border: 0` on
        `.o_statusbar_status`, and core's areItemsWrapping() (statusbar_field.js) folds the entire
        bar into one "..." dropdown the moment
        `root.getBoundingClientRect().height > firstItem.getBoundingClientRect().height`. A few
        pixels of container chrome made that permanently true, so the widget collapsed at EVERY
        viewport width - the T-2 bug. No compiled-colour assertion can see it; the honest guard is
        that the file never declares the properties that could cause it.

        The `::after` marker rules are excised before scanning: that box is a pseudo-element, it is
        excluded from both the button's layout and the container's getBoundingClientRect, and
        sizing/bordering it is the entire feature. Its `border-radius: 50%` is pinned separately as
        an explicit allow-list entry in viin_backend_theme/tests/test_theme_radius_is_core.py, so a
        SECOND radius added tomorrow still fails there and gets a decision.

        THIS IS A NON-REGRESSION GUARD, NOT A RED-BEFORE-GREEN ONE, and that is deliberate: it was
        green before the numbering layer existed (there was no file) and it is green after, because
        what it protects is that the layer never GROWS into the thing that was reverted. It is
        capable of failing, and fails the moment anyone adds one of the listed properties.

        WOULD FAIL IF REVERTED: re-adding the stepper's `padding`/`border`/`clip-path` block to this
        file names the property."""
        with open(STATUSBAR_STEPS_SCSS, encoding="utf-8") as handle:
            source = re.sub(r"//[^\n]*", "", handle.read())

        # The scan is scoped to everything OUTSIDE the `::after` marker blocks: that box is the one
        # this file is allowed to create, it is a pseudo-element (excluded from the button's own
        # layout and from getBoundingClientRect on the container), and sizing and bordering it is
        # the whole point. Both marker rules are excised - the base one and the current-step
        # `border-color` modifier - so the scan below sees only rules that style a REAL element.
        marker_blocks = re.findall(r"&[^{}\n]*::after\s*\{[^{}]*\}", source)
        self.assertTrue(
            marker_blocks,
            "statusbar_steps.scss no longer contains a `::after` marker block for this guard to "
            "scope around - re-ground it on the new structure rather than deleting it.",
        )
        outside = source
        for block in marker_blocks:
            outside = outside.replace(block, "")

        # Properties that can move a step box or the measured container. `border-radius` is
        # deliberately NOT one of them (see the docstring), so the `border` pattern excludes it.
        forbidden = ("clip-path", "padding", "padding-top", "padding-bottom", "padding-left",
                     "padding-right", "padding-inline", "padding-block", "margin", "margin-left",
                     "height", "min-height", "max-height", "line-height")
        offenders = [
            "%r" % prop
            for prop in forbidden
            if re.search(r"(?:^|[;{\s])%s\s*:" % re.escape(prop), outside)
        ]
        if re.search(r"(?:^|[;{\s])border(?!-radius)[a-z-]*\s*:", outside):
            offenders.append("'border'")
        self.assertFalse(
            offenders,
            "statusbar_steps.scss declares %s outside the ::after marker. Those properties move the "
            "step box or the measured container, and a container that measures taller than its "
            "first child makes core's areItemsWrapping() collapse the whole statusbar into a single "
            "dropdown at every width (the T-2 regression). The numbering layer is additive only."
            % ", ".join(offenders),
        )
        self.assertNotIn(
            "clip-path", outside,
            "statusbar_steps.scss mentions clip-path. That property IS core's arrow geometry - the "
            "reverted stepper's `clip-path: none` is what squared the chevrons.",
        )

    # ----------------------------------------------------------------------------------------
    # 26. FIVE PROVEN DARK-MODE ROOT CAUSES (RC-1 .. RC-5), 2026-08-03
    # ----------------------------------------------------------------------------------------
    def _channels(self, hex_colour):
        """Return the (r, g, b) integer channels of a normalised ``#rrggbb`` colour."""
        return tuple(int(hex_colour[offset:offset + 2], 16) for offset in (1, 3, 5))

    def _dominant_channel(self, hex_colour):
        """Return the index (0=r, 1=g, 2=b) of the colour's strongest channel.

        A hue FINGERPRINT that survives any amount of lightening or darkening, so "danger is still
        red-ish, primary still teal-ish" can be asserted without pinning a hex - which is exactly the
        RC-5 instruction ("lighten, do not hue-shift")."""
        channels = self._channels(hex_colour)
        return channels.index(max(channels))

    def _assert_state_band_lightens_the_panel(self, band, label):
        """A dark-mode hover/selection band must RAISE the panel, perceptibly but not into a slab.

        This encodes the RC-1 root cause as a behaviour rather than a value: core builds both bands
        from `rgba($black, .08)`, a DARKENING overlay, which on an already-dark panel is a ~1.02:1
        no-op - the affordance simply vanishes. Any correct dark arm must therefore be LIGHTER than
        the surface it sits on, and land inside the perceptibility band."""
        self.assertGreater(
            _relative_luminance(band), _relative_luminance(DARK_BODY_BG),
            "The %s band %s is DARKER than the dark panel %s. Core builds it from "
            "`rgba($black, .08)` (bootstrap_overridden.scss:186), an overlay that darkens - a no-op "
            "on an already-dark surface, so the state has no visible affordance at all. A dark arm "
            "has to lighten." % (label, band, DARK_BODY_BG),
        )
        ratio = _contrast_ratio(band, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, DARK_STATE_BAND_MIN_CONTRAST,
            "The %s band %s is only %.2f:1 from the panel %s - below the %.2f:1 floor, so it is not "
            "perceptible as a band. Light mode's own band composites to ~1.19:1 on white."
            % (label, band, ratio, DARK_BODY_BG, DARK_STATE_BAND_MIN_CONTRAST),
        )
        self.assertLessEqual(
            ratio, DARK_STATE_BAND_MAX_CONTRAST,
            "The %s band %s is %.2f:1 from the panel %s - above the %.2f:1 ceiling, i.e. a bright "
            "slab rather than chrome. A hover/selected state marks an item; it does not repaint the "
            "surface, and a forwarded LIGHT band lands here."
            % (label, band, ratio, DARK_BODY_BG, DARK_STATE_BAND_MAX_CONTRAST),
        )

    def test_dark_dropdown_item_hover_and_selected_states_are_readable_not_black(self):
        """RC-1. A hovered or selected dropdown item must render readable text on a visible band.

        THE DEFECT, ROOT-CAUSED BY LIVE CONFIRM-BY-TOGGLE (2026-08-03). Core re-declares the four
        Bootstrap dropdown-link scalars in bootstrap_overridden.scss:184-189 and only the first is
        semantic - `$dropdown-link-color: $o-main-text-color`, which dark_palette.scss already
        re-points. The other three are LITERALS off the black ramp (`$black`, `rgba($black, .08)`,
        `$black`) that no surface or text override can reach, so they recompiled unchanged into
        web.assets_web_dark. Bootstrap emits two of them as the runtime `--dropdown-link-hover-color`
        / `--dropdown-link-active-color` on `.dropdown-menu` (lib/bootstrap/scss/_dropdown.scss:37-40;
        $prefix is '' in Odoo), from where SEVEN surfaces read them: `.dropdown-item:hover` / `.active`
        (_dropdown.scss:191/198), utils.scss:284-285, core/dropdown/dropdown.scss:88,
        webclient/webclient.scss:76, model_field_selector_popover.scss:11 and
        html_editor.common.scss:533/538.

        Both halves are asserted, because they fail differently: the TOKEN half catches a re-point
        that never happened, and the end-to-end half catches a re-point that happened but is
        outranked on the element that actually paints.

        THE BAND IS ASSERTED AS A DIRECTION, NOT A VALUE (see
        :meth:`_assert_state_band_lightens_the_panel`): core's band DARKENS, which is invisible on a
        dark panel, so "must lighten" is the behaviour under guard.

        WOULD FAIL IF REVERTED: dropping the $dropdown-link-hover-color / -active-color re-points
        returns #000000 (1.20:1 on the panel); dropping the hover-bg re-point returns the darkening
        overlay and the direction assertion fails."""
        dark = self._compiled_css(DARK_BUNDLE)
        light = self._css()
        menu = {
            "classes": DROPDOWN_MENU_CLASSES, "ancestors": DROPDOWN_MENU_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        for prop, core_value, state in (
            ("--dropdown-link-hover-color", CORE_DROPDOWN_LINK_HOVER_COLOR, "hovered"),
            ("--dropdown-link-active-color", CORE_DROPDOWN_LINK_ACTIVE_COLOR, "selected"),
        ):
            raw = _winning_declaration(dark, menu, (prop,))
            self.assertIsNotNone(
                raw,
                "No compiled declaration of %s applies to `.dropdown-menu` in the dark bundle. "
                "Bootstrap emits it from _dropdown.scss:37-40, so either the bundle did not build or "
                "core moved the token - re-ground this guard rather than deleting it." % prop,
            )
            colour = _normalize_colour(raw)
            self.assertIsNotNone(
                colour, "%s resolves to %r, which carries no colour." % (prop, raw),
            )
            self.assertNotEqual(
                colour, core_value,
                "%s still compiles core's %s in the DARK bundle. That is the RC-1 root cause: the "
                "scalar is a literal in bootstrap_overridden.scss, so a %s dropdown item renders "
                "black text on the #111B1E panel - 1.20:1, measured live on the m2o autocomplete."
                % (prop, core_value, state),
            )
            ratio = _contrast_ratio(colour, DARK_BODY_BG)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "%s compiles %s, which is %.2f:1 on the dark panel %s - below the WCAG AA "
                "normal-text threshold of %.1f:1."
                % (prop, colour, ratio, DARK_BODY_BG, WCAG_AA_NORMAL_TEXT),
            )

        band_raw = _winning_declaration(dark, menu, ("--dropdown-link-hover-bg",))
        self.assertIsNotNone(
            band_raw,
            "No compiled declaration of --dropdown-link-hover-bg applies to `.dropdown-menu` in the "
            "dark bundle (Bootstrap emits it at _dropdown.scss:38).",
        )
        band = _normalize_colour(band_raw)
        self.assertIsNotNone(
            band, "--dropdown-link-hover-bg resolves to %r, which carries no colour." % band_raw,
        )
        self._assert_state_band_lightens_the_panel(band, "dropdown-item hover")

        # End-to-end: the element that actually paints, resolved through the real var() chain.
        item = {
            "classes": DROPDOWN_ITEM_CLASSES, "ancestors": DROPDOWN_ITEM_ANCESTORS,
            "states": frozenset({"hover"}), "prev_sibling": frozenset(),
        }
        chain = [item, menu]
        foreground = self._resolve_colour(dark, chain, ("color",), "hovered .dropdown-item [dark]")
        background = self._resolve_colour(
            dark, chain, BACKGROUND_PROPS, "hovered .dropdown-item [dark]",
        )
        ratio = _contrast_ratio(foreground, background)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "A hovered .dropdown-item renders %s on %s in the dark bundle - %.2f:1, below the WCAG "
            "AA normal-text threshold of %.1f:1. The tokens above may be correct while a rule on the "
            "item itself still wins." % (foreground, background, ratio, WCAG_AA_NORMAL_TEXT),
        )

        # LIGHT + PRINT UNTOUCHED. The fix is contributed to web.assets_web_dark only, so core's own
        # near-black-on-white pair must still compile in web.assets_backend.
        light_hover = _normalize_colour(
            _winning_declaration(light, menu, ("--dropdown-link-hover-color",)) or "",
        )
        self.assertEqual(
            light_hover, CORE_DROPDOWN_LINK_HOVER_COLOR,
            "--dropdown-link-hover-color compiles %s in the LIGHT bundle instead of core's %s. The "
            "dark arm leaked out of web.assets_web_dark - black on a white dropdown is correct and "
            "must not move." % (light_hover, CORE_DROPDOWN_LINK_HOVER_COLOR),
        )

    def test_dark_autocomplete_active_row_does_not_compile_to_black(self):
        """RC-1, compile-time half. The highlighted m2o/m2m suggestion must not compile to black.

        WHY THIS NEEDS ITS OWN GUARD, SEPARATE FROM THE TOKEN ONE ABOVE. The autocomplete is the
        surface the owner reported, and it is the one surface a runtime custom-property re-point can
        never reach: autocomplete.scss:23-27 reads the pair as raw COMPILE-TIME Sass
        (`color: $dropdown-link-hover-color; background-color: $dropdown-link-hover-bg`) inside
        `.o-autocomplete .ui-menu-item > a.ui-state-active`. So a fix that only set
        `--dropdown-link-hover-color` on some element would leave the active row rendering #000000 on
        the #111B1E panel - 1.20:1, i.e. the highlighted row of every many2one/many2many/one2many
        dropdown is invisible - while a token-level test passed. Only re-pointing the Sass SCALAR
        fixes both, and only this rule-level assertion proves it did.

        WOULD FAIL IF REVERTED: with the scalars back at core's values this rule compiles
        `color: #000` over an `rgba(0,0,0,.08)` overlay - 1.00:1 between the two."""
        dark = self._compiled_css(DARK_BUNDLE)
        light = self._css()

        raw_foreground = _autocomplete_active_row_declaration(dark, ("color",))
        raw_background = _autocomplete_active_row_declaration(dark, BACKGROUND_PROPS)
        self.assertIsNotNone(
            raw_foreground,
            "No compiled rule paints the colour of `.o-autocomplete .ui-menu-item > a.ui-state-active` "
            "in the dark bundle. Core declares it at autocomplete.scss:25 - re-ground this guard on "
            "the new structure rather than deleting it.",
        )
        self.assertIsNotNone(
            raw_background,
            "No compiled rule paints the background of the autocomplete active row in the dark "
            "bundle (core declares it at autocomplete.scss:26).",
        )
        foreground = _normalize_colour(raw_foreground)
        background = _normalize_colour(raw_background)
        self.assertNotEqual(
            foreground, BLACK,
            "The autocomplete active row compiles `color: %s` in the DARK bundle. That is core's "
            "$dropdown-link-hover-color ($black, bootstrap_overridden.scss:185) read as compile-time "
            "Sass, and it measured 1.20:1 on the #111B1E panel - the highlighted suggestion of every "
            "m2o/m2m/o2m dropdown is invisible." % foreground,
        )
        self._assert_state_band_lightens_the_panel(background, "autocomplete active row")
        ratio = _contrast_ratio(foreground, background)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The autocomplete active row renders %s on %s - %.2f:1, below the WCAG AA normal-text "
            "threshold of %.1f:1." % (foreground, background, ratio, WCAG_AA_NORMAL_TEXT),
        )

        light_foreground = _normalize_colour(
            _autocomplete_active_row_declaration(light, ("color",)) or "",
        )
        self.assertEqual(
            light_foreground, BLACK,
            "The autocomplete active row compiles %s in the LIGHT bundle instead of core's black. "
            "The dark arm leaked out of web.assets_web_dark." % light_foreground,
        )

    def test_dark_list_group_action_and_active_tiers_clear_aa(self):
        """RC-2. A hovered or selected list-group row must be readable on a DARK band in dark mode.

        THE DEFECT, MEASURED. bootstrap_overridden.scss:199-203 keys the whole list-group interactive
        tier off values that cannot cross the scheme boundary:
        `$list-group-action-hover-color: $gray-900` (#212529) and
        `$list-group-active-color/-bg` = `$o-black` on `lighten(saturate(adjust-hue($o-info, 15), 1.8),
        50)` - a LIGHT pale-blue band. Live-measured on the systray Activity/Messaging menu: the row
        under a stationary pointer rendered #212529 = 1.14:1, and `.active` rendered black on a light
        band floating in the dark panel.

        The ACTIVE band is asserted as a DIRECTION plus a ceiling rather than a hex, for the same
        reason as RC-1: light mode's own selected band sits only ~1.11:1 from its white page - the
        HUE, the bold weight and the marker carry "selected", never brightness - so the dark arm is
        held to the same order of magnitude and a forwarded light slab (13:1 on the panel) fails.

        WOULD FAIL IF REVERTED: without the $list-group-action-hover-color re-point the hovered row
        returns #212529 (1.14:1); without the $o-list-group-active-bg re-point the selected band
        returns the pale blue and the ceiling assertion fails."""
        dark = self._compiled_css(DARK_BUNDLE)
        group = {
            "classes": LIST_GROUP_CLASSES, "ancestors": LIST_GROUP_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        hovered = {
            "classes": LIST_GROUP_ITEM_ACTION_CLASSES, "ancestors": LIST_GROUP_ITEM_ANCESTORS,
            "states": frozenset({"hover"}), "prev_sibling": frozenset(),
        }
        selected = {
            "classes": LIST_GROUP_ITEM_ACTIVE_CLASSES, "ancestors": LIST_GROUP_ITEM_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        hover_fg = self._resolve_colour(
            dark, [hovered, group], ("color",), "hovered .list-group-item-action [dark]",
        )
        self.assertNotEqual(
            hover_fg, CORE_LIST_GROUP_ACTION_HOVER_COLOR,
            "The hovered list-group row still compiles core's $gray-900 %s in the DARK bundle "
            "($list-group-action-hover-color, bootstrap_overridden.scss:203) - 1.14:1 on the panel, "
            "which is what the systray Activity/Messaging row under a stationary pointer rendered."
            % CORE_LIST_GROUP_ACTION_HOVER_COLOR,
        )
        hover_bg = self._resolve_colour(
            dark, [hovered, group], BACKGROUND_PROPS, "hovered .list-group-item-action [dark]",
        )
        self._assert_state_band_lightens_the_panel(hover_bg, "list-group action hover")
        ratio = _contrast_ratio(hover_fg, hover_bg)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "A hovered list-group row renders %s on %s - %.2f:1, below the WCAG AA normal-text "
            "threshold of %.1f:1." % (hover_fg, hover_bg, ratio, WCAG_AA_NORMAL_TEXT),
        )

        active_fg = self._resolve_colour(
            dark, [selected, group], ("color",), "selected .list-group-item [dark]",
        )
        active_bg = self._resolve_colour(
            dark, [selected, group], BACKGROUND_PROPS, "selected .list-group-item [dark]",
        )
        self.assertNotEqual(
            active_fg, BLACK,
            "The selected list-group row still compiles core's $o-black in the DARK bundle "
            "($o-list-group-active-color, primary_variables.scss:199).",
        )
        self._assert_state_band_lightens_the_panel(active_bg, "list-group selected")
        ratio = _contrast_ratio(active_fg, active_bg)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "A selected list-group row renders %s on %s - %.2f:1, below the WCAG AA normal-text "
            "threshold of %.1f:1." % (active_fg, active_bg, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_grayscale_bg_utilities_flip_to_dark_surfaces(self):
        """RC-3. `.bg-100` / `.bg-200` / `.bg-300` must be DARK surfaces in the dark bundle.

        THE DEFECT, MEASURED. `.text-900` was closed earlier, but it is one cell of a grid core
        generates mechanically: `@each $-name, $-color in map-merge($-o-bg-colors-custom, $o-grays) {
        .bg-#{$-name}, .text-bg-#{$-name} { @include o-print-color($-color, background-color,
        bg-opacity) } }` (bootstrap_review_backend.scss:240-243) off the FIXED $o-grays ramp. The three
        light rungs therefore recompiled unchanged into web.assets_web_dark. The surface that exposed
        it is the COMMAND-PALETTE FOOTER strip (`.bg-100`), where the dark muted-text tier #8EA5A8 sat
        on #F8F9FA at 2.46:1.

        WHAT IS ASSERTED IS THE PAIR, NOT THE HEX. Both text tiers that legitimately sit on these
        surfaces - the body tier and the MUTED tier - must clear AA on whatever the surface resolves
        to. That is what makes the guard about readability rather than about a chosen value, and it is
        why the muted tier is checked: it is the stricter of the two and the one the footer failed on.

        BLAST RADIUS IS DELIBERATE AND ENUMERATED. The class-wide re-point is safe because the
        `text-bg-*` pairs are a DIFFERENT class name and keep their own color-contrast() label - held
        by test_black_on_light_pill_exceptions_stay_black_on_light_in_the_dark_bundle. The full
        enumeration lives in dark_secondary_surfaces.dark.scss.

        WOULD FAIL IF REVERTED: each class returns its core grayscale rung and the muted tier lands at
        2.46:1 / 2.61:1 / 2.79:1."""
        dark = self._compiled_css(DARK_BUNDLE)
        light = self._css()
        surfaces = (
            ("bg-100", CORE_LIGHT_BG_100, "the command-palette footer strip"),
            ("bg-200", CORE_LIGHT_BG_200, "a light band under dark body text"),
            ("bg-300", CORE_LIGHT_BG_300, "core's selection/toggle band and the .vr divider"),
        )
        for utility, core_light, where in surfaces:
            element = {
                "classes": frozenset({utility}), "ancestors": UTILITY_ANCESTORS,
                "prev_sibling": frozenset(),
            }
            surface = self._resolve_colour(
                dark, [element], BACKGROUND_PROPS, ".%s [dark]" % utility,
            )
            self.assertNotEqual(
                surface, core_light,
                ".%s still compiles core's grayscale rung %s in the DARK bundle - %s. The $o-grays "
                "ramp is a compile-time literal that no $body-*-bg override reaches."
                % (utility, core_light, where),
            )
            for tier, tier_name in (
                (DARK_MUTED_TIER, "muted-text tier ($body-secondary-color)"),
                (DARK_READABLE_TEXT, "body-text tier ($body-color)"),
            ):
                ratio = _contrast_ratio(tier, surface)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "The dark %s %s renders %.2f:1 on the .%s surface %s - below the WCAG AA "
                    "normal-text threshold of %.1f:1. Both tiers legitimately sit on these "
                    "surfaces, and the muted one is what the command-palette footer failed on."
                    % (tier_name, tier, ratio, utility, surface, WCAG_AA_NORMAL_TEXT),
                )
            light_surface = self._resolve_colour(
                light, [element], BACKGROUND_PROPS, ".%s [light]" % utility,
            )
            self.assertEqual(
                light_surface, core_light,
                ".%s compiles %s in the LIGHT bundle instead of core's %s. The dark arm leaked out "
                "of web.assets_web_dark - these are correct light-mode surfaces."
                % (utility, light_surface, core_light),
            )

    def test_dark_near_black_text_and_light_surface_utilities_flip_in_dark(self):
        """RC-4. `.text-dark` / `.text-black` / `.bg-white` / `.bg-light` must flip in dark mode.

        THE DEFECT, MEASURED. Same generated grid and same root cause as RC-3, on the Bootstrap
        black/white and `light`/`dark` theme names (bootstrap_review_backend.scss:113-115 and
        :148-172): `.text-dark` bakes $o-gray-900 #212529 = 1.14:1 on the panel, `.text-black` bakes
        #000000 = 1.16:1, and `.bg-white` / `.bg-light` stay light islands on a dark canvas.

        AND A THIRD, SEPARATE LEVER - which is where RC-4 was actually reported.
        bootstrap_review_backend.scss:122-129 wraps every `.btn-link.text-*` in
        `o-btn-link-variant($o-gray-600 !important, o-text-color($-name) or $-color !important)`, and
        that mixin emits a DIRECT `color:` (utils.scss:184-201 -> o-hover-text-color), not a custom
        property, at specificity (0,2,0) with `!important`. So it outranks `.text-dark`'s (0,1,0)
        `color: var(--color) !important` no matter what `--color` holds: the mail-activity
        "Reschedule" toggler in the crm.lead list (x9 on one screen) measured $o-gray-600 #6C757D =
        3.73:1 at rest and would render #212529 = 1.14:1 on hover. A fix that only re-points the
        utility leaves this surface broken, which is why the resting AND hovered arms are asserted
        separately here.

        Core's DESIGN is preserved rather than flattened: `.btn-link.text-*` is muted at rest and
        contextual on hover, so the guard requires the two states to DIFFER as well as to clear AA.

        WOULD FAIL IF REVERTED: the utilities return their core literals; the btn-link arms return
        #6C757D (3.73:1) and #212529 (1.14:1), and the hover arm equals the light-mode value."""
        dark = self._compiled_css(DARK_BUNDLE)
        light = self._css()

        for utility, core_light in (
            ("text-dark", CORE_LIGHT_TEXT_DARK),
            ("text-black", CORE_LIGHT_TEXT_BLACK),
        ):
            element = {
                "classes": frozenset({utility}), "ancestors": UTILITY_ANCESTORS,
                "prev_sibling": frozenset(),
            }
            colour = self._resolve_colour(dark, [element], ("color",), ".%s [dark]" % utility)
            self.assertNotEqual(
                colour, core_light,
                ".%s still compiles core's near-black %s in the DARK bundle - 1.1:1 on the #111B1E "
                "panel, i.e. invisible. It is a compile-time literal off the grayscale ramp, exactly "
                "like the .text-900 utility already closed above." % (utility, core_light),
            )
            ratio = _contrast_ratio(colour, DARK_BODY_BG)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                ".%s compiles %s = %.2f:1 on the dark panel %s - below the WCAG AA normal-text "
                "threshold of %.1f:1."
                % (utility, colour, ratio, DARK_BODY_BG, WCAG_AA_NORMAL_TEXT),
            )
            light_colour = self._resolve_colour(
                light, [element], ("color",), ".%s [light]" % utility,
            )
            self.assertEqual(
                light_colour, core_light,
                ".%s compiles %s in the LIGHT bundle instead of core's %s - the dark arm leaked out "
                "of web.assets_web_dark." % (utility, light_colour, core_light),
            )

        for utility, core_light in (("bg-white", WHITE), ("bg-light", CORE_LIGHT_BG_100)):
            element = {
                "classes": frozenset({utility}), "ancestors": UTILITY_ANCESTORS,
                "prev_sibling": frozenset(),
            }
            surface = self._resolve_colour(
                dark, [element], BACKGROUND_PROPS, ".%s [dark]" % utility,
            )
            self.assertNotEqual(
                surface, core_light,
                ".%s still compiles %s in the DARK bundle - a light island on the dark canvas, and "
                "the surface every `%s` element's inherited dark body text sits unreadably on."
                % (utility, core_light, utility),
            )
            for tier, tier_name in (
                (DARK_MUTED_TIER, "muted-text tier"), (DARK_READABLE_TEXT, "body-text tier"),
            ):
                ratio = _contrast_ratio(tier, surface)
                self.assertGreaterEqual(
                    ratio, WCAG_AA_NORMAL_TEXT,
                    "The dark %s %s renders %.2f:1 on the .%s surface %s - below the WCAG AA "
                    "normal-text threshold of %.1f:1."
                    % (tier_name, tier, ratio, utility, surface, WCAG_AA_NORMAL_TEXT),
                )
            light_surface = self._resolve_colour(
                light, [element], BACKGROUND_PROPS, ".%s [light]" % utility,
            )
            self.assertEqual(
                light_surface, core_light,
                ".%s compiles %s in the LIGHT bundle instead of core's %s - the dark arm leaked."
                % (utility, light_surface, core_light),
            )

        resting = {
            "classes": frozenset({"btn", "btn-link", "text-dark"}), "ancestors": UTILITY_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        hovered = dict(resting, states=frozenset({"hover"}))
        rest_colour = self._resolve_colour(
            dark, [resting], ("color",), "resting .btn-link.text-dark [dark]",
        )
        self.assertNotEqual(
            rest_colour, CORE_LIGHT_BTN_LINK_MUTED,
            "A resting `.btn-link.text-dark` still compiles core's $o-gray-600 %s in the DARK bundle "
            "- 3.73:1 on the #111B1E panel, the exact value measured x9 on the crm.lead list "
            "(mail-activity \"Reschedule\"). That colour comes from o-btn-link-variant's DIRECT "
            "`color:` at (0,2,0) !important, so re-pointing the .text-dark utility's --color alone "
            "cannot reach it." % CORE_LIGHT_BTN_LINK_MUTED,
        )
        hover_colour = self._resolve_colour(
            dark, [hovered], ("color",), "hovered .btn-link.text-dark [dark]",
        )
        self.assertNotEqual(
            hover_colour, CORE_LIGHT_TEXT_DARK,
            "A hovered `.btn-link.text-dark` still compiles core's near-black %s in the DARK bundle "
            "(o-btn-link-variant's hover arm, `o-text-color('dark') or $-color !important`) - "
            "1.14:1 on the panel." % CORE_LIGHT_TEXT_DARK,
        )
        for state, colour in (("resting", rest_colour), ("hovered", hover_colour)):
            ratio = _contrast_ratio(colour, DARK_BODY_BG)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "A %s `.btn-link.text-dark` renders %s = %.2f:1 on the dark panel %s - below the "
                "WCAG AA normal-text threshold of %.1f:1."
                % (state, colour, ratio, DARK_BODY_BG, WCAG_AA_NORMAL_TEXT),
            )
        self.assertNotEqual(
            rest_colour, hover_colour,
            "The resting and hovered `.btn-link.text-dark` both compile %s. Core's design for this "
            "control is muted at rest and contextual on hover; collapsing the two states to one "
            "value clears AA but deletes the hover affordance." % rest_colour,
        )

    def test_dark_accent_foregrounds_clear_aa_without_shifting_hue(self):
        """RC-5. The outline-CTA label and the contextual TEXT tiers need a dark arm that stays on hue.

        THE DEFECT, MEASURED. Two accent FOREGROUNDS tuned for a white page recompiled into dark:
          (a) `.btn-outline-primary` - core ships NO "primary" key in $o-btns-bs-outline-override, so
              the class falls through to `button-outline-variant($theme-colors["primary"])`
              (bootstrap_review_backend.scss:64-76) and the mixin sets `--btn-color: $color` verbatim.
              With $theme-colors["primary"] correctly pinned to the AA teal #007F8E (4.74:1 on WHITE)
              the LABEL measured 3.69:1 on the #111B1E panel - the "New" button of every form view
              (form_controller.xml:9) and the kanban "Load more..." control.
          (b) $o-theme-text-colors (primary_variables.scss:92-97) is core's OWN WCAG-tuning seam for
              `.text-{success,info,warning,danger}` - four values chosen to pass AA on white. All four
              sit at 3.71-3.85:1 on the dark panel; `.text-danger` (the cog-menu "Delete") measured
              3.76:1. The same map also feeds the INVALID-STATE indicators through `o-text-color()`
              (notebook.scss:62, fields.scss:70, time_picker.scss:8), which is why it matters beyond
              the utility class.

        SEMANTIC IDENTITY IS ASSERTED AS A HUE FINGERPRINT, not as a hex: the dominant RGB channel of
        core's light value must still be dominant in the dark arm. That survives any amount of
        lightening and fails immediately on a hue shift - "lighten, do not hue-shift", checkable.

        WOULD FAIL IF REVERTED: the outline label returns #007F8E (3.69:1) and each contextual tier
        returns its core light value (~3.7:1)."""
        dark = self._compiled_css(DARK_BUNDLE)
        light = self._css()

        button = {
            "classes": FORM_NEW_BUTTON_CLASSES, "ancestors": FORM_NEW_BUTTON_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        label = self._resolve_colour(
            dark, [button], ("color",), ".btn-outline-primary label [dark]",
        )
        self.assertNotEqual(
            label, CHROME_BASE,
            "The `.btn-outline-primary` label still compiles the LIGHT-mode AA teal %s in the DARK "
            "bundle - 3.69:1 on the #111B1E panel. #007F8E is 4.74:1 on WHITE; it is a light-mode "
            "token and cannot cross the scheme boundary unchanged. That button is \"New\" on every "
            "form view." % CHROME_BASE,
        )
        ratio = _contrast_ratio(label, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "The `.btn-outline-primary` label compiles %s = %.2f:1 on the dark panel %s - below the "
            "WCAG AA normal-text threshold of %.1f:1."
            % (label, ratio, DARK_BODY_BG, WCAG_AA_NORMAL_TEXT),
        )
        self.assertEqual(
            self._dominant_channel(label), self._dominant_channel(CHROME_BASE),
            "The `.btn-outline-primary` label compiles %s, whose dominant RGB channel differs from "
            "the chrome teal %s. The dark arm must LIGHTEN the teal, not hue-shift it - a primary "
            "CTA that stops reading as the brand colour is a different bug."
            % (label, CHROME_BASE),
        )
        # The ring is read from `--btn-border-color`, not from `border-color`: Bootstrap paints it with
        # the SHORTHAND `border: var(--btn-border-width) solid var(--btn-border-color)`, a multi-value
        # declaration no single-var resolver can unwrap. The custom property is also the exact thing
        # the map sets, so this reads the token the fix owns.
        raw_border = _winning_declaration(dark, button, ("--btn-border-color",))
        self.assertIsNotNone(
            raw_border,
            "No compiled declaration of --btn-border-color applies to `.btn-outline-primary` in the "
            "dark bundle. Bootstrap's button mixins always emit it, so either the bundle did not "
            "build or core changed the token - re-ground this guard rather than deleting it.",
        )
        border = _normalize_colour(raw_border)
        self.assertIsNotNone(
            border, "--btn-border-color resolves to %r, which carries no colour." % raw_border,
        )
        ratio = _contrast_ratio(border, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_NON_TEXT_MIN,
            "The `.btn-outline-primary` ring compiles %s = %.2f:1 on the dark panel %s - below WCAG "
            "SC 1.4.11's %.1f:1 minimum for a non-text UI component. An outline button IS its "
            "outline." % (border, ratio, DARK_BODY_BG, WCAG_NON_TEXT_MIN),
        )
        light_label = self._resolve_colour(
            light, [button], ("color",), ".btn-outline-primary label [light]",
        )
        self.assertEqual(
            light_label, CHROME_BASE,
            "The `.btn-outline-primary` label compiles %s in the LIGHT bundle instead of the AA teal "
            "%s. The dark arm leaked out of web.assets_web_dark, or the new outline-map key was "
            "added somewhere both bundles read." % (light_label, CHROME_BASE),
        )

        for name, core_light in sorted(CORE_LIGHT_THEME_TEXT_COLORS.items()):
            element = {
                "classes": frozenset({"text-%s" % name}), "ancestors": UTILITY_ANCESTORS,
                "prev_sibling": frozenset(),
            }
            colour = self._resolve_colour(dark, [element], ("color",), ".text-%s [dark]" % name)
            self.assertNotEqual(
                colour, core_light,
                ".text-%s still compiles core's light-tuned %s in the DARK bundle. "
                "$o-theme-text-colors is core's WCAG seam FOR A WHITE PAGE - every value in it is "
                "~3.7:1 on the #111B1E panel, and the same map feeds the invalid-field and "
                "invalid-notebook-tab indicators through o-text-color()." % (name, core_light),
            )
            ratio = _contrast_ratio(colour, DARK_BODY_BG)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                ".text-%s compiles %s = %.2f:1 on the dark panel %s - below the WCAG AA normal-text "
                "threshold of %.1f:1."
                % (name, colour, ratio, DARK_BODY_BG, WCAG_AA_NORMAL_TEXT),
            )
            self.assertEqual(
                self._dominant_channel(colour), self._dominant_channel(core_light),
                ".text-%s compiles %s, whose dominant RGB channel differs from core's %s. The dark "
                "arm must LIGHTEN each semantic colour, never hue-shift it - danger has to keep "
                "reading as red, success as green." % (name, colour, core_light),
            )
            light_colour = self._resolve_colour(
                light, [element], ("color",), ".text-%s [light]" % name,
            )
            self.assertEqual(
                light_colour, core_light,
                ".text-%s compiles %s in the LIGHT bundle instead of core's %s - the dark arm "
                "leaked out of web.assets_web_dark." % (name, light_colour, core_light),
            )

    def test_black_on_light_pill_exceptions_stay_black_on_light_in_the_dark_bundle(self):
        """The black-on-light colour PILLS must keep their own pair - even in the dark bundle.

        WHY THIS GUARD EXISTS. RC-3 and RC-4 re-point four background utilities and two text
        utilities CLASS-WIDE. That is the right altitude for those families, but the same repo has
        already been burned once by a class-wide re-point (the WHITE burger panel), and the failure
        mode here is specific and easy to reach: a future "let's be thorough" pass that also darkens
        `text-bg-*`, `.o_badge_color_N`, `.o_tag_color_N` or the calendar chips would leave their
        deliberately DARK label on a now-dark chip. Those pills are CORRECT as shipped - they carry
        their own bg+text pair and measured 9.8:1 - so this test pins the pair rather than the value:
        a light chip with a darker label clearing AA. It fails the moment any of them is dragged into
        a dark re-point.

        The three shapes cover the three DIFFERENT mechanisms core uses, so no one of them stands in
        for the others: `.o_tag.o_tag_color_N` goes through o-print-color on BOTH axes
        (tags_list.scss:6-13, i.e. the same `--background-color` / `--color` properties RC-3/RC-4
        re-point - the closest call of the three), `.badge.o_badge_color_N` uses direct `!important`
        declarations (badge.scss:3-6), and `.text-bg-300` is core's own color-contrast() pairing
        (bootstrap_review_backend.scss:245-247).

        THIS IS A NON-REGRESSION GUARD, NOT A RED-BEFORE-GREEN ONE, and deliberately so: it was green
        before RC-3/RC-4 and must stay green after. It is capable of failing and fails the moment a
        re-point is widened to any of these selectors."""
        dark = self._compiled_css(DARK_BUNDLE)
        pills = (
            ("`.o_tag.o_tag_color_1` (o-print-color on both axes)", TAG_PILL_CLASSES),
            ("`.badge.o_badge_color_1` (direct !important declarations)", BADGE_PILL_CLASSES),
            ("`.text-bg-300` (core's own color-contrast pairing)", TEXT_BG_300_CLASSES),
        )
        for label, classes in pills:
            element = {
                "classes": classes, "ancestors": UTILITY_ANCESTORS, "prev_sibling": frozenset(),
            }
            pill = self._resolve_colour(dark, [element], BACKGROUND_PROPS, "%s [dark]" % label)
            text = self._resolve_colour(dark, [element], ("color",), "%s [dark]" % label)
            self.assertGreaterEqual(
                _contrast_ratio(pill, DARK_BODY_BG), WCAG_NON_TEXT_MIN,
                "%s compiles the chip %s, only %.2f:1 from the dark panel %s - it has been dragged "
                "into a dark re-point. These pills are deliberately LIGHT chips with a dark label "
                "and are correct as shipped; darkening the chip without darkening its label is the "
                "regression this guard exists for."
                % (label, pill, _contrast_ratio(pill, DARK_BODY_BG), DARK_BODY_BG),
            )
            self.assertLess(
                _relative_luminance(text), _relative_luminance(pill),
                "%s compiles the label %s LIGHTER than its chip %s. The pill pairs a dark label with "
                "a light chip in both schemes." % (label, text, pill),
            )
            ratio = _contrast_ratio(text, pill)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "%s renders its label %s on the chip %s at %.2f:1 - below the WCAG AA normal-text "
                "threshold of %.1f:1." % (label, text, pill, ratio, WCAG_AA_NORMAL_TEXT),
            )
