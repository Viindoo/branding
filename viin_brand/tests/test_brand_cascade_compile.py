# Compiled-cascade guard for the CHROME tier of the brand: navbar entry states, search facets,
# statusbar, settings tab, stat values and the progress-bar trough. Sibling of
# test_brand_color_compile.py, which guards the brand-identity tier (navbar surface, --primary,
# .btn-primary, --link-color).
#
# Every assertion resolves the value a real element computes from the COMPILED bundle, through a
# small cascade resolver (_computed_value): `!important` first, then specificity, then source order,
# with var() resolving through inherited custom properties. A source-substring check would stay green
# after core renames a variable, moves a surface to another token or wraps the consumer in a rule the
# module does not win, and "#007F8E appears in the bundle" says nothing about which declaration
# paints an element.
#
# Colour ladder under test (declared once in static/src/scss/brand_variables.scss):
#   $o-brand-primary / $o-brand-odoo  #00BBCE  decorative identity teal, 2.33:1 - never under white
#                                              text, never on interactive chrome
#   $o-viin-chrome-base               #007F8E  4.74:1 - base chrome, carries white text
#   $o-viin-chrome-deep               #005E68  7.50:1 - hover / focus / pressed / open rung
#   $o-brand-secondary                #7F4282  6.99:1 on the form sheet - stat values
#
# Two deliberate exceptions: the favourite search facet keeps core's yellow, and the stat value is
# purple, not teal.
import os
import re

from odoo.tests.common import TransactionCase, tagged

try:
    # Imported defensively: a missing constant fails the tests that need it, not the collection of
    # the whole tests package.
    from ..controllers.webmanifest import VIINDOO_THEME_COLOR
except ImportError:
    VIINDOO_THEME_COLOR = None

# Owned by the sibling test files and reused rather than re-declared.
from .test_brand_color_compile import (
    ODOO_COMMUNITY_PURPLE,
    ODOO_ENTERPRISE_AUBERGINE,
    VIINDOO_NAVBAR_BACKGROUND_COLOR,
)
from .test_brand_ssot import BRAND_VARIABLES_SCSS, _resolve_scss_hex

BACKEND_BUNDLE = "web.assets_backend"
DARK_PALETTE_SCSS = os.path.join(os.path.dirname(BRAND_VARIABLES_SCSS), "dark_palette.scss")


def dark_palette_var(var_name):
    """Return the hex ``var_name`` resolves to in dark_palette.scss.

    :param var_name: Sass variable declared in dark_palette.scss
    :return: the lower-cased hex colour
    :raises AssertionError: when the variable is not declared there
    """
    with open(DARK_PALETTE_SCSS, encoding="utf-8") as scss_file:
        value = _resolve_scss_hex(scss_file.read(), var_name)
    if value is None:
        raise AssertionError(
            "%s must be declared in %s - callers read their expected dark colour from this SSOT "
            "rather than re-literalising it." % (var_name, os.path.basename(DARK_PALETTE_SCSS))
        )
    return value.lower()


# Fixed design constants asserted as literals; deriving them by re-computing a Sass darken()/mix()
# here would compare production logic against itself.
CHROME_BASE = VIINDOO_NAVBAR_BACKGROUND_COLOR            # #007f8e
CHROME_DEEP = "#005e68"                                  # pressed / open / hover rung
WHITE = "#ffffff"
BLACK = "#000000"
# Core's progress-bar trough is $o-view-background-color, i.e. plain white.
CORE_PROGRESS_TROUGH = WHITE
# Core's $o-enterprise-color default: the content swatch brand_palette_reset.scss keeps aubergine
# while the chrome uses of the same variable are teal.
CORE_CONTENT_O_COLOR_1 = ODOO_ENTERPRISE_AUBERGINE

# WCAG 2.1 SC 1.4.3 minimum contrast for normal-size text.
WCAG_AA_NORMAL_TEXT = 4.5

# web.assets_web_dark includes web.assets_web (so every backend surface recompiles) plus the
# `*.dark.scss` glob. The dark surfaces are fixed palette constants of dark_palette.scss, asserted
# as the surface a token renders on rather than resolved from the bundle, so a dark-on-white
# result cannot hide behind a panel that is still painted white.
DARK_BUNDLE = "web.assets_web_dark"
DARK_BODY_BG = "#111b1e"   # dark body / form-sheet / panel tier
DARK_APP_BG = "#0b1315"    # dark webclient background band behind panels
DARK_RAISED = "#152225"    # dark raised tier (list/kanban/settings headers)
# Dark arm of the interactive link (#007F8E in light). Quoted for the failure message only; the
# assertion is the measured WCAG contrast against the dark surface.
DARK_LINK_REF = "#4fd4e2"

# The brand purple is a light-mode accent: the dark bundle carries no purple, every purple surface
# falls back to its default look. brand_variables.scss compiles our purple rules under
# `@if not $o-viin-dark-bundle` and also re-points $o-brand-secondary in dark, because core reads
# that token directly in `.o_xxs_form_view .o_form_label` (2.50:1 on the dark panel) and in the
# search-panel section header border, where no guard of ours reaches.
DARK_BUNDLE_FORBIDDEN_PURPLE = "#b589b8"   # a dark-tuned brand purple - must NOT appear in dark
DARK_MUTED_TIER = "#8ea5a8"       # $body-secondary-color: 6.75:1 on #111B1E, and NOT purple

# Secondary solid surfaces core paints from the gray ramp (`$o-gray-100/200`, the `.bg-N`
# utilities) or from a Bootstrap table variant, as the dark hex each must resolve to.
DARK_KANBAN_CANVAS = "#0b1315"        # kanban renderer/group/header canvas -> app-grey
DARK_SETTINGS_SIDEBAR = "#152225"     # settings tab sidebar (--settings__tab-bg) -> gray rung 100
DARK_SETTINGS_HEADER = "#1d2d31"      # settings section-header strip (--settings__title-bg) -> gray rung 200
DARK_FACET_BAND = "#1d2d31"           # search-facet .bg-200 resting band -> gray rung 200
DARK_TABLE_INFO_BAND = "#123037"      # selected .table-info row (--bs-table-bg) -> dark info tint
# The light values Bootstrap's `.table-info` paints a selected-row cell with; the cell must resolve
# to neither in dark.
LIGHT_TABLE_INFO_BAND = "#ccebfa"     # core .table-info --bs-table-bg
LIGHT_TABLE_INFO_ACCENT = "#c1deec"   # the light inset box-shadow accent overlay repainting the cell
DARK_READABLE_TEXT = "#edf4f5"        # the dark body text ($body-color) that sits on these surfaces

# Core values each override must move away from, grounded in core's own source rather than the
# production value, so each guard fails on a revert.
#
# `.text-secondary`: Odoo's backend re-declares `$secondary: $gray-300`, so Bootstrap's text utility
# compiles to #DEE2E6 = 1.30:1 on white. The same token paints the surface tier (`.bg-secondary`,
# `.border-secondary`), which must not move: `--secondary-rgb` stays core's rung-300 triplet in each
# bundle, whitespace-stripped for comparison.
CORE_INVISIBLE_TEXT_SECONDARY = "#dee2e6"
CORE_SECONDARY_RGB = "222,226,230"
DARK_SECONDARY_RGB = "37,56,60"

# The neutral button pair core compiles from `$o-btns-bs-override["secondary"]` ($o-gray-300 fill,
# $o-gray-900 label), the light-bundle values; the dark bundle resolves the same keys through the
# dark gray ramp (pager arrows, the chatter Log note / Activity toggles).
CORE_LIGHT_BTN_SECONDARY_BG = "#dee2e6"

# The statusbar current step: core's $o-component-active-bg is `mix($o-action, $o-gray-100, 20%)`, a
# light cyan tint that no $body-*-bg override reaches, so it recompiled unchanged into the dark
# bundle.
CORE_LIGHT_STATUSBAR_ACTIVE_BG = "#c6edf1"
# The stat button: `$o-btns-bs-outline-override["secondary"]` keys off the same gray ramp and is
# expanded through the `button-variant` mixin, so `border` is a literal border colour and
# `hover-background` a literal fill. Every smart button compiles as `btn btn-outline-secondary`.
CORE_LIGHT_BTN_OUTLINE_BORDER = "#dee2e6"      # 13.45:1 on the dark panel - the glare
CORE_LIGHT_BTN_OUTLINE_HOVER_BG = "#e9ecef"    # the near-white hover fill the dark label vanishes on

# A hairline separates without glaring: a contrast band rather than a pinned hex. The lower bound
# rejects an invisible border, the upper one the white border. Light mode's own stat-button border
# (#DEE2E6 on white = 1.30:1) anchors the band.
SUBTLE_BORDER_MIN_CONTRAST = 1.15
SUBTLE_BORDER_MAX_CONTRAST = 3.0

# The dark current-step fill is a surface tier, not a light slab: light mode's active fill (#C6EDF1)
# sits only 1.25:1 from the sheet. The ceiling rejects the forwarded light tint (14.0:1 on the dark
# panel) without pinning a design value.
DARK_ACTIVE_FILL_MAX_GLARE = 4.0

# Element models are transcribed from core's own markup. An ancestor pool is the union of the
# classes on the real ancestor chain, read off the COMPILED selector - the full SCSS nesting of the
# rule that paints the surface - not the template alone: SCSS wrappers contribute ancestor classes
# the XML never shows. An unscoped rule (Bootstrap's bare `.btn`) applies, a rule scoped to a context
# the element is not in is excluded. Pools are generous on purpose: a wide pool can only add a
# competitor and fail loudly, a narrow one can hide the override that breaks the surface.

# The pager's previous button, `.btn-secondary` of core web, present on every multi-record view. It
# is the first child of its btn-group, so it has no previous sibling and rejects Bootstrap's
# sibling-gated `.btn-check:checked + .btn` competitors.
PAGER_ANCESTORS = frozenset({
    "o_web_client", "o_action_manager", "o_view_controller", "o_control_panel", "o_cp_pager",
    "o_pager", "d-flex", "gap-2", "h-100", "btn-group", "d-print-none",
})
PAGER_PREVIOUS_CLASSES = frozenset({
    "btn", "btn-secondary", "o_pager_previous", "px-2", "rounded-start",
})

# A bare `.text-secondary` in ordinary view content. The pool carries no view-type class, so a
# view-scoped rule is excluded and the generic utility is measured.
TEXT_SECONDARY_CLASSES = frozenset({"text-secondary"})
TEXT_SECONDARY_ANCESTORS = frozenset({"o_web_client", "o_action_manager", "o_view_controller"})

# The name cell of a grouped-list group row. Both foreground shapes are modelled: `.text-black`
# (Odoo's o-print-color `color: var(--color) !important`) and `.text-body` (Bootstrap's
# `rgba(var(--body-color-rgb), ...) !important`) resolve through different levers, so a rule that
# beats only one is a latent half-fix.
LIST_GROUP_NAME_ANCESTORS = frozenset({
    "o_web_client", "o_action_manager", "o_view_controller", "o_list_view", "o_list_renderer",
    "o_renderer", "table-responsive", "o_list_table", "table", "table-sm", "table-hover",
    "position-relative", "mb-0", "o_list_table_grouped", "o_group_has_content", "o_group_header",
    "o_group_open", "cursor-pointer",
})
_LIST_GROUP_NAME_BASE = frozenset({"o_group_name", "fs-6", "fw-bold"})
LIST_GROUP_NAME_OPEN = _LIST_GROUP_NAME_BASE | {"text-black"}
LIST_GROUP_NAME_FOLDED = _LIST_GROUP_NAME_BASE | {"text-body"}
# The list cell surface: core paints the table from `--table-bg: $o-view-background-color`, which
# dark_palette.scss re-points to the dark panel. The group header declares no screen background.
LIST_SURFACE_LIGHT = WHITE
LIST_SURFACE_DARK = DARK_BODY_BG

# WCAG 2.1 SC 1.4.11 minimum contrast for non-text UI components.
WCAG_NON_TEXT_MIN = 3.0

# Core's dim default for the empty/readonly/false form-label variant (`opacity: 0.66`): the literal
# the dark polish lifts above.
CORE_FADED_LABEL_OPACITY = 0.66

# `$o-gray-900`, the near-black the `.text-900` utility bakes as a compile-time literal
# (`color: var(--color) !important`). dark_palette.scss re-points $body-color but not the $o-gray-*
# scale, so `.text-900` stays #212529 in both bundles. Core wraps every form-label cell in
# `o_wrap_label text-break text-900` and the bare `<label class="o_form_label">` inherits that
# colour: 1.14:1 on the dark sheet. This is the reversion signature the base-tier guards forbid.
LIGHT_BODY_TEXT = "#212529"

# The mobile burger / app-menu sidebar is a light island: core declares the four tokens it is
# painted from as `!default` light literals that no $body-*-bg override reaches, so the panel
# recompiled white in the dark bundle. These are the light values the dark bundle must not resolve.
CORE_BURGER_PANEL_BG = WHITE                # $o-burger-base-bg
CORE_BURGER_ENTRY_TEXT = "#343a40"          # $o-burger-base-color, painted at .8 alpha
CORE_BURGER_TOPBAR_BG = "#f8f9fa"           # $o-burger-topbar-bg
CORE_BURGER_TOPBAR_TEXT = BLACK             # $o-burger-topbar-color
# Core paints the entry text through `rgba($o-burger-base-color, .8)`, so the composite the user
# reads is measured, not the raw text colour.
CORE_BURGER_ENTRY_TEXT_ALPHA = 0.8
# The dark tiers dark_palette.scss maps those tokens onto: the panel is the form-sheet tier, the
# topbar the raised tier.
DARK_BURGER_PANEL = DARK_BODY_BG            # #111b1e
DARK_BURGER_TOPBAR = DARK_RAISED            # #152225

# The search facet label (search_bar.xml, "web.SearchBar.Facets"): a groupBy facet has two shapes
# (`text-bg-action`, plus `btn` when the search model can order by count) and a rule matching only
# one is a latent bug, so both are asserted. The static label classes are carried too: a model
# listing only the classes under test hides competitors keyed on the others and can only
# cause a false PASS.
_FACET_LABEL_BASE = frozenset({
    "o_searchview_facet_label", "position-relative", "rounded-start-2", "px-1", "rounded-end-0",
    "p-0",
})
FACET_LABEL_FIELD = _FACET_LABEL_BASE | {"btn", "btn-primary"}
FACET_LABEL_GROUPBY = _FACET_LABEL_BASE | {"text-bg-action"}
FACET_LABEL_GROUPBY_ORDERABLE = _FACET_LABEL_BASE | {"text-bg-action", "btn"}
FACET_LABEL_FAVORITE = _FACET_LABEL_BASE | {"btn", "btn-favourite"}
FACET_VALUES = frozenset({
    "o_facet_values", "position-relative", "d-flex", "flex-wrap", "align-items-center", "ps-2",
    "rounded-end-2", "text-wrap", "overflow-hidden",
})
# The ":hover overlay" div core renders before the facet label. Bootstrap ships sibling-gated button
# rules whose subject carries no state pseudo-class; without a real sibling to test against they
# would count as competitors for the resting facet paint.
FACET_LABEL_PREV_SIBLING = frozenset({
    "position-absolute", "start-0", "top-0", "bottom-0", "end-0", "bg-view", "border",
    "rounded-2", "shadow", "opacity-0", "opacity-100-hover",
})

# Ancestor pools of the surfaces under test.
# .o_main_navbar > .o_menu_sections > (.o_nav_entry | .dropdown-toggle); the overflow menu renders
# as .o_menu_sections_more inside the same .o_menu_sections.
NAVBAR_ANCESTORS = frozenset({
    "o_web_client", "o_main_navbar", "o_menu_sections", "o_menu_sections_more", "dropdown",
})
# .o_cp_searchview > .o_searchview > .o_searchview_input_container > .o_searchview_facet >
# (.o_searchview_facet_label + .o_facet_values).
SEARCH_FACET_ANCESTORS = frozenset({
    "o_web_client", "o_control_panel", "o_cp_searchview", "o_searchview",
    "o_searchview_input_container", "o_searchview_facet",
})
# .o_field_statusbar > .o_statusbar_status > .o_arrow_button, rendered as
# `btn btn-secondary o_arrow_button`, hence the "secondary" button map feeding it.
STATUSBAR_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_form_statusbar", "o_field_statusbar", "o_statusbar_status",
})
# The two step states. `disabled` on the CURRENT step is load-bearing: core renders it
# `t-att-disabled="props.isDisabled || item.isSelected"` and Bootstrap paints a disabled button
# from --btn-disabled-color, which the `button-variant` mixin defaults to `color-contrast($background)`
# rather than the map's `color` key. That default measured white on the light-cyan active fill
# (1.25:1) in the dark bundle, and a model without the state would resolve the map's `color` and
# miss it. `o_viin_numbered_step` is this cluster's own hook (statusbar_steps.xml).
STATUSBAR_CURRENT_STEP = {
    "classes": frozenset({
        "btn", "btn-secondary", "o_arrow_button", "o_viin_numbered_step",
        "o_arrow_button_current",
    }),
    "states": frozenset({"disabled"}),
    "ancestors": STATUSBAR_ANCESTORS,
    "prev_sibling": frozenset({"btn", "btn-secondary", "o_arrow_button"}),
}
# A clickable step (not current, not disabled), as on crm.lead's stage_id.
STATUSBAR_STEP = {
    "classes": frozenset({"btn", "btn-secondary", "o_arrow_button", "o_viin_numbered_step"}),
    "ancestors": STATUSBAR_ANCESTORS,
    "prev_sibling": frozenset({"btn", "btn-secondary", "o_arrow_button"}),
}
# The same step on a readonly statusbar (sale.order, account.move, purchase.order): every step is
# `disabled` and core swaps the label onto $text-muted, a different token from the clickable state.
STATUSBAR_STEP_DISABLED = dict(STATUSBAR_STEP, states=frozenset({"disabled"}))
# The compiled selector is `.o_base_settings_view .o_form_renderer .o_setting_container
# .settings_tab .selected`; the two wrapper classes are invisible in the settings template.
# `.o_form_view` stays because a sibling block is scoped as `.o_form_view.o_base_settings_view`.
SETTINGS_TAB_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_base_settings_view", "o_form_renderer",
    "o_setting_container", "settings_tab",
})
# `.o-form-buttonbox > .oe_stat_button > .o_stat_info > .o_stat_value` on the desktop form sheet.
# o_bottom_sheet is absent on purpose: that mobile context pins --o-stat-text-color to currentColor
# and must keep winning there.
BUTTONBOX_ANCESTORS = frozenset({"o_web_client", "o_form_view", "o_form_sheet", "o_form_sheet_bg"})
# Core compiles a stat button as
# `oe_stat_button btn btn-outline-secondary flex-grow-1 flex-lg-grow-0`.
STAT_BUTTON_ANCESTORS = BUTTONBOX_ANCESTORS | {
    "o-form-buttonbox", "oe_stat_button", "btn", "btn-outline-secondary", "flex-grow-1",
    "flex-lg-grow-0", "o_stat_info", "o_field_statinfo",
}
# The stat button itself, for the guards that resolve its own outline-map tokens
# (--btn-border-color / --btn-color / --btn-hover-bg / --btn-hover-color).
STAT_BUTTON = {
    "classes": frozenset({
        "oe_stat_button", "btn", "btn-outline-secondary", "flex-grow-1", "flex-lg-grow-0",
    }),
    "ancestors": BUTTONBOX_ANCESTORS | {"o-form-buttonbox"},
    "prev_sibling": frozenset(),
}
# .o_progressbar > .o_progress.
PROGRESSBAR_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_list_view", "o_field_widget", "o_progressbar",
})
# Core nests the mobile form-label colour as
# `.o_form_view.o_xxs_form_view .o_group .o_inner_group .o_form_label { color: $o-brand-secondary }`,
# the same Sass variable as the desktop stat value, so both re-tint together. The pool must hold
# every class the compiled selector demands (o_group AND o_inner_group).
XXS_FORM_LABEL_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_xxs_form_view", "o_group", "o_inner_group",
})
# The desktop label and its faded variant compile to
# `.o_form_view .o_form_label.o_form_label_{empty,false,readonly}`, which demands only .o_form_view.
# The sheet classes are added because a real desktop label always sits inside the sheet.
FORM_LABEL_ANCESTORS = frozenset({
    "o_web_client", "o_form_view", "o_form_sheet_bg", "o_form_sheet",
})
# Core wraps every form-label cell in `o_cell o_wrap_label text-break text-900`. The bare
# `<label class="o_form_label">` is its child with no colour of its own, so `color` inherits from
# the cell and its compile-time #212529. Modelling the cell as the label's styling parent makes the
# dark-on-dark reversion observable. The value cell (`o_wrap_input`) has no text-900, which is why
# field values stay the readable #EDF4F5.
FORM_LABEL_CELL_CLASSES = frozenset({"o_cell", "o_wrap_label", "text-break", "text-900"})
# A kanban column title carries `.text-900` directly, on the dark kanban header canvas: a
# representative non-form-label `.text-900` surface proving the class-wide --color re-point reaches
# beyond form labels.
KANBAN_TITLE_CLASSES = frozenset({
    "o_column_title", "flex-grow-1", "min-w-0", "mw-100", "fw-bold", "text-900",
})
KANBAN_HEADER_ANCESTORS = frozenset({
    "o_web_client", "o_kanban_view", "o_kanban_renderer", "o_kanban_header",
})
# A resting menu entry paints `color: var(--NavBar-entry-color, #{$o-navbar-entry-color})`, which is
# `rgba($o-white, .9)`, on `.o_nav_entry` / `.o_menu_toggle`. The navbar is scheme-invariant teal, so
# this is asserted once: the entry text must render opaque #FFFFFF to clear AA on the teal bar, not
# the .9-alpha composite (#E6F2F4, ~4.15:1).
NAVBAR_ENTRY_CLASSES = frozenset({"o_nav_entry", "o_menu_toggle"})

# `.o_kanban_renderer` declares --Kanban-background (and the derived --KanbanGroup-background) from
# $o-kanban-background, so the renderer is where the token resolves.
KANBAN_RENDERER_ANCESTORS = frozenset({"o_web_client", "o_view_controller", "o_kanban_view"})
# The settings custom properties live on the two-class wrapper `.o_base_settings_view
# .o_form_renderer`.
SETTINGS_RENDERER_ANCESTORS = frozenset({"o_web_client", "o_form_view", "o_base_settings_view"})
# The facet pill carries `o_searchview_facet` and the `bg-200` utility; its ancestors are the
# control-panel search chain.
FACET_PILL_ANCESTORS = frozenset({
    "o_web_client", "o_control_panel", "o_cp_searchview", "o_searchview",
    "o_searchview_input_container",
})
# A selected row is `<tr class="table-info o_data_row">` in the list table; `--bs-table-bg` and
# `--bs-table-color` are declared on it and inherited by its cells.
TABLE_INFO_ROW_ANCESTORS = frozenset({
    "o_web_client", "o_list_view", "o_list_renderer", "o_list_table",
})

# The mobile burger / app-menu panels are portalled to `body`, so neither descends from
# .o_web_client: the pool is the panel root alone, as in core's `.o_burger_menu, .o_app_menu_sidebar`
# block. Both panels compile from the same nested block with identical declarations, so the app-menu
# sidebar stands for both.
BURGER_SIDEBAR_ANCESTORS = frozenset({"o_app_menu_sidebar"})
# The scrolling panel; `o_burger_menu_app` carries the background on both panels, so the user-burger
# is not a second, un-darkened island.
BURGER_PANEL_CLASSES = frozenset({
    "o_burger_menu_content", "o_burger_menu_app", "flex-grow-1", "flex-shrink-1", "overflow-auto",
})
BURGER_TOPBAR_CLASSES = frozenset({
    "o_sidebar_topbar", "d-flex", "align-items-center", "justify-content-between",
    "flex-shrink-0", "py-0", "fs-4",
})
# A top-level section title (`web.SectionMenu`) carries `.text-900` directly, so it computes the
# dark #EDF4F5 the emphasis re-point feeds that utility: the text half of the 1.11:1 failure, the
# panel background being the other half.
BURGER_SECTION_TITLE_CLASSES = frozenset({
    "bg-transparent", "fw-bolder", "text-900", "pt-3", "pb-2",
})
# The panel classes are ancestors of anything rendered inside it.
BURGER_SECTION_TITLE_ANCESTORS = (
    BURGER_SIDEBAR_ANCESTORS | BURGER_PANEL_CLASSES | {"list-unstyled", "py-2", "ps-0", "mb-0", "px-3"}
)

# `background` and `background-color` are one property family: the shorthand resets the colour, and
# core uses both spellings for these surfaces.
BACKGROUND_PROPS = ("background", "background-color")

# Core values grounded from core's own source, so each guard names the regression signature it
# refuses. The ratios are those of core's values in the dark bundle.
#
# Dropdown item tokens: core re-declares the four Bootstrap dropdown-link scalars and only
# $dropdown-link-color is semantic; the other three are black/grayscale literals no surface or text
# override reaches.
CORE_DROPDOWN_LINK_HOVER_COLOR = BLACK      # $black - the autocomplete active row = 1.20:1
CORE_DROPDOWN_LINK_ACTIVE_COLOR = BLACK     # $black
CORE_LIST_GROUP_ACTION_HOVER_COLOR = "#212529"   # $gray-900 - the systray row = 1.14:1
# The $o-grays ramp feeding `.bg-N00` through o-print-color. `.bg-100` is the command-palette footer
# strip, where the muted text tier #8EA5A8 is 2.46:1.
CORE_LIGHT_BG_100 = "#f8f9fa"   # $o-gray-100
CORE_LIGHT_BG_200 = "#e9ecef"   # $o-gray-200
CORE_LIGHT_BG_300 = "#dee2e6"   # $o-gray-300
# Near-black text utilities: $o-gray-900 / $o-black.
CORE_LIGHT_TEXT_DARK = "#212529"
CORE_LIGHT_TEXT_BLACK = BLACK
# A separate lever reads the near-black text: core wraps every `.btn-link.text-*` in
# `o-btn-link-variant($o-gray-600 !important, ...)`, which emits a direct `color:` rather than a
# custom property, so it outranks `.text-dark` whatever --color holds (the mail-activity
# "Reschedule" toggler, 3.73:1 at rest).
CORE_LIGHT_BTN_LINK_MUTED = "#6c757d"   # $o-gray-600
# Accent foregrounds with no dark arm. (a) `.btn-outline-primary`: core ships no "primary" key in
# $o-btns-bs-outline-override, so the label compiles the light-mode teal #007F8E verbatim = 3.69:1
# on the dark panel (the form "New" button, the kanban "Load more..." control). (b)
# $o-theme-text-colors, core's WCAG-tuning seam for the contextual text utilities: four values tuned
# for a white page, 3.71-3.85:1 on the dark panel (`.text-danger` is 3.76:1).
CORE_LIGHT_THEME_TEXT_COLORS = {
    "danger": "#d23f3a",
    "success": "#008818",
    "info": "#0180a5",
    "warning": "#9a6b01",
}

# A hover / selection band must be perceptible without becoming a slab: a contrast band rather than
# a pinned hex. The floor is anchored on light mode's `rgba($black, .08)` over white (~#EBEBEB =
# 1.19:1); the ceiling rejects a bright slab, like DARK_ACTIVE_FILL_MAX_GLARE.
DARK_STATE_BAND_MIN_CONTRAST = 1.15
DARK_STATE_BAND_MAX_CONTRAST = 3.0

# Bootstrap emits the dropdown-link scalars as runtime custom properties on `.dropdown-menu` (no
# `bs-` prefix in Odoo) and `.dropdown-item` reads them. The pool is minimal so an unscoped rule
# always applies and no view-specific rule is admitted.
#
# The modelled menu is a Bootstrap-native `.dropdown-menu`, deliberately NOT an OWL
# `.o-dropdown--menu`: core zeroes the native hover/active effects for OWL menus and drives the
# highlight from a JS-managed `.focus` class, so a `:hover` item there resolves
# `background-color: transparent` whatever the tokens hold. viin_backend_theme overrides that path
# and guards it in its own module. The dropdown-link tokens govern the native `.dropdown-item:hover`
# / `.active`, which the html_editor toolbars, the model-field-selector popover and the o-nocontent
# dropdown render.
DROPDOWN_MENU_CLASSES = frozenset({"dropdown-menu"})
DROPDOWN_MENU_ANCESTORS = frozenset({"o_web_client"})
DROPDOWN_ITEM_CLASSES = frozenset({"dropdown-item"})
DROPDOWN_ITEM_ANCESTORS = DROPDOWN_MENU_ANCESTORS | DROPDOWN_MENU_CLASSES
# `--list-group-action-hover-color` / `--list-group-active-*` are declared on `.list-group` and read
# by `.list-group-item-action:hover` / `.list-group-item.active` (the systray Activity/Messaging
# menu).
LIST_GROUP_CLASSES = frozenset({"list-group"})
LIST_GROUP_ANCESTORS = frozenset({"o_web_client"})
LIST_GROUP_ITEM_ACTION_CLASSES = frozenset({"list-group-item", "list-group-item-action"})
LIST_GROUP_ITEM_ACTIVE_CLASSES = frozenset({"list-group-item", "list-group-item-action", "active"})
LIST_GROUP_ITEM_ANCESTORS = LIST_GROUP_ANCESTORS | LIST_GROUP_CLASSES
# A bare utility class in ordinary webclient content, with no view-type class in the pool, so a
# view-scoped rule is excluded and the generic utility is measured.
UTILITY_ANCESTORS = frozenset({"o_web_client", "o_action_manager", "o_view_controller"})
# The form "New" button in the control panel; not sibling-gated, so no previous sibling is modelled.
FORM_NEW_BUTTON_CLASSES = frozenset({"btn", "btn-outline-primary", "o_form_button_create"})
FORM_NEW_BUTTON_ANCESTORS = frozenset({
    "o_web_client", "o_action_manager", "o_view_controller", "o_form_view", "o_control_panel",
    "o_cp_buttons", "d-flex",
})
# The black-on-light pill exceptions the gray and near-black utility families must not reach, each
# carrying its own bg+text pair: `.o_tag.o_tag_color_N` through o-print-color on both axes, `.badge`
# + `.o_badge_color_N` through direct `!important` declarations, `.text-bg-300` through core's
# color-contrast() label. Colour index 1 is representative: every index comes from the same two
# adjust-color() expressions.
TAG_PILL_CLASSES = frozenset({"o_tag", "o_tag_color_1"})
BADGE_PILL_CLASSES = frozenset({"badge", "o_badge_color_1"})
TEXT_BG_300_CLASSES = frozenset({"text-bg-300"})
# The highlighted suggestion row of an m2o/m2m/o2m dropdown. It carries none of the
# `o_m2o_start_typing` / `o_m2o_no_result` / `o_m2o_dropdown_option` variant classes on purpose:
# core ships four competing `ui-state-active` rules and the most specific belongs to the "start
# typing..." placeholder row, whose `background: none` must not be mistaken for this row's band.
AUTOCOMPLETE_ACTIVE_ROW_CLASSES = frozenset({
    "dropdown-item", "ui-menu-item-wrapper", "text-truncate", "ui-state-active",
})
AUTOCOMPLETE_ACTIVE_ROW_ANCESTORS = frozenset({
    "o_web_client", "o-autocomplete", "o-autocomplete--dropdown-menu", "ui-widget", "show",
    "o-autocomplete--dropdown-item", "ui-menu-item", "d-block",
})


def _colour_spellings(hex_colour):
    """Every lower-cased form the SCSS compiler can emit a given ``#rrggbb`` colour as.

    The hex literal, and the bare ``r,g,b`` triplet Odoo's `to-rgb()` produces for the o-print-color
    mixin (how the group-by facet paints), with and without spaces.
    """
    red, green, blue = (int(hex_colour.lstrip("#")[start:start + 2], 16) for start in (0, 2, 4))
    return (
        hex_colour.lower(),
        "%d,%d,%d" % (red, green, blue),
        "%d, %d, %d" % (red, green, blue),
    )


def _relative_luminance(hex_colour):
    """Relative luminance per the WCAG 2.1 definition.

    Transcribed from the W3C specification, an external formula, so a readability assertion built on
    it cannot compare production logic against itself.
    """
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
    """Alpha-composite ``fg_hex`` at ``alpha`` over an opaque ``bg_hex``.

    CSS ``opacity`` blends the whole element, text included, so the pixel a user reads is this
    composite, not the un-faded colour; contrast must be measured on it.

    :return: the #rrggbb result
    """
    fg = [int(fg_hex[o:o + 2], 16) for o in (1, 3, 5)]
    bg = [int(bg_hex[o:o + 2], 16) for o in (1, 3, 5)]
    out = [round(fg[i] * alpha + bg[i] * (1 - alpha)) for i in range(3)]
    return "#%02x%02x%02x" % tuple(out)


# One non-nested `selectors { body }` rule. `[^{}]` keeps each match to one rule, so rules inside
# @media / @supports wrappers are still captured individually.
_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
# The asset pipeline prepends a `/* <source-file-path> */` banner to each source-file fragment; it
# would glue onto the following selector group, so it is stripped before parsing selectors.
_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
# Tokens of one compound selector. Pseudo-classes/elements come first so `:not(...)` and `::before`
# win over the bare-identifier branch; the nested-paren alternative keeps `:not(.a:hover)` intact.
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
# Core emits colours as `RGBA(0, 187, 206, var(--bg-opacity, 1))` through o-print-color, which a
# hex-only reader would miss. Channels are decimals because Sass colour functions emit fractional
# ones (`.o_tag.o_tag_color_1` compiles `RGBA(255, 155.5, 155.5, ...)`); _normalize_colour rounds
# them, as a browser rasterises.
_FUNC_RGB_RE = re.compile(
    r"\brgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)", re.IGNORECASE,
)

# A bare element type (`i`, `span`, `div`), anchored so it cannot be confused with a class, id,
# attribute or pseudo token, which all carry a leading sigil.
_TYPE_SELECTOR_RE = re.compile(r"[A-Za-z][\w-]*")

# Pseudo-classes describing a state or structural position rather than a different element. A
# compound is a candidate only if every one it carries was declared by the caller, so a `:hover`
# rule never pollutes the resting-state answer.
_STATE_PSEUDO_CLASSES = frozenset({
    "hover", "focus", "focus-visible", "focus-within", "active", "disabled", "enabled",
    "checked", "first-child", "last-child", "only-child", "first-of-type", "last-of-type",
})


def _normalize_colour(value):
    """Return ``value``'s first colour as a lower-case #rrggbb string, or None.

    Accepts #rgb, #rrggbb, #rrggbbaa and rgb()/rgba(), so core's o-print-color output and
    hand-written hexes compare on equal terms.
    """
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
    """Return the alpha (0.0-1.0) a colour value carries, or 1.0 when opaque or unknown.

    Reads ``rgba()`` / ``hsla()`` and 8-digit ``#rrggbbaa``. Needed because _normalize_colour drops
    alpha, so a token whose defect is opacity (the navbar entry text ``rgba(255,255,255,.9)``) would
    look like an AA-passing #FFFFFF.
    """
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

    The state-axis dual of :func:`_compound_classes` (``:not()`` arguments and pseudo-elements
    excluded); used to reject an ancestor compound the class-only ancestor model can never satisfy.
    """
    found = set()
    for token in _COMPOUND_TOKEN_RE.findall(compound):
        if token.startswith(":not(") or token.startswith("::"):
            continue
        if token.startswith(":"):
            name = token[1:].split("(", 1)[0]
            if name in _STATE_PSEUDO_CLASSES:
                found.add(name)
    return found


def _compound_matches(compound, classes, states, pseudo_element, tag=None):
    """Whether one compound selector matches an element with ``classes`` in ``states``.

    Conservative about what it does not model: a compound with an id, an attribute selector or an
    unrecognised pseudo-class returns False, so exotic competitor rules are ignored.

    A type selector matches only an element that declares its tag. An element modelled without one
    fails every type-bearing compound, which hides rules such as core's
    `.o-mail-Message-body > i.text-muted.opacity-75`; a guard whose subject is styled through its tag
    must declare it.

    Pseudo-element matching is strict in both directions: a ``::before`` query matches only a
    compound naming that pseudo-element, and such a compound never matches a query for the
    originating element (`.btn` is no competitor for a ``::before`` background).

    :param tag: lower-cased tag name of the element, or None when not modelled
    """
    matched_pseudo_element = False
    for token in _COMPOUND_TOKEN_RE.findall(compound):
        if token.startswith("::"):
            if token[2:] != (pseudo_element or ""):
                return False
            matched_pseudo_element = True
        elif token.startswith(":not("):
            # :not() fails as soon as any argument matches. Its arguments constrain the originating
            # element, never the pseudo-element box, so the pseudo-element is not propagated.
            for argument in token[5:-1].split(","):
                if _compound_matches(argument.strip(), classes, states, None, tag):
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
        elif _TYPE_SELECTOR_RE.fullmatch(token):
            if tag is None or token.lower() != tag:
                return False
        else:
            return False                              # id or [attr] - not modelled
    if pseudo_element and not matched_pseudo_element:
        return False
    # At least one positive class, so the universal-ish rules of unrelated components are no
    # competitors.
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

    Follows the CSS cascade for a single origin with no inline styles: ``!important`` beats normal,
    then higher specificity, then later source order, then later declaration order in a rule.

    :param element: dict accepted by :func:`_matches_element`
    """
    best_key, best_value = None, None
    for order, selector, body in _iter_rules(css):
        if not _matches_element(selector, element):
            continue
        for decl_order, (value, important) in enumerate(_declarations(body, prop_names)):
            key = (important, _specificity(selector), order, decl_order)
            if best_key is None or key > best_key:
                best_key, best_value = key, value
    return best_value


def _selector_scope_applies(selector, ancestors):
    """Whether ``selector``'s ancestor context can be satisfied by the ``ancestors`` class pool.

    The scope half of :func:`_matches_element`, usable on its own by a guard that identifies its
    rules by subject and reads raw declarations: a subject-only match would hand it a rule scoped to
    a context the element is not in. Every ancestor compound's positive classes must be a subset of
    ``ancestors``, so an unscoped rule applies and a rule scoped to another context never does;
    sibling-linked compounds are skipped. Combinator kind, ancestor order and @media context are not
    distinguished and the pool is a flat set, which can only add candidates, so a guard fails loudly
    rather than passing silently.

    :param ancestors: class names carried by the element's styling ancestors
    """
    compounds = _split_compounds(selector)
    for position, (_combinator, compound) in enumerate(compounds[:-1]):
        if compounds[position + 1][0] in ("+", "~"):
            continue                                  # sibling of the chain, not an ancestor of it
        if not _compound_classes(compound) <= ancestors:
            return False
        if _compound_state_pseudo_classes(compound):
            # The pool holds classes only, so a compound gated on a state pseudo-class can never be
            # confirmed. A class-less one would pass the subset check vacuously: Bootstrap's
            # `fieldset:disabled .btn` (0,2,1) would outrank the real `.btn:hover` (0,2,0), though a
            # search facet is never inside a disabled <fieldset>.
            return False
    return True


def _custom_property_scope_reaches(selector, pool):
    """Whether a custom property declared by a rule with ``selector`` is in scope on an element.

    A custom property inherits, so a declaration reaches the element from itself, from any ancestor
    or from `:root`; the subject compound is therefore held to the same pool as the ancestors. A rule
    scoped to a context the element is not in (a customizer-themed dark navbar) does not reach it.
    Every compound on the chain must carry positive classes within ``pool``; sibling-linked
    compounds are skipped. Unlike :func:`_selector_scope_applies`, a compound gated on a state
    pseudo-class is admitted, so an existence guard over hover/active hooks still sees
    `.o_main_navbar:hover .o_nav_entry { --hook: ... }`. Everything ignored can only admit a rule, so
    a guard fails loudly rather than passing silently.

    :param pool: classes of the element and of every styling ancestor
    """
    compounds = _split_compounds(selector)
    for position, (_combinator, compound) in enumerate(compounds):
        if position + 1 < len(compounds) and compounds[position + 1][0] in ("+", "~"):
            continue                                  # sibling of the chain, not on it
        if not _compound_classes(compound) <= pool:
            return False
    return True


def _custom_property_declarations_reaching(css, prop_name, pool):
    """Return the compiled declarations of custom property ``prop_name`` that reach an element.

    :param pool: classes of the element and of every styling ancestor
    :return: ``[(selector, value), ...]`` of the rules :func:`_custom_property_scope_reaches` admits
    """
    found = []
    for _order, selector, body in _iter_rules(css):
        if not _custom_property_scope_reaches(selector, pool):
            continue
        for value, _important in _declarations(body, (prop_name,)):
            found.append((selector, value))
    return found


def _matches_element(selector, element):
    """Whether ``selector``'s subject (its right-most compound) matches the modelled element.

    Ancestor and sibling context are approximated, which suffices for the class-only selectors these
    surfaces use. Every approximation can only add candidate rules, so a guard fails loudly rather
    than passing silently:

    * ancestor context is decided by :func:`_selector_scope_applies`;
    * a sibling-gated subject is matched against ``element["prev_sibling"]`` unconditionally: a
      sibling-gated rule must not apply to an element with no such sibling (Bootstrap's
      `.btn-check:checked + .btn` would otherwise outrank the plain `.btn` rule);
    * a child-combinator subject (``>``) is matched against ``element["parent"]`` when the caller
      models a parent, and read as a descendant otherwise.

    Ancestor order, deeper ``>`` links, sibling chains over one hop and @media context are not
    distinguished.

    :param element: dict with ``classes`` and ``ancestors``, and optionally ``states``,
        ``pseudo_element``, ``tag``, ``prev_sibling`` and ``parent``
    """
    compounds = _split_compounds(selector)
    if not compounds:
        return False
    if not _compound_matches(
        compounds[-1][1], element["classes"], element.get("states", frozenset()),
        element.get("pseudo_element"), element.get("tag"),
    ):
        return False
    if not _selector_scope_applies(selector, element["ancestors"]):
        return False
    if compounds[-1][0] in ("+", "~"):
        prev_sibling = element.get("prev_sibling") or frozenset()
        if not _compound_matches(compounds[-2][1], prev_sibling, frozenset(), None):
            return False
    if compounds[-1][0] == ">" and element.get("parent") is not None:
        # A parent is the nearest ancestor, so a subset check; a classless parent compound (a bare
        # `div >`) has an empty class set and stays permissive.
        if not _compound_classes(compounds[-2][1]) <= element["parent"]:
            return False
    return True


def _computed_value(css, chain, prop_names, depth=6):
    """Resolve ``prop_names`` on ``chain[0]``, following ``var()`` through the ancestor chain.

    Custom properties inherit, so an unresolved ``var(--x)`` is looked up on the element, then
    outwards; with no declaration anywhere it falls back to its own fallback argument, as a browser
    does.

    :param chain: the element and its styling ancestors, innermost first
    :param depth: maximum number of ``var()`` hops
    :return: the resolved value, or None
    """
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
    """Cascade winner of ``prop_names`` for the debug db-name ``<mark>`` in the user menu.

    The ``<mark>`` is bare and classless, which the generic resolver refuses. Among the rules whose
    subject is exactly ``mark`` and which scope it under ``.oe_topbar_name``, the winner is picked
    as in :func:`_winning_declaration`.

    :return: the winning value, or None when no such rule exists
    """
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
    """Cascade winner of ``prop_names`` for a RESTING burger/app-menu sidebar menu row.

    A menu row is a bare ``<li>`` / ``<button>`` that core styles by type under
    ``.o_burger_menu_content``, which the generic resolver refuses. Rules whose subject is exactly
    ``li`` / ``button`` are ordered as in :func:`_winning_declaration`; hover subjects (``li:hover``)
    do not match, so a hover value is never read as the resting one.

    :return: the winning value, or None when no such rule exists
    """
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
    """Rewrite ``selector`` with bare TYPE tokens dropped from every compound.

    Turns a type+class subject (autocomplete's ``a.ui-state-active``) into the class-only shape
    :func:`_compound_matches` understands, keeping the class and state constraints. A type-only
    ancestor compound is omitted: the ancestor pool holds no element names, so it could never be
    confirmed, and omitting it errs toward admitting a competitor.

    :return: the rewritten selector, or None when the subject itself is type-only
    """
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

    Orders as :func:`_winning_declaration`, with specificity measured on the original selector and
    only the matching going through :func:`_strip_type_selectors`. A name-only reader would hand the
    `background: none` of the autocomplete "start typing..." placeholder row to the real suggestion
    row; honouring the class context excludes it.

    :param scope: substring every candidate selector must contain, keeping the scan inside one
        component
    :return: the winning value, or None
    """
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
    """Cascade winner of ``prop_names`` for the highlighted m2o/m2m autocomplete suggestion row.

    The row is ``a.dropdown-item.ui-menu-item-wrapper.text-truncate.ui-state-active`` and carries
    none of the `o_m2o_start_typing` / `o_m2o_no_result` / `o_m2o_dropdown_option` variant classes,
    so the rules gated on those are excluded. Core reads the dropdown-link hover pair as raw Sass
    here (`color: $dropdown-link-hover-color; background-color: $dropdown-link-hover-bg`), so no
    runtime `--dropdown-link-*` re-point reaches it, only the Sass scalar.

    :return: the winning value, or None when core moved or renamed the component
    """
    element = {
        "classes": AUTOCOMPLETE_ACTIVE_ROW_CLASSES,
        "ancestors": AUTOCOMPLETE_ACTIVE_ROW_ANCESTORS,
        "prev_sibling": frozenset(),
    }
    return _winning_declaration_for_typed_subject(css, element, prop_names, "o-autocomplete")


# Length tokens of a box-model value; only a non-zero one can add height to a border-box.
_ZERO_LENGTH_TOKEN_RE = re.compile(r"^0(?:px|em|rem|%|pt|vh|vw|vmin|vmax)?$")
_LENGTH_TOKEN_RE = re.compile(r"^-?[\d.]+(?:px|em|rem|%|pt|vh|vw|vmin|vmax)?$")


def _is_zero_box_geometry(value):
    """Whether a resolved box-model declaration carries no non-zero length.

    A `border`/`padding` shorthand mixes a length with style keywords and a colour
    (``0 solid transparent``); only a length token can add height, so other tokens are ignored. A
    `calc()`/`var()` token counts as non-zero: it cannot be ruled out.
    """
    for token in value.strip().split():
        lowered = token.lower()
        if _ZERO_LENGTH_TOKEN_RE.match(lowered):
            continue
        if _LENGTH_TOKEN_RE.match(lowered):
            return False
        if "calc(" in lowered or "var(" in lowered:
            return False
    return True


_NON_INFLATING_EXTENT_KEYWORDS = frozenset({
    "auto", "none", "fit-content", "min-content", "max-content",
    "inherit", "initial", "unset", "revert", "revert-layer",
})
_PERCENTAGE_EXTENT_RE = re.compile(r"^(\d+(?:\.\d+)?)%$")


def _is_non_inflating_extent(value):
    """Whether a resolved height/min-height/max-height cannot pin a border-box to a foreign size.

    A percentage resolves against the parent's content height, so where the parent is sized by the
    row it contains, `height: 100%` lands the box on the row it already occupies; `auto` and the
    intrinsic keywords are content-derived. An absolute length, `calc()`/`var()` and a percentage
    above 100% stay offenders. Unlike :func:`_is_zero_box_geometry`, which suits `padding`/`border`
    where every length adds to the box, a percentage here speaks about the parent.
    """
    lowered = value.strip().lower()
    if lowered in _NON_INFLATING_EXTENT_KEYWORDS:
        return True
    match = _PERCENTAGE_EXTENT_RE.match(lowered)
    if match:
        return float(match.group(1)) <= 100.0
    return _is_zero_box_geometry(lowered)


@tagged("post_install", "-at_install")
class BrandCascadeCompileTest(TransactionCase):

    def _backend_bundle(self):
        """Return the compiled web.assets_backend AssetsBundle, with its ``css_errors`` populated."""
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
            "cascade surfaces can be verified.",
        )
        return css

    def _compiled_css(self, bundle_name):
        """Compile any asset bundle by name and return its CSS payload as decoded text.

        :raises AssertionError: when the payload is empty, since an unbuilt bundle verifies nothing
        """
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

        :root is not modelled by :func:`_matches_element` (it needs a positive class). The trailing
        ``:`` in the pattern keeps ``--link-color`` from matching ``--link-color-rgb``.
        """
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
            "viin_brand/controllers/webmanifest.py (the single Python brand-hex SSOT).",
        )
        return VIINDOO_THEME_COLOR.lower()

    def _brand_secondary_ssot(self):
        """Return the light $o-brand-secondary hex, read from the token SSOT.

        Every "purple" assertion anchors on this reader instead of re-literalising the colour. The
        "purple, not teal" claim is asserted separately against the teal ladder, so pointing the
        token at a teal still fails loudly.
        """
        with open(BRAND_VARIABLES_SCSS, encoding="utf-8") as scss_file:
            value = _resolve_scss_hex(scss_file.read(), "$o-brand-secondary")
        self.assertIsNotNone(
            value,
            "$o-brand-secondary must be declared in %s - it is the SSOT for every META/STRUCTURE "
            "purple surface in this cluster." % os.path.basename(BRAND_VARIABLES_SCSS),
        )
        return value.lower()

    def _dark_palette_var(self, var_name):
        """Alias of the module-level :func:`dark_palette_var`."""
        return dark_palette_var(var_name)

    def _resolve_secondary_own_band(self, css, element, surface):
        """Resolve the ``(text, background)`` a `*-secondary` variant paints on itself.

        Both properties are declared on ``element`` (`.alert`/`.list-group-item`) and re-pointed by
        its `-secondary` modifier on the same element; only the :root custom-property fallback
        (_resolve_colour_value) is needed to follow `var(--secondary-text-emphasis)` /
        `var(--secondary-bg-subtle)`.
        """
        text = self._effective_label_colour(css, [element], surface)
        raw_background = _winning_declaration(css, element, BACKGROUND_PROPS)
        self.assertIsNotNone(
            raw_background,
            "No compiled background declaration applies to %s - the surface is unstyled, so its "
            "own subtle band cannot be verified." % surface,
        )
        background = self._resolve_colour_value(css, [element], raw_background)
        self.assertIsNotNone(
            background,
            "%s resolves background %r to no colour - the subtle-band token was dropped or core "
            "moved the surface to a different lever." % (surface, raw_background),
        )
        return text, background

    def _resolve_colour(self, css, chain, prop_names, surface):
        """Resolve a property to a normalised colour, failing loudly when nothing paints it."""
        value = _computed_value(css, chain, prop_names)
        self.assertIsNotNone(
            value,
            "No compiled declaration of %s applies to %s. The surface is unstyled, so the "
            "brand cascade cannot be reaching it." % ("/".join(prop_names), surface),
        )
        colour = _normalize_colour(value)
        self.assertIsNotNone(
            colour,
            "%s resolves %s to %r, which carries no colour. The token was dropped or "
            "core moved the surface to a different lever."
            % (surface, "/".join(prop_names), value),
        )
        return colour

    def test_navbar_menu_entry_interactive_states_use_deep_chrome_rung(self):
        """Hovered, focused, pressed and open navbar menu entries render the deep chrome rung.

        Core paints all four states from `$o-navbar-entry-bg--hover` / `--active`, defaulting to
        `rgba($o-black, .08)`, a barely perceptible ~#007583 over the teal navbar. The surface must
        be darker than resting, not the decorative teal, and WCAG AA against the white entry text,
        read off the value the cascade computes rather than a pinned hex.
        """
        flat_brand_teal = self._assert_flat_teal_available()
        css = self._css()

        # Every navbar chrome state, as a real element inside .o_menu_sections.
        states_under_test = (
            ("hovered menu entry", {"o_nav_entry"}, frozenset({"hover"})),
            ("focused menu entry", {"o_nav_entry"}, frozenset({"focus"})),
            ("pressed menu entry", {"o_nav_entry"}, frozenset({"active"})),
            ("hovered section dropdown toggle", {"dropdown-toggle"}, frozenset({"hover"})),
            # .dropdown.show.dropdown-toggle also covers the open overflow ("More") menu, which
            # core renders inside .o_menu_sections.
            ("open section/overflow dropdown", {"dropdown", "show", "dropdown-toggle"}, frozenset()),
        )

        # Core reads the two hooks and never declares them where the regular navbar entries inherit
        # them, so the var() fallback the module's variables feed is load-bearing. A declaration on
        # that chain would stop the fallback rendering, and the resolution below walks only the
        # entry, so the check is scoped here: a declaration under another context (the Customizer's
        # own dark top bar) never reaches these entries.
        navbar_chain_pool = NAVBAR_ANCESTORS.union(
            *(classes for _label, classes, _states in states_under_test)
        )
        navbar_state_hooks = (
            "--NavBar-entry-backgroundColor--hover", "--NavBar-entry-backgroundColor--active",
        )
        for hook in navbar_state_hooks:
            declarations = _custom_property_declarations_reaching(css, hook, navbar_chain_pool)
            self.assertFalse(
                declarations,
                "%s is DECLARED where the regular navbar entries inherit it (%s), so the compiled "
                "var() fallback that carries the chrome rung does not render there. Re-ground this "
                "guard against the new lever."
                % (hook, "; ".join(
                    "%s { %s: %s }" % (selector, hook, value) for selector, value in declarations
                )),
            )

        for label, classes, states in states_under_test:
            element = {
                "classes": frozenset(classes),
                "states": states,
                "ancestors": NAVBAR_ANCESTORS,
                "prev_sibling": frozenset({"o_nav_entry", "dropdown-toggle"}),
            }
            colour = self._resolve_colour(css, [element], BACKGROUND_PROPS, label)
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
                _contrast_ratio(colour, WHITE), WCAG_AA_NORMAL_TEXT,
                "The %s compiled to %s, which does not clear WCAG AA (>= %.1f:1) against the "
                "white navbar entry text; it measures %.2f:1."
                % (label, colour, WCAG_AA_NORMAL_TEXT, _contrast_ratio(colour, WHITE)),
            )

    def test_search_facet_field_and_filter_render_chrome_base_on_white(self):
        """Field and filter search facets render the chrome base under white text.

        Core renders both as `btn btn-primary`. The module pins the Bootstrap button custom
        properties (--btn-bg / --btn-border-color / --btn-color and their hover and active rungs)
        on the label element itself, so the sibling .o_facet_remove close button keeps its red.

        The resting and hovered backgrounds are the value the cascade computes through the pinned
        tokens. The pressed rung is asserted on `--btn-active-bg`: core reaches that state through
        `.btn:first-child:active` / `.btn.active` / `.btn.show`, which turn on structural position and
        runtime classes a static stylesheet cannot pin to this element. The resolver models each
        element's previous sibling so Bootstrap's `.btn-check:checked + .btn` (0,3,0, no state
        pseudo-class) cannot hand the resting query a pressed value.

        Hover and pressed are asserted on readability (WCAG AA against the white facet text), not on
        a pinned hex. The pressed rung is the one that fails on a revert: it falls back to the
        near-white #E6F2F4 (~1.1:1) of the primary button map.
        """
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
            "--btn-* pinning on .o_searchview_facet_label was dropped, so core's "
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
            "A field/filter search facet's text compiled to %s instead of white. The "
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
        self.assertGreaterEqual(
            _contrast_ratio(hovered_bg, resting_fg), WCAG_AA_NORMAL_TEXT,
            "A hovered field/filter search facet renders %s text on %s - %.2f:1, below the WCAG "
            "AA normal-text threshold of %.1f:1. The --btn-hover-bg pinning is missing."
            % (resting_fg, hovered_bg, _contrast_ratio(hovered_bg, resting_fg),
               WCAG_AA_NORMAL_TEXT),
        )

        pressed_token = self._resolve_colour(
            css, [element], ("--btn-active-bg",), "pressed field/filter search facet token"
        )
        self.assertGreaterEqual(
            _contrast_ratio(pressed_token, resting_fg), WCAG_AA_NORMAL_TEXT,
            "The pressed-state token --btn-active-bg on a field/filter search facet resolves to "
            "%s, which is %.2f:1 against the facet's white text %s - below the WCAG AA "
            "normal-text threshold of %.1f:1."
            % (pressed_token, _contrast_ratio(pressed_token, resting_fg), resting_fg,
               WCAG_AA_NORMAL_TEXT),
        )

        border = self._resolve_colour(
            css, [element], ("--btn-border-color",), "field/filter search facet border token"
        )
        self.assertEqual(
            border, CHROME_BASE,
            "A field/filter search facet's border token compiled to %s; it must match the chrome "
            "base fill %s so the pill reads as one branded unit." % (border, CHROME_BASE),
        )

    def test_search_facet_groupby_is_the_structure_purple_not_the_filter_teal(self):
        """A groupBy search facet renders the structure purple, distinct from a filter facet.

        Teal is an action and purple is meta-structure: a field or filter facet narrows the record
        set and stays teal, a groupBy facet only re-organises it. The discriminator is the facet type
        itself (`'text-bg-action': facet.type == 'groupBy'`), not `.o_facet_with_domain`, which keys
        on facet.domain and would leak onto a domain-less non-groupBy facet.

        Both core shapes are asserted: a groupBy always gets `text-bg-action` and, when the search
        model can order by count, a bare `btn` too, so a rule keyed on `:not(.btn)` would stop
        matching on such views. Core generates `.text-bg-action` through o-print-color with
        `background-color: var(--background-color) !important` and `color: var(--color) !important`,
        which beat any specificity, so the override must feed the two custom properties those read.

        The arms assert opposite things. Light: the facet is the brand purple under a white label
        (6.99:1) and differs from a filter facet. Dark: the facet is neither purple nor the
        dark-tuned purple and is core's own `.text-bg-action` paint, since the rule must not be
        emitted into that bundle at all (`@if not $o-viin-dark-bundle`).
        """
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
                        "this guard exists for. Either the rule does not key on .text-bg-action "
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
                    # Dark arm: the facet has no accent of ours. Both purples are refused by name and
                    # the positive half asserts core's default paint. Group-by and filter facets are
                    # both teal here, in different shades, so the "differs from filter" check is
                    # light-only.
                    self.assertNotEqual(
                        background, expected_light_purple,
                        "A %s compiled the brand purple %s in the DARK bundle. The purple accent is "
                        "LIGHT-ONLY: the rule must be inside "
                        "`@if not $o-viin-dark-bundle` so it never reaches web.assets_web_dark."
                        % (label, expected_light_purple),
                    )
                    self.assertNotEqual(
                        background, DARK_BUNDLE_FORBIDDEN_PURPLE,
                        "A %s compiled the dark-tuned purple %s. $o-brand-secondary has no dark "
                        "arm: the facet carries no purple in the dark bundle."
                        % (label, DARK_BUNDLE_FORBIDDEN_PURPLE),
                    )
                    self.assertEqual(
                        background, flat_brand_teal,
                        "A %s compiled %s in the dark bundle, but the DEFAULT is "
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

            # The values half of the pill follows its label. Light: the purple, so the facet reads
            # as one unit (core draws no border there; the teal frame is this module's). Dark: the
            # label is core's teal, so the frame must revert with it, or a purple frame around a
            # teal label reads as two components - the signature of guarding the label rule only.
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
                    frame, (expected_light_purple, DARK_BUNDLE_FORBIDDEN_PURPLE),
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

    def test_search_facet_favourite_keeps_native_yellow_and_no_teal_frame(self):
        """A saved-favourite search facet keeps core's yellow and receives no chrome frame.

        Core renders a favourite facet as `btn btn-favourite`, generated by
        button-variant($o-main-favorite-color), gold #f3cc00, which keeps the "saved filter"
        affordance. Every teal-ifying facet rule therefore carries a `:not(.btn-favourite)` guard,
        including the .o_facet_values frame: a teal frame hugging a yellow label contradicts the
        design as loudly as repainting the label. A test asserting the favourite facet is teal would
        be wrong.
        """
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
                "The %s favourite search facet compiled to the chrome colour %s. The product "
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
            "core uses for saved-filter facets.",
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
            "no border there, and the favourite facet stays 100%% native - the "
            "`:not(.btn-favourite)` guard on the .o_facet_values rule was dropped." % frame_colour,
        )

    def test_statusbar_current_arrow_outline_is_chrome_base_over_a_light_fill(self):
        """The current statusbar arrow is outlined in the chrome base over a light fill.

        Core routes both the arrow outline and its notch through --o-statusbar-border-active,
        seeded from `$o-component-active-border` of the "secondary" entry of $o-btns-bs-override;
        brand_variables.scss sets that variable to the chrome base. The fill is deliberately not
        teal: $o-action is untouched, so $o-component-active-bg stays a light tint carrying dark
        text, and the asserted invariant is that the fill stays readable under dark text.
        """
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

        # The notch: core paints .o_arrow_button_current::before from the same token, so one token
        # covers both surfaces; asserting it guards against core splitting the notch onto its own
        # lever.
        notch_element = {
            # `btn btn-secondary o_arrow_button` plus the state class. The two Bootstrap classes
            # are load-bearing: without them the model excludes every `.btn` rule instead of ruling
            # it out on the merits.
            "classes": frozenset({
                "btn", "btn-secondary", "o_arrow_button", "o_arrow_button_current",
            }),
            "states": frozenset({"disabled"}),
            "pseudo_element": "before",
            "ancestors": STATUSBAR_ANCESTORS,
            # a row of sibling arrow buttons
            "prev_sibling": frozenset({"btn", "btn-secondary", "o_arrow_button"}),
        }
        notch = self._resolve_colour(
            css, [notch_element, status_element], BACKGROUND_PROPS, "statusbar current-arrow notch"
        )
        self.assertEqual(
            notch, CHROME_BASE,
            "The statusbar current-arrow NOTCH compiled to %s instead of the chrome base %s. Core "
            "does not paint .o_arrow_button_current::before from --o-statusbar-border-active, so "
            "the single token does not cover both the outline and the notch."
            % (notch, CHROME_BASE),
        )

        fill = self._resolve_colour(
            css, [status_element], ("--o-statusbar-background-active",),
            "statusbar current-arrow fill",
        )
        self.assertNotIn(
            fill, (CHROME_BASE, CHROME_DEEP),
            "The statusbar current-arrow FILL compiled to the chrome colour %s. $o-action must "
            "stay untouched so the arrow keeps its light fill with dark text - only the "
            "outline tier darkens." % fill,
        )
        self.assertGreaterEqual(
            _contrast_ratio(fill, BLACK), WCAG_AA_NORMAL_TEXT,
            "The statusbar current-arrow fill %s only reaches %.2f:1 against the dark step label, "
            "below the WCAG AA normal-text threshold of %.1f:1 - it is not the light tint the "
            "light-fill/dark-outline split depends on."
            % (fill, _contrast_ratio(fill, BLACK), WCAG_AA_NORMAL_TEXT),
        )

    def test_selected_settings_tab_indicator_is_chrome_base(self):
        """The selected Settings tab shows a chrome-base inset indicator.

        settings_form_view.scss draws it as `box-shadow: inset 2px 0 0 $o-component-active-border`,
        the same lever as the statusbar arrow. It is a separate test so the two surfaces can fail
        independently if core re-routes one of them onto a different variable.
        """
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

    def test_stat_value_renders_brand_secondary_purple_with_a_teal_icon(self):
        """A stat-button value renders the brand secondary purple, paired with a teal icon.

        Core reads the colour from `var(--o-stat-text-color, $o-brand-primary)`, whose fallback is
        the 2.33:1 decorative teal, so the module pins the custom property on .o-form-buttonbox. The
        expected purple is read from the $o-brand-secondary token rather than re-literalised, and
        the "purple, not teal" claim is asserted independently against both teals, so pointing the
        token at a teal still fails. A test asserting the value is teal would be wrong.
        """
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
        # .o_bottom_sheet is core's sanctioned exception (it pins --o-stat-text-color to
        # currentColor on mobile); the desktop form sheet is the surface under test, so that
        # context is excluded from the resolution.
        buttonbox = {
            "classes": frozenset({
                "o-form-buttonbox", "d-print-none", "position-relative", "d-flex", "w-md-auto",
                "o_not_full",
            }),
            "ancestors": BUTTONBOX_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        stat_value = {
            "classes": frozenset({"o_stat_value"}), "ancestors": STAT_BUTTON_ANCESTORS,
            "prev_sibling": frozenset({"o_stat_text"}),   # the text renders before the value
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
            "A stat-button value compiled to the chrome base %s. This surface is purple, not "
            "teal - see this test's docstring before changing it."
            % CHROME_BASE,
        )
        self.assertGreaterEqual(
            _contrast_ratio(value_colour, WHITE), WCAG_AA_NORMAL_TEXT,
            "A stat-button value renders %s on the white form sheet - %.2f:1, below the WCAG AA "
            "normal-text threshold of %.1f:1."
            % (value_colour, _contrast_ratio(value_colour, WHITE), WCAG_AA_NORMAL_TEXT),
        )

        # The pairing: a teal ICON above a purple VALUE. Core reads the icon from
        # var(--o-stat-button-color, $primary) and $primary is the chrome base, so the pairing
        # holds; assert it so a change to $primary cannot collapse both onto one colour.
        icon = {
            "classes": frozenset({"o_button_icon"}), "ancestors": STAT_BUTTON_ANCESTORS,
            "prev_sibling": frozenset(),                  # the icon is the first child
        }
        icon_colour = self._resolve_colour(css, [icon, buttonbox], ("color",), "stat-button icon")
        self.assertEqual(
            icon_colour, CHROME_BASE,
            "The stat-button ICON compiled to %s instead of the chrome base %s, breaking the "
            "teal-icon / purple-value pairing." % (icon_colour, CHROME_BASE),
        )
        self.assertNotEqual(
            icon_colour, value_colour,
            "The stat-button icon and value both compiled to %s. The icon is teal and the value "
            "purple; collapsing them onto one colour loses that pairing." % icon_colour,
        )

    def test_progressbar_trough_carries_the_brand_wash_not_core_white(self):
        """The progress-bar trough carries a near-white brand wash, not core's plain white.

        Core leaves the track at $o-view-background-color, plain white, which makes an empty bar
        indistinguishable from the sheet. The track is decoration (the value renders in the sibling
        .o_progressbar_value), so the wash is asserted for presence and hue, not contrast: a
        near-white tint leaning to the brand's cyan side (red channel lowest, every channel >= 0xE0),
        which survives a tweak of the mix percentage without re-implementing the Sass mix().
        """
        css = self._css()
        element = {
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

        red, green, blue = (int(trough[offset:offset + 2], 16) for offset in (1, 3, 5))
        self.assertTrue(
            red < green and red < blue and min(red, green, blue) >= 0xE0,
            "The progress-bar trough %s is not a near-white wash of the brand teal (expected a "
            "tint whose red channel is the lowest and whose channels all stay above 0xE0, so the "
            "track reads as a faint brand-tinted surface behind the filled portion)." % trough,
        )

    def test_backend_bundle_compiles_without_css_errors(self):
        """web.assets_backend compiles clean: no Sass error and no cached error payload.

        Every assertion in this file reads the compiled bundle, so a silent compile failure would
        make them all meaningless. On a Sass error Odoo does not raise: css() collects the message
        into ``css_errors`` and serves the previous stylesheet with an error banner appended. Both
        halves are checked: ``css_errors`` reports the compile that just ran, but css() returns early
        when a compiled attachment is cached, leaving the list empty over an error payload, so the
        payload markers are checked too. Sass compiles the whole bundle in one pass, so malformed
        SCSS in any file this module adds to it lands here.
        """
        bundle = self._backend_bundle()
        css = self._compiled_backend_css(bundle)

        self.assertFalse(
            bundle.css_errors,
            "web.assets_backend reported SCSS compile errors: %s. The cascade files "
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
                "Odoo appends when a Sass compile fails. A cached error "
                "payload is being served, so the backend is rendering stale styles." % marker,
            )

    def test_content_palette_o_color_1_stays_core_aubergine_while_chrome_stays_teal(self):
        """The editor/website content swatch o-color-1 renders core aubergine, not the brand teal.

        brand_variables.scss sets `$o-enterprise-color: #00BBCE` for the chrome, but core seeds the
        content palette from the same variable at compile time, so without a fix `o-color-1` bleeds
        to teal and breaks the core Hoot tests asserting rgb(113, 75, 103) = #714B67 (html_editor
        color_selector, website builder image_shape). brand_palette_reset.scss map-merges base-1
        o-color-1 back to aubergine after html_editor builds it, touching no chrome token.

        The observable is `.bg-o-color-1`, which html_editor generates from the active palette's
        o-color-1 entry. The fix is also proven scoped in the same bundle: a chrome facet still
        renders the chrome teal and the decorative brand teal still exists elsewhere.
        """
        # html_editor builds the content palette; without it there is nothing to bleed into and
        # brand_palette_reset.scss is a no-op, so the guard would fail vacuously. Skip instead.
        if not self.env["ir.module.module"].search_count(
            [("name", "=", "html_editor"), ("state", "=", "installed")]
        ):
            self.skipTest(
                "html_editor is not installed - no content colour palette is built, so the brand "
                "teal cannot bleed into o-color-1 and there is nothing to guard."
            )
        flat_brand_teal = self._assert_flat_teal_available()
        css = self._css()

        # .bg-o-color-1 is a plain, unscoped utility painted !important through o-print-color /
        # bg-variant, which the resolver's cascade and RGBA() normalisation handle.
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
            "brand teal $o-enterprise-color bled into the content palette (html_editor seeds base-1 "
            "o-color-1 from it) - brand_palette_reset.scss was dropped or its manifest append was "
            "removed, so the swatch is not reset to core."
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

        # Scoped-fix proof 1: a real chrome surface in the same bundle stays the chrome teal; a
        # disturbed chrome lever would move the field/filter facet base off CHROME_BASE.
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

        # Scoped-fix proof 2: the decorative brand teal still exists in the bundle - the reset
        # touches a content swatch, not the brand.
        self.assertIn(
            flat_brand_teal, css.lower(),
            "The flat brand-identity teal %s vanished from the compiled bundle. The content-palette "
            "reset must not nuke the brand decorative teal - only base-1 o-color-1 returns to core."
            % flat_brand_teal,
        )

    def test_brand_secondary_text_clears_wcag_aa_on_light_and_dark_surfaces(self):
        """The $o-brand-secondary readable-text surfaces clear WCAG AA in both schemes.

        Three surfaces read the same $o-brand-secondary variable as readable text: the desktop
        stat-button value and label (through .o-form-buttonbox's --o-stat-text-color, ours) and the
        mobile form label (`.o_xxs_form_view .o_form_label`, core's). On the light sheet #7F4282 is
        6.99:1; on the dark panel #111B1E it is 2.50:1, so the dark bundle must not use it. Core
        leaves `.o_stat_text` uncoloured at an inherited 3.12:1, so painting the label purple meets
        the brand request and repairs an AA failure.

        The answer in dark is no purple, not a darker purple: the dark arm refuses both purples and
        pins each surface to its default. The defaults differ because the surfaces are reached
        differently. The stat value is ours: `--o-stat-text-color` becomes $body-color, since core's
        own fallback `$o-brand-primary` is the decorative teal, still the wrong accent. The mobile
        label is core's rule, so it is neutralised at the token: dark_palette.scss re-points
        $o-brand-secondary to the dark muted tier, which also covers core's search-panel divider.

        Each surface is resolved on the surface it renders on, over {light: assets_backend / white,
        dark: assets_web_dark / #111B1E}.
        """
        with open(BRAND_VARIABLES_SCSS, encoding="utf-8") as scss_file:
            expected_light_secondary = _resolve_scss_hex(scss_file.read(), "$o-brand-secondary")
        self.assertIsNotNone(
            expected_light_secondary,
            "$o-brand-secondary must be declared in %s - it is the SSOT for the stat-value / mobile "
            "form-label colour." % os.path.basename(BRAND_VARIABLES_SCSS),
        )
        expected_light_secondary = expected_light_secondary.lower()

        # The surfaces, as the element chains the resolver walks.
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
        # The stat LABEL is the first child of .o_stat_info (the value models it as its previous
        # sibling), so it has no preceding sibling. Core gives `.o_stat_text` no colour, so it
        # inherits the btn-outline-secondary grey, 3.12:1 on white: the AA assertion below guards it.
        stat_label_chain = [
            {"classes": frozenset({"o_stat_text"}), "ancestors": STAT_BUTTON_ANCESTORS,
             "prev_sibling": frozenset()},
            buttonbox,
        ]
        mobile_label_chain = [
            {"classes": frozenset({"o_form_label"}), "ancestors": XXS_FORM_LABEL_ANCESTORS,
             "prev_sibling": frozenset()},
        ]
        # Each surface names its dark default: the stat value is ours to state (the bright
        # body-text tier), the mobile label is core's rule, neutralised at the token (the muted tier).
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
                        "%s. The purple accent is light-only."
                        % (label, expected_light_secondary, DARK_BODY_BG),
                    )
                    self.assertNotEqual(
                        colour, DARK_BUNDLE_FORBIDDEN_PURPLE,
                        "The %s compiled the dark-tuned purple %s. A darker purple is not the answer "
                        "to the dark panel - the answer is NO purple."
                        % (label, DARK_BUNDLE_FORBIDDEN_PURPLE),
                    )
                    self.assertEqual(
                        colour, dark_default,
                        "The %s compiled %s in the dark bundle instead of the default "
                        "for it, %s. For the stat value that default is stated by our own "
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

    def test_interactive_link_token_clears_wcag_aa_on_light_and_dark_surfaces(self):
        """The --link-color content-link token clears WCAG AA against the panel in both schemes.

        Content links read the :root --link-color custom property (emitted from $o-main-link-color /
        $link-color). On white the AA teal #007F8E is 4.74:1; on the dark panel #111B1E it is only
        3.69:1, so the dark arm retints the link to a lighter teal (#4FD4E2).
        """
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
                "dark arm (product value %s) instead of the light AA teal."
                % (link_colour, arm, surface, ratio, WCAG_AA_NORMAL_TEXT, DARK_LINK_REF),
            )

    def test_navbar_menu_entry_text_is_opaque_for_aa_on_the_teal_navbar(self):
        """A resting navbar menu-entry renders opaque white text, not a .9-alpha composite.

        The navbar teal is scheme-invariant, so this is not a dark-only defect. Core paints the
        resting entry text `var(--NavBar-entry-color, #{$o-navbar-entry-color})` with
        $o-navbar-entry-color = `rgba($o-white, .9)`, which composites to ~#E6F2F4 over the #007F8E
        bar: ~4.15:1, below AA. The entry-text token must render opaque #FFFFFF (4.74:1).

        The opacity is asserted on the resolved value's alpha: _normalize_colour drops alpha, so a
        contrast check alone would read the composite as an AA-passing #FFFFFF and never fail.
        """
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
            "surface is unstyled, so the opaque-entry guard cannot be verified - re-ground the "
            "element model.",
        )
        alpha = _alpha_of(raw_value)
        self.assertEqual(
            alpha, 1.0,
            "The resting navbar menu-entry text compiled to %r (alpha %.2f). At .9 opacity the "
            "white composites to ~#E6F2F4 over the teal bar (~4.15:1, below AA). The entry-text "
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

    def test_secondary_surfaces_flip_dark_in_the_dark_bundle(self):
        """Kanban canvas, settings sidebar and header, facet band and selected row are dark in dark.

        These secondary surfaces are painted from the gray ramp ($o-gray-100 / $o-gray-200) or a
        Bootstrap table variant. The dark ramp of dark_palette.scss makes the settings sidebar rung
        100 (#152225), the settings section header and the facet band rung 200 (#1D2D31); the kanban
        canvas takes $o-kanban-background and the selected row dark_secondary_surfaces.dark.scss.
        Each is asserted on the surface it renders on in the dark bundle and is proven not to be its
        light value.

        Contrast is asserted on the facet value text (WCAG AA) and the selected-row checkbox fill
        (WCAG non-text) on the darkened band. The row's --bs-table-bg is asserted only through those
        checks: "not the light info tint and independently readable" is the contract, and a row that
        stayed the light tint (#ccebfa) fails both. The light arm asserts the same surfaces stay
        light in web.assets_backend.
        """
        flat_brand_teal = self._assert_flat_teal_available()   # the selected-row checkbox fill #00BBCE
        light_gray_100 = "#f8f9fa"
        light_gray_200 = "#e9ecef"

        dark_css = self._compiled_css(DARK_BUNDLE)
        light_css = self._css()

        # Kanban canvas: .o_kanban_renderer --Kanban-background
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

        # Settings sidebar and section header
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
                "the dark gray ramp of dark_palette.scss did not reach core's gray-ramp literal."
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

        # Search facet resting band
        facet_band = {
            "classes": frozenset({"o_searchview_facet", "bg-200"}),
            "ancestors": FACET_PILL_ANCESTORS, "prev_sibling": frozenset(),
        }
        dark_facet = self._resolve_colour(
            dark_css, [facet_band], BACKGROUND_PROPS, "dark search-facet band"
        )
        self.assertEqual(
            dark_facet, DARK_FACET_BAND,
            "The search-facet resting band compiled to %s in the dark bundle instead of the gray "
            "rung 200 %s - the value text then sits on a light band at ~1.07:1."
            % (dark_facet, DARK_FACET_BAND),
        )
        self.assertNotEqual(
            dark_facet, light_gray_200,
            "The search-facet band is still the light grayscale %s in dark - the dark gray ramp "
            "did not reach .bg-200." % light_gray_200,
        )
        self.assertGreaterEqual(
            _contrast_ratio(DARK_READABLE_TEXT, dark_facet), WCAG_AA_NORMAL_TEXT,
            "The facet value text %s on the darkened band %s is %.2f:1, below WCAG AA %.1f:1."
            % (DARK_READABLE_TEXT, dark_facet, _contrast_ratio(DARK_READABLE_TEXT, dark_facet),
               WCAG_AA_NORMAL_TEXT),
        )

        # Selected list row (.table-info) and its checkbox
        table_info_row = {
            "classes": frozenset({"table-info", "o_data_row"}),
            "ancestors": TABLE_INFO_ROW_ANCESTORS, "prev_sibling": frozenset(),
        }
        dark_row = self._resolve_colour(
            dark_css, [table_info_row], ("--bs-table-bg",), "dark selected .table-info row"
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

    def test_selected_table_info_row_cells_paint_dark_band_not_light_accent(self):
        """A selected row's cells paint the dark selection band, not a light Bootstrap accent.

        Render-level companion to the --bs-table-bg row-token check in
        test_secondary_surfaces_flip_dark_in_the_dark_bundle: the row variable can be dark while the
        row still renders light. Bootstrap paints a table cell through
        `.table > :not(caption) > * > *` as three inherited-token layers:
        `background-color: var(--bs-table-bg)`, an opaque inset overlay
        `box-shadow: inset 0 0 0 9999px var(--bs-table-bg-state, ...)` and
        `color: var(--bs-table-color-state, ...)`. Core's `.table-info` fills them with a light info
        tint (#CCEBFA band, #C1DEEC overlay, near-black text), so the module overrides the cell
        itself in dark_secondary_surfaces.dark.scss and this guard resolves the cell's real layers.

        One rule addressed by type covers every `td` of the selected row (data cells, record
        selector, trailing cell). WCAG is asserted on the light row text (AA) and the teal selection
        checkbox (non-text) on the darkened band.
        """
        flat_brand_teal = self._assert_flat_teal_available()   # selected-row checkbox fill #00BBCE

        dark_css = self._compiled_css(DARK_BUNDLE)
        light_css = self._css()

        # The rule addresses every `td` of the selected row by its type, so it has no class on its
        # subject and the class-based resolver cannot model it: its declarations are read raw from
        # the compiled rule, which is the last one declared for that exact selector.
        cell_selector = ".o_list_table tr.o_data_row.table-info > td"

        def declared(css, prop):
            value = None
            for _order, selector, body in _iter_rules(css):
                if " ".join(selector.split()) == cell_selector:
                    for found, _important in _declarations(body, (prop,)):
                        value = found
            return value

        band = _normalize_colour(declared(dark_css, "background-color") or "")
        self.assertIsNotNone(
            band,
            "No dark rule paints every `td` of the selected row (%s): the trailing cell and any "
            "cell without a cell class would stay the light Bootstrap band." % cell_selector,
        )
        self.assertNotEqual(band, LIGHT_TABLE_INFO_BAND)
        self.assertEqual(band, DARK_TABLE_INFO_BAND)

        # The inset box-shadow overlay is painted ON TOP of the background, so it is what a light
        # accent actually shows through: it must be the dark band too.
        overlay = _normalize_colour(declared(dark_css, "box-shadow") or "")
        self.assertIsNotNone(overlay)
        self.assertNotEqual(overlay, LIGHT_TABLE_INFO_ACCENT)
        self.assertEqual(overlay, DARK_TABLE_INFO_BAND)

        text = _normalize_colour(declared(dark_css, "color") or "")
        self.assertIsNotNone(text)
        self.assertGreaterEqual(
            _contrast_ratio(text, band), WCAG_AA_NORMAL_TEXT,
            "The selected-row cell text %s on the dark band %s is %.2f:1, below WCAG AA %.1f:1."
            % (text, band, _contrast_ratio(text, band), WCAG_AA_NORMAL_TEXT),
        )
        self.assertGreaterEqual(
            _contrast_ratio(flat_brand_teal, band), WCAG_NON_TEXT_MIN,
            "The selection checkbox fill %s on the dark band %s is %.2f:1, below the WCAG "
            "non-text threshold %.1f:1." % (flat_brand_teal, band,
                                            _contrast_ratio(flat_brand_teal, band), WCAG_NON_TEXT_MIN),
        )

        # Non-leak: this dark-only rule must never be compiled into the LIGHT web.assets_backend.
        self.assertIsNone(
            declared(light_css, "background-color"),
            "The dark selected-row cell rule leaked into the LIGHT web.assets_backend bundle - "
            "dark_secondary_surfaces.dark.scss must stay dark-bundle only.",
        )

    def test_dark_faded_form_label_is_lifted_above_core_dim_default(self):
        """A faded (empty/readonly) form label is lifted above core's 0.66 opacity in dark.

        The faded label's base colour is #EDF4F5 because the module gives the general
        `.o_form_label` its own `color: var(--body-color)` in dark_secondary_surfaces.dark.scss; a
        bare label inherits #212529 from its `.text-900` cell. Core fades the empty/readonly/false
        variant with `opacity: 0.66`, which composites #EDF4F5 over the #111B1E sheet to #A2AAAC =
        7.41:1: above AA and AAA but perceptually dim next to a filled label (15.72:1). At 0.85 the
        composite is #CCD3D5 = 11.54:1.

        Asserted: (a) the dark bundle lifts the opacity strictly above core's 0.66 (the grounded
        literal CORE_FADED_LABEL_OPACITY, never the production value); (b) the composited label
        still clears WCAG AA on the dark sheet; (c) light mode keeps core's 0.66, the lift being
        dark-only.
        """
        faded_label = {
            "classes": frozenset({"o_form_label", "o_form_label_readonly"}),
            "ancestors": FORM_LABEL_ANCESTORS, "prev_sibling": frozenset(),
        }
        dark_css = self._compiled_css(DARK_BUNDLE)
        raw_opacity = _winning_declaration(dark_css, faded_label, ("opacity",))
        self.assertIsNotNone(
            raw_opacity,
            "No compiled `opacity` declaration applies to a faded (readonly) form label in the dark "
            "bundle - core's faded-label rule or the element model changed; re-ground.",
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

    def _resolve_colour_value(self, css, chain, raw):
        """Resolve a raw ``color`` / custom-property value to a normalised #rrggbb, or None.

        Follows ``var()`` through the ancestor ``chain`` (custom properties inherit, so ``--color``
        set on the ``.text-900`` cell is found there) and finally through ``:root``, which
        :func:`_matches_element` does not represent, via :meth:`_root_custom_prop_values`. Bounded so
        a self-referential var cannot spin.

        :return: the colour, or None when the value resolves to none
        """
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
        """Resolve the ``color`` an element computes, honouring CSS inheritance through ``chain``.

        ``color`` inherits, but a direct declaration on the element, even a normal one, beats any
        inherited value, since ``!important`` on an ancestor governs only that ancestor's own
        cascade. So the chain is walked innermost-first and the first element with a winning
        ``color`` is returned, resolving ``var()`` through the chain then ``:root``; when none
        declares ``color`` the ``:root --body-color`` is inherited.

        A single-element resolver would read only the label's own rules and report the dark body text
        #EDF4F5 while the live label inherits #212529 from its ``.o_cell.o_wrap_label.text-900``
        parent cell. Passing the cell in ``chain`` makes that dark-on-dark reversion observable.
        """
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
            "the inherited body-text chain the element relies on is missing; re-ground." % surface,
        )
        return _normalize_colour(body_colours[-1])

    def _general_form_label_chain(self):
        """The desktop general form label modelled with its real ``.text-900`` cell parent.

        chain[0] is the bare `<label class="o_form_label">`, chain[1] its
        `.o_cell.o_wrap_label.text-break.text-900` parent cell. The label's ancestor pool includes
        the cell classes because the cell is an ancestor; a generous pool only adds competitors.
        """
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
        """The general (non-faded) form label resolves a WCAG-AA colour in dark, never light #212529.

        Base-tier companion to test_dark_faded_form_label_*, which composites a hardcoded #EDF4F5 and
        so cannot notice the base colour reverting; this guard resolves the colour a plain
        `.o_form_label` computes through the real cascade in web.assets_web_dark.

        The resolver walks a chain because the label is a bare `<label class="o_form_label">` whose
        parent cell carries `text-900`, compiled to `color: var(--color) !important` with `--color` =
        #212529 ($o-gray-900), which the dark palette does not flip. With no colour of its own the
        label inherits that #212529: 1.14:1 on the dark sheet #111B1E. The module gives the label its
        own `.o_form_view .o_form_label { color: var(--body-color) }` (#EDF4F5, 15.72:1), a direct
        declaration that beats the inherited value without !important. The effective colour is
        resolved cascade-faithfully, so a muted tier of its own would still pass as long as it clears
        AA and is not #212529: the guard protects the contract, not a literal. The light arm asserts
        the label stays #212529 in web.assets_backend, where the override file is absent.
        """
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
            "override is dark-bundle only); it resolved %s." % (LIGHT_BODY_TEXT, light_eff),
        )

    def test_dark_text_900_emphasis_surfaces_resolve_readable_not_light_default(self):
        """Every `.text-900` near-black emphasis surface reads light-on-dark in the dark bundle.

        Companion to the general-form-label guard, proving the class-wide `--color` re-point reaches
        beyond form labels. `.text-900` bakes `--color: RGBA(33,37,41,...); color: var(--color)
        !important` = $o-gray-900, #212529 in the light ramp and the dark body tier #EDF4F5 in the
        dark ramp of dark_palette.scss. It is applied to form-label cells, navbar apps-menu section
        titles, property labels, kanban column titles and animated numbers, all on the dark app
        surface.

        The kanban column title stands for the non-form-label surfaces: it carries `.text-900`
        directly, so its resolved `color` must clear WCAG AA on the dark kanban header and not be
        #212529. The light arm asserts the utility stays #212529 in web.assets_backend.
        """
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

    def test_debug_database_name_is_readable_on_the_teal_navbar(self):
        """The debug-mode database name renders readable on the teal navbar, not a dim <mark>.

        With env.debug on, core shows the DB name in the user-menu toggle as a bare `<mark>` inside
        `.o_user_menu .oe_topbar_name`. Bootstrap's <mark> paints a pale highlight fill
        (--bs-highlight-bg) and the text only inherits, so the name sinks into the teal navbar
        ($o-navbar-background #007F8E). The navbar is scheme-invariant, so the rule lives in
        web.assets_backend.

        Protected: the <mark> drops the highlight fill and paints an AA-clearing colour on the bar
        (opaque #FFFFFF is 4.74:1 on #007F8E).
        """
        css = self._css()
        raw_colour = _winning_topbar_mark_declaration(css, ("color",))
        self.assertIsNotNone(
            raw_colour,
            "No `.oe_topbar_name mark` colour rule compiled into web.assets_backend - the debug "
            "db-name <mark> is unstyled, so it inherits a dim colour on the teal navbar. "
            "brand_cascade.scss must paint it.",
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

    def test_dark_mobile_burger_sidebar_is_a_dark_surface_so_its_text_clears_aa(self):
        """The mobile burger / app-menu sidebar is a dark panel in dark mode, not a white island.

        Core declares every colour of this component as an `!default` light literal in
        burger_menu.variables.scss and consumes them directly: panel `$o-burger-base-bg: $o-white`,
        topbar `$o-burger-topbar-bg: $o-gray-100`, entry text `$o-burger-base-color: $o-gray-800` at
        .8 alpha and topbar text `$o-burger-topbar-color: $o-black`. None is reachable from the
        $body-*-bg neutrals, so the panel recompiles white in web.assets_web_dark while everything
        drawn on it recompiles for a dark backdrop: the `web.SectionMenu` section titles
        (`fw-bolder text-900 pt-3 pb-2`) compute the dark #EDF4F5 on white = 1.11:1.

        The panel, not the title, is the assertion subject. Contrast is satisfiable by darkening the
        panel or by reverting the title to near-black, and the second leaves a white panel in dark
        mode and the panel's non-.text-900 text (`.text-body` user-menu links, the li/button rows)
        broken. So each surface is asserted to be its dark tier and not core's light literal, and
        readability is measured against the resolved panel, never a hardcoded backdrop. The
        $o-burger-* block at the end of dark_palette.scss makes all pass.

        The entry-row composite is green in both the fully light and fully dark state (core's light
        island is internally consistent at 6.23:1); it guards the dangerous partial change of
        darkening the panel while leaving `$o-burger-base-color` at $o-gray-800, which composites
        rgba(52,58,64,.8) to #3E454C on #111B1E = 1.80:1.

        The light arm asserts all four tokens keep core's values in web.assets_backend, since
        dark_palette.scss contributes to web.assets_web_dark alone.

        Model scope: the panels are portalled to `body`, so the ancestor pool is the panel root
        alone; the app-menu sidebar stands for both panels, which compile from the same selector
        group. Menu rows are bare `<li>`/`<button>`, read through
        :func:`_winning_burger_entry_declaration`.
        """
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

        # The panel surface itself
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

        # The section title, measured on the resolved panel
        dark_title = self._effective_label_colour(
            dark_css, [section_title, panel], "dark burger sidebar section title"
        )
        title_ratio = _contrast_ratio(dark_title, dark_panel)
        self.assertGreaterEqual(
            title_ratio, WCAG_AA_NORMAL_TEXT,
            "The `web.SectionMenu` sidebar section title resolves %s on the burger panel %s = "
            "%.2f:1, below WCAG AA %.1f:1. This is the 1.11:1 failure: the `.text-900` "
            "emphasis re-point gives the title the dark body tier while core keeps the panel white."
            % (dark_title, dark_panel, title_ratio, WCAG_AA_NORMAL_TEXT),
        )

        # The panel's own menu rows (li/button), at core's .8 alpha
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

        # The topbar band above the panel
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

        # Light arm: the panel stays white-with-dark-text (dark-bundle-only change)
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
            msg="The light burger menu rows must keep core's .8 alpha arm; "
                "%r carries a different opacity." % light_entry_raw,
        )

    def test_text_secondary_utility_is_readable_in_both_schemes(self):
        """`.text-secondary` clears WCAG AA in both schemes and moves nothing else.

        Bootstrap derives the text utility from $theme-colors, and Odoo's backend re-declares
        `$secondary: $gray-300` because the same token paints the surface tier, so `.text-secondary`
        compiles to #DEE2E6: 1.30:1 on white, invisible. Odoo's own frontend keeps stock $gray-600.

        The obvious fix, flipping the shared `$secondary` to $gray-600, would repaint the whole
        surface tier: the `border-secondary` hairlines across mail/Discuss and every `.bg-secondary` /
        `.text-bg-secondary` chip, whose color-contrast() foreground would flip from black to white.
        The rule under guard is therefore two-sided: the text tier is readable and the shared
        `--secondary-rgb` surface token stays where core put it, `$gray-300` (#DEE2E6 in light, the
        dark ramp's rung 300 #25383C in dark), never the muted-text rung #8EA5A8 the text tier takes.

        Dark is not free: #6C757D is only 3.73:1 on the dark panel, so the token needs its own dark
        arm (#8EA5A8, 6.75:1).
        """
        element = {
            "classes": TEXT_SECONDARY_CLASSES, "ancestors": TEXT_SECONDARY_ANCESTORS,
            "prev_sibling": frozenset(),
        }
        arms = (
            ("light", BACKEND_BUNDLE, WHITE, CORE_SECONDARY_RGB),
            ("dark", DARK_BUNDLE, DARK_BODY_BG, DARK_SECONDARY_RGB),
        )
        for arm, bundle_name, surface, surface_rgb in arms:
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

            # The surface tier must not move with it. `--secondary-rgb` is the shared :root token
            # .bg-secondary / .border-secondary / .text-bg-secondary all read.
            surface_tokens = [
                value.replace(" ", "")
                for value in self._root_custom_prop_values(css, "secondary-rgb")
            ]
            self.assertTrue(
                surface_tokens,
                "No :root --secondary-rgb is emitted in %s, so this guard cannot prove the surface "
                "tier is untouched. Re-ground it against the token Bootstrap uses."
                % bundle_name,
            )
            self.assertEqual(
                surface_tokens[-1], surface_rgb,
                "The shared --secondary-rgb surface token compiled to %r instead of core's %r in "
                "%s. `$secondary` itself was flipped: that fixes the text but also repaints every "
                ".bg-secondary chip and the .border-secondary hairlines across mail/Discuss, and "
                "flips .text-bg-secondary's color-contrast() foreground. Correct the TEXT tier "
                "only (the $o-viin-text-secondary token)."
                % (surface_tokens[-1], surface_rgb, bundle_name),
            )

    def test_dark_neutral_button_is_a_dark_pill_and_the_light_one_is_untouched(self):
        """In dark mode `.btn-secondary` is a dark pill, and light mode does not move.

        Core keys the neutral button off the gray ramp ($o-gray-300 fill, $o-gray-900 label). Under
        the dark ramp of dark_palette.scss that pair is a dark fill under a light label; a light-grey
        pill with a #212529 label on the #0B1315 canvas is the regression guarded (pager arrows, the
        resting chatter "Log note" / "Activity" toggles, the control-panel custom buttons).

        Asserted is the behaviour, not a hex: the fill is darker than its own label and the pair
        clears AA, which core's light pill fails on both halves.

        The non-regression half is the real risk. The module merges one key into
        $o-btns-bs-override, a map read by more than `.btn-secondary`: a plain assignment instead of
        map-merge would wipe the AA-teal "primary" entry and hand `.btn-primary` back to the flat
        2.33:1 decorative teal, asserted in both bundles.

        The active-step keys (`--o-statusbar-background-active` / `--o-statusbar-border-active`) are
        not asserted identical across bundles: forwarding light's #C6EDF1 into dark would put a
        glaring cyan slab under a 1.25:1 white label, and a parity check cannot see that because it
        compares the bundles to each other, never to a surface. That requirement is measured in
        test_dark_statusbar_current_step_is_a_dark_surface_with_a_readable_label. The hover key is
        this map's own state and stays here. The stat-button border/hover and the mobile stat-strip
        divider read the separate $o-btns-bs-OUTLINE-override map, with its own guards below.
        """
        dark_css = self._compiled_css(DARK_BUNDLE)
        light_css = self._compiled_css(BACKEND_BUNDLE)
        pager = {
            "classes": PAGER_PREVIOUS_CLASSES, "ancestors": PAGER_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        # Light arm: unchanged, so the dark assertions below are a real delta.
        light_fill = self._resolve_colour(
            light_css, [pager], BACKGROUND_PROPS, "light .btn-secondary fill"
        )
        self.assertEqual(
            light_fill, CORE_LIGHT_BTN_SECONDARY_BG,
            "The LIGHT `.btn-secondary` compiled to %s instead of core's %s. The dark arm must not "
            "leak into web.assets_backend - dark_buttons.scss is contributed to the dark bundle "
            "ONLY." % (light_fill, CORE_LIGHT_BTN_SECONDARY_BG),
        )

        # Dark arm: a dark pill with a readable light label.
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

        # Non-regression: the AA-teal primary button survives the map-merge.
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

        # The statusbar also reads `hover-background` from the same entry, so the neutral pill's
        # hover fill is the hovered step too: dark in the dark bundle, core's light grey in the
        # light one; a near-white hover under the dark step label (#EDF4F5) would be ~1.25:1.
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

    def test_list_group_header_name_renders_the_structure_purple_in_both_schemes(self):
        """A grouped-list group name renders the structure purple, readably, in both schemes.

        A group header is not an action but the structure the records were re-organised into, so it
        is the list-view counterpart of the purple group-by facet.

        Importance is the trap, twice over. Core stamps the name cell with `.text-black` when open or
        `.text-body` when folded, and both are `!important` (o-print-color emits
        `color: var(--color) !important`; Bootstrap's utility emits
        `color: rgba(var(--body-color-rgb), ...) !important`). Importance beats specificity and the
        two shapes resolve through different levers, so a fix that beats only one is a latent
        half-fix that shows when a user folds a group; both are asserted. Re-pointing either
        underlying token would be far too broad: `--color` is shared by every o-print-color utility
        and `--body-color-rgb` by the whole body text tier.
        """
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
                    "literal with its own class-wide dark re-point at (0,1,0); this cell's own rule "
                    "still has to win on its own terms, which is what this assertion checks.)" % label,
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
                    # No purple in dark. Unlike the group-by facet, this rule is not dropped in
                    # dark: that would hand the cell back to core's black-on-dark `.text-black`. The
                    # dark arm re-aims it at the bright body tier, asserted positively so deleting
                    # the @else arm is caught by more than the black refusal above.
                    self.assertNotIn(
                        colour, (expected_light_purple, DARK_BUNDLE_FORBIDDEN_PURPLE),
                        "The %s group name compiled the purple %s in the DARK bundle. The purple "
                        "accent is light-only." % (label, colour),
                    )
                    self.assertEqual(
                        colour, DARK_READABLE_TEXT,
                        "The %s group name compiled %s in the dark bundle instead of the bright "
                        "body-text tier %s. That is the default look, and it is the "
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

    def test_no_brand_purple_survives_anywhere_in_the_dark_bundle(self):
        """web.assets_web_dark contains no occurrence of either brand purple.

        The per-surface tests prove the named surfaces are purple-free in dark; this one is the rule
        itself, which catches the next purple rule added without the `@if not $o-viin-dark-bundle`
        wrapper and the core consumers nobody in this repo owns (the mobile form label, the
        search-panel section divider, the POS backend kanban) if the token re-point were removed.

        The purple is a brand hex, so it either appears in the compiled text or it does not. Both
        spellings the compiler emits are searched (the `#rrggbb` literal and the `r,g,b` triplet
        Odoo's `to-rgb()` produces for o-print-color) and both purples: the light #7F4282 (an
        unguarded rule) and the dark-tuned #B589B8 (a dark arm of the purple).

        Non-vacuous by construction: the same scan on the light bundle must find the purple, so a
        typo in the needle, a bundle that failed to build or a purple that disappeared from light too
        cannot make the dark half pass for the wrong reason.
        """
        light_purple = self._brand_secondary_ssot()
        needles = {
            "the LIGHT brand purple %s (an unguarded rule reached the dark bundle)" % light_purple:
                _colour_spellings(light_purple),
            "the dark-tuned purple %s (a dark arm of the purple exists)" % DARK_BUNDLE_FORBIDDEN_PURPLE:
                _colour_spellings(DARK_BUNDLE_FORBIDDEN_PURPLE),
        }

        # Control: the light bundle MUST still contain the light purple, or this scan proves nothing.
        light_css = self._compiled_css(BACKEND_BUNDLE).lower()
        self.assertTrue(
            any(spelling in light_css for spelling in _colour_spellings(light_purple)),
            "The brand purple %s does not appear in the compiled LIGHT bundle at all. Either the "
            "purple accent was removed from light too - light keeps it on the "
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
                # Report the offending rule, not just "found it", so the offending rule is locatable.
                start = dark_css.rfind("}", 0, index) + 1
                self.fail(
                    "web.assets_web_dark contains %s, spelled %r. The purple accent is LIGHT-MODE "
                    "ONLY : every rule painting it must sit inside "
                    "`@if not $o-viin-dark-bundle`, and $o-brand-secondary itself is re-pointed to "
                    "the neutral muted tier in dark_palette.scss for the core rules we cannot guard. "
                    "Offending rule: %s"
                    % (description, spelling, dark_css[start:index + 40].strip()),
                )

    def test_dark_statusbar_current_step_is_a_dark_surface_with_a_readable_label(self):
        """The current statusbar step carries a readable label on a scheme-appropriate fill.

        Ruled out: a bright near-white/cyan slab with a white label on a dark sale order (a white
        label on the light #C6EDF1 slab is 1.25:1), painfully bright against the #0B1315 canvas.

        The two halves have different causes, so the guard measures the pair. The fill is core's
        $o-component-active-bg = `mix($o-action, $o-gray-100, 20%)`, a light cyan tint no $body-*-bg
        override touches, so it recompiles verbatim into the dark bundle. The label is not the button
        map's `color` key: core renders the current step `disabled`, and Bootstrap's `button-variant`
        defaults --btn-disabled-color to `color-contrast($background)`, white once dark_buttons.scss
        made the resting fill dark.

        The dark arm is held to three measured properties rather than a hex: AA against its own
        label, lighter than the panel it sits on (a raised surface, not a hole) and within a modest
        contrast band of that panel (a surface tier, not a white slab). Light is pinned equal to
        core's #C6EDF1, so the dark half is a real delta.
        """
        light_css = self._compiled_css(BACKEND_BUNDLE)
        dark_css = self._compiled_css(DARK_BUNDLE)
        status_root = {
            "classes": frozenset({"o_statusbar_status"}), "ancestors": STATUSBAR_ANCESTORS,
            "prev_sibling": frozenset(),
        }

        # Light arm: pinned to core, so the dark assertions below are a delta.
        light_fill = self._resolve_colour(
            light_css, [status_root], ("--o-statusbar-background-active",),
            "light statusbar current-step fill",
        )
        self.assertEqual(
            light_fill, CORE_LIGHT_STATUSBAR_ACTIVE_BG,
            "The LIGHT statusbar current-step fill compiled to %s instead of core's %s. The light "
            "arm is pinned to core; the dark arm belongs in dark_palette.scss, which "
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

        # Dark arm: a raised dark SURFACE, not the light slab forwarded from core.
        dark_fill = self._resolve_colour(
            dark_css, [status_root], ("--o-statusbar-background-active",),
            "dark statusbar current-step fill",
        )
        self.assertNotEqual(
            dark_fill, CORE_LIGHT_STATUSBAR_ACTIVE_BG,
            "The dark statusbar current step still compiles core's LIGHT fill %s. That is the cyan "
            "slab: 14.0:1 against the %s panel, with a 1.25:1 white label on it."
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

    def test_stat_button_border_is_a_subtle_hairline_and_its_label_is_readable_in_both_schemes(self):
        """A smart button's border separates it without glaring, in both schemes.

        Core compiles every smart button as `oe_stat_button btn btn-outline-secondary` and expands
        $o-btns-bs-outline-override through the same `button-variant` mixin as the filled map (not
        Bootstrap's `button-outline-variant`), so its `border` key is a literal border colour. Core
        keys it to $o-gray-300: #DEE2E6 in the light ramp (13.45:1 against the #111B1E form sheet, a
        pure-white hairline round every stat button, if it ever stopped following the dark ramp) and
        the subtle #25383C in dark. The same map's `color` key (#212529) is what a stat button
        without the StatInfo template renders its bare `<span>` in: 1.14:1 on that sheet, invisible.

        "Subtle hairline" is a relationship, not a value: light mode's own border is 1.30:1 on white.
        Both arms are held to the same contrast band, so neither can drift into the other's failure
        mode, too faint to separate the buttons or bright enough to glare. The label is asserted
        together with the border because both come from one map entry, and a partial fix would leave
        a dark-on-dark label.
        """
        light_css = self._compiled_css(BACKEND_BUNDLE)
        dark_css = self._compiled_css(DARK_BUNDLE)

        # Light is pinned to core's own values.
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
                "The %s stat-button border %s is only %.2f:1 against the %s form sheet - it does "
                "not separate one smart button from the next."
                % (arm, border, ratio, panel),
            )
            self.assertLessEqual(
                ratio, SUBTLE_BORDER_MAX_CONTRAST,
                "The %s stat-button border %s is %.2f:1 against the %s form sheet - a glaring "
                "hairline, not a subtle one (light mode's own border is 1.30:1 on white). Point it "
                "at the dark $border-color tier, never at core's $o-gray-300."
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

    def test_stat_button_hover_keeps_every_label_it_carries_readable_in_both_schemes(self):
        """Hovering a smart button does not hide the text it carries, in either scheme.

        The collision is between two correct values. The hover fill is core's $o-gray-200 (#E9ECEF in
        light, the dark ramp's #1D2D31 in dark). The text on it is not the button's own
        --btn-hover-color: `.o_stat_text` and `.o_stat_value` both read --o-stat-text-color, which
        brand_cascade.scss pins to the dark body tier #EDF4F5 in dark. Dark text on a light hover
        fill would be 1.06:1. So the guard resolves every text token that can ride the hover fill
        and measures each against it: --btn-hover-color covers a plain `.btn-outline-secondary`
        elsewhere in the backend, --o-stat-text-color covers the stat value and label, which
        brand_cascade.scss routes through one property so they cannot drift apart.
        """
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

    def test_statusbar_steps_render_a_numbered_marker_that_inherits_its_step_label_colour(self):
        """Every statusbar step renders its ordinal, readably, in both schemes.

        Both schemes show a number per step, on core's arrow geometry.

        The colour assertion is an absence: statusbar_steps.scss paints the digit `currentColor`, so
        it inherits whatever the step's label resolves to, per step state and scheme. The guard
        asserts the marker declares no colour of its own (it would otherwise need its own contrast
        budget and dark arm) and measures the label pairs the digit inherits. Both step states are
        measured because they resolve through different tokens: the current step is `disabled`
        (--btn-disabled-color on the active fill) and every other step is a resting `.btn-secondary`
        (--btn-color on --btn-bg).

        The geometry half is required: `clip-path: none` on an arrow button turns core's chevron
        chain into rectangles, so the polygon must stay compiled and never be unset, in both
        bundles, scanned on the raw rules so no selector shape slips past the resolver. It overlaps
        viin_backend_theme's test_statusbar_steps_keep_cores_arrow_geometry on purpose: that one
        guards the theme, this one the module that ships the statusbar rule.
        """
        for bundle_name in (BACKEND_BUNDLE, DARK_BUNDLE):
            css = self._compiled_css(bundle_name)

            # The marker renders the ordinal from the data attribute.
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
                "numbers are simply not in the bundle."
                % bundle_name,
            )

            # It carries no colour of its own, so it inherits its step's label.
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

            # What it inherits clears AA on the step it sits in.
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

            # The readonly statusbar is held to the visibility floor rather than AA. sale.order /
            # account.move / purchase.order render every step `disabled` and core swaps the label
            # onto $text-muted, an alpha colour, so it is composited against the step fill before
            # measuring. Inactive components are exempt from WCAG SC 1.4.3, so the threshold is the
            # 3:1 non-text floor, which light mode already delivers (3.69:1). It is what makes
            # core's dark value fail: $o-main-color-muted is built from the gray ramp, so left there
            # it composites over the dark step #25383C below the floor and the upcoming stages
            # vanish.
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

            # Core's chevron geometry is untouched.
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
                "into a rectangle:\n  %s"
                % (bundle_name, "\n  ".join(unset)),
            )
            self.assertTrue(
                polygons,
                "No compiled rule in %s clips `.o_arrow_button` into a polygon, so the statusbar does "
                "not render Odoo CE's chevron steps at all." % bundle_name,
            )

    def test_the_statusbar_numbering_layer_declares_no_step_or_container_geometry(self):
        """`.o_statusbar_status` compiles with no padding/border/height of its own.

        Core's areItemsWrapping() (statusbar_field.js) folds the whole statusbar into a "..." dropdown
        as soon as `root.getBoundingClientRect().height > firstItem.getBoundingClientRect().height`,
        root being `.o_statusbar_status` and firstItem its first visible `.o_arrow_button`. Core gives
        the container `align-items: stretch` and no padding or border, so in a single unwrapped row
        every button is stretched to the container's content box and the two heights are equal by
        construction. Geometry on the container itself inflates `root`'s border-box beyond the
        stretched row and collapses every statusbar at every viewport width. A numbering layer
        contributed to `.o_arrow_button` cannot do that unless an edit starts touching the container.

        Asserted is inflation, not ownership and not a property name: the guard reads the compiled
        cascade of the whole backend bundle, so it cannot tell core's declarations from this
        cluster's, and asks about the outcome on the box: is `.o_statusbar_status` pinned to a size
        its own stretched row did not choose? Core's `hr` module declares `height: 100%` here
        (versions_timeline.scss), which is not inflation: a percentage resolves against the parent,
        sized by the same row. Extents are judged by :func:`_is_non_inflating_extent` (percentage
        <= 100%, `auto` and intrinsic keywords pass; an absolute length does not), `padding`/`border`
        by :func:`_is_zero_box_geometry`, where every non-zero length adds to the box. Treating any
        declared height as inflation would make the verdict depend on which unrelated core modules
        are installed.

        Resolving through the real cascade also catches a forbidden property landing via another
        file, a mixin or a shorthand. A real browser measurement would need font metrics this suite
        cannot supply, and the declared-geometry read needs no new infrastructure. `margin` is not
        checked: `getBoundingClientRect()` measures the border box, which margin sits outside of.
        """
        css = self._css()
        container = {"classes": frozenset({"o_statusbar_status"}), "ancestors": STATUSBAR_ANCESTORS}

        # Every literal property name that can add to `.o_statusbar_status`'s OWN border-box
        # height - longhand and shorthand both queried, since the cascade may resolve either.
        box_geometry_props = (
            "height", "min-height", "max-height", "line-height",
            "padding", "padding-top", "padding-bottom",
            "padding-block", "padding-block-start", "padding-block-end",
            "border", "border-top", "border-bottom",
            "border-width", "border-top-width", "border-bottom-width",
        )
        # An extent asks a different question from an additive box property - see
        # _is_non_inflating_extent - so the two are judged by their own predicates.
        extent_props = ("height", "min-height", "max-height")
        offenders = []
        for prop in box_geometry_props:
            value = _winning_declaration(css, container, (prop,))
            if value is None:
                continue
            inflates = (
                not _is_non_inflating_extent(value) if prop in extent_props
                else not _is_zero_box_geometry(value)
            )
            if inflates:
                offenders.append("%s: %s" % (prop, value))
        self.assertFalse(
            offenders,
            ".o_statusbar_status compiled %s. Each of these pins the container's own border-box "
            "to a size the stretched row of buttons did not choose, which is exactly the overflow "
            "collapse (areItemsWrapping() folds the whole bar into one dropdown at every width)."
            % "; ".join(offenders),
        )

    def _channels(self, hex_colour):
        """Return the (r, g, b) integer channels of a normalised ``#rrggbb`` colour."""
        return tuple(int(hex_colour[offset:offset + 2], 16) for offset in (1, 3, 5))

    def _dominant_channel(self, hex_colour):
        """Return the index (0=r, 1=g, 2=b) of the colour's strongest channel.

        A hue fingerprint that survives any lightening or darkening, so "danger is still red-ish,
        primary still teal-ish" can be asserted without pinning a hex ("lighten, do not hue-shift").
        """
        channels = self._channels(hex_colour)
        return channels.index(max(channels))

    def _assert_state_band_lightens_the_panel(self, band, label):
        """A dark-mode hover/selection band raises the panel, perceptibly but not into a slab.

        Core builds both bands from `rgba($black, .08)`, a darkening overlay that is a ~1.02:1 no-op
        on an already-dark panel, so the affordance vanishes. Any correct dark arm is lighter than
        the surface it sits on and lands inside the perceptibility band.
        """
        self.assertGreater(
            _relative_luminance(band), _relative_luminance(DARK_BODY_BG),
            "The %s band %s is DARKER than the dark panel %s. Core builds it from "
            "`rgba($black, .08)`, an overlay that darkens - a no-op "
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
        """A hovered or selected dropdown item renders readable text on a visible band.

        Core re-declares the four Bootstrap dropdown-link scalars in bootstrap_overridden.scss and
        only the first is semantic: `$dropdown-link-color: $o-main-text-color`, which
        dark_palette.scss already re-points. The other three are literals off the black ramp
        (`$black`, `rgba($black, .08)`, `$black`) that no surface or text override reaches, so they
        recompile unchanged into web.assets_web_dark. Bootstrap emits two of them as the runtime
        `--dropdown-link-hover-color` / `--dropdown-link-active-color` on `.dropdown-menu` (no prefix
        in Odoo), from where `.dropdown-item:hover` / `.active`, the core dropdown, webclient, the
        model-field-selector popover and the html_editor toolbars read them.

        Both halves are asserted because they fail differently: the token half catches a re-point
        that never happened, the end-to-end half a re-point that is outranked on the element that
        paints. The band is asserted as a direction (see
        :meth:`_assert_state_band_lightens_the_panel`): core's band darkens, invisible on a dark
        panel, so "must lighten" is the behaviour under guard.
        """
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
                "Bootstrap emits it on `.dropdown-menu`, so either the bundle did not build or "
                "core moved the token - re-ground this guard rather than deleting it." % prop,
            )
            colour = _normalize_colour(raw)
            self.assertIsNotNone(
                colour, "%s resolves to %r, which carries no colour." % (prop, raw),
            )
            self.assertNotEqual(
                colour, core_value,
                "%s still compiles core's %s in the DARK bundle. That is the dropdown-token mechanism: the "
                "scalar is a literal in bootstrap_overridden.scss, so a %s dropdown item renders "
                "black text on the #111B1E panel - 1.20:1, e.g. on the m2o autocomplete."
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
            "dark bundle (Bootstrap emits it on `.dropdown-menu`).",
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

        # Light is untouched: the override is contributed to web.assets_web_dark only, so core's own
        # near-black-on-white pair still compiles in web.assets_backend.
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
        """The highlighted m2o/m2m suggestion does not compile to black in the dark bundle.

        The autocomplete is the surface a runtime custom-property re-point can never reach: core
        reads the pair as raw compile-time Sass (`color: $dropdown-link-hover-color;
        background-color: $dropdown-link-hover-bg`) inside `.o-autocomplete .ui-menu-item >
        a.ui-state-active`. A fix that only set `--dropdown-link-hover-color` on some element would
        leave the active row #000000 on the #111B1E panel (1.20:1, the highlighted row of every
        many2one/many2many/one2many dropdown invisible) while the token-level test passed. Only
        re-pointing the Sass scalar fixes both, and only this rule-level assertion proves it did.
        """
        dark = self._compiled_css(DARK_BUNDLE)
        light = self._css()

        raw_foreground = _autocomplete_active_row_declaration(dark, ("color",))
        raw_background = _autocomplete_active_row_declaration(dark, BACKGROUND_PROPS)
        self.assertIsNotNone(
            raw_foreground,
            "No compiled rule paints the colour of `.o-autocomplete .ui-menu-item > a.ui-state-active` "
            "in the dark bundle. Core declares it in autocomplete.scss - re-ground this guard on "
            "the current structure rather than deleting it.",
        )
        self.assertIsNotNone(
            raw_background,
            "No compiled rule paints the background of the autocomplete active row in the dark "
            "bundle (core declares it in autocomplete.scss).",
        )
        foreground = _normalize_colour(raw_foreground)
        background = _normalize_colour(raw_background)
        self.assertNotEqual(
            foreground, BLACK,
            "The autocomplete active row compiles `color: %s` in the DARK bundle. That is core's "
            "$dropdown-link-hover-color ($black) read as compile-time "
            "Sass, and it is 1.20:1 on the #111B1E panel - the highlighted suggestion of every "
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
        """A hovered or selected list-group row is readable on a dark band in dark mode.

        bootstrap_overridden.scss keys the whole list-group interactive tier off values that cannot
        cross the scheme boundary: `$list-group-action-hover-color: $gray-900` (#212529) and
        `$list-group-active-color/-bg` = `$o-black` on `lighten(saturate(adjust-hue($o-info, 15),
        1.8), 50)`, a light pale-blue band. On the systray Activity/Messaging menu the row under a
        stationary pointer renders #212529 = 1.14:1, and `.active` renders black on a light band
        floating in the dark panel.

        The active band is asserted as a direction plus a ceiling rather than a hex, as for the
        dropdown tokens: light mode's own selected band sits only ~1.11:1 from its white page (hue,
        bold weight and marker carry "selected", never brightness), so the dark arm is held to the
        same order of magnitude and a forwarded light slab (13:1 on the panel) fails.
        """
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
            "($list-group-action-hover-color) - 1.14:1 on the panel, "
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
            "($o-list-group-active-color).",
        )
        self._assert_state_band_lightens_the_panel(active_bg, "list-group selected")
        ratio = _contrast_ratio(active_fg, active_bg)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "A selected list-group row renders %s on %s - %.2f:1, below the WCAG AA normal-text "
            "threshold of %.1f:1." % (active_fg, active_bg, ratio, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_grayscale_bg_utilities_flip_to_dark_surfaces(self):
        """`.bg-100` / `.bg-200` / `.bg-300` are dark surfaces in the dark bundle.

        The `.bg-N` utilities are cells of a grid core generates mechanically off the $o-grays ramp:
        `.bg-#{$-name}, .text-bg-#{$-name} { @include o-print-color($-color, background-color,
        bg-opacity) }`. The dark ramp of dark_palette.scss makes the three rungs dark surfaces in
        web.assets_web_dark; on the light rungs the command-palette footer strip (`.bg-100`) would
        carry the dark muted-text tier #8EA5A8 on #F8F9FA at 2.46:1.

        The pair is asserted, not the hex: both text tiers that legitimately sit on these surfaces,
        the body tier and the muted tier, must clear AA on whatever the surface resolves to. The
        muted tier is the stricter and the one the footer failed on.

        The class-wide re-point is safe because the `text-bg-*` pairs are a different class name and
        keep their own color-contrast() label, held by
        test_black_on_light_pill_exceptions_stay_black_on_light_in_the_dark_bundle.
        """
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
        """`.text-dark` / `.text-black` / `.bg-white` / `.bg-light` flip in dark mode.

        Same generated grid and root cause as the gray utilities, on the Bootstrap black/white and
        `light`/`dark` theme names: `.text-dark` bakes $o-gray-900 #212529 = 1.14:1 on the panel,
        `.text-black` bakes #000000 = 1.16:1, and `.bg-white` / `.bg-light` stay light islands on a
        dark canvas.

        A third, separate lever reads the near-black text: core wraps every `.btn-link.text-*` in
        `o-btn-link-variant($o-gray-600 !important, o-text-color($-name) or $-color !important)`,
        which emits a direct `color:` at specificity (0,2,0) with `!important`, not a custom
        property. It outranks `.text-dark`'s (0,1,0) `color: var(--color) !important` whatever
        `--color` holds: the mail-activity "Reschedule" toggler in the crm.lead list measured
        $o-gray-600 #6C757D = 3.73:1 at rest and would render #212529 = 1.14:1 on hover. A fix that
        only re-points the utility leaves it broken, so the resting and hovered arms are asserted
        separately.

        Core's design is preserved rather than flattened: `.btn-link.text-*` is muted at rest and
        contextual on hover, so the two states must differ as well as clear AA.
        """
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
                "panel, i.e. invisible. It is a compile-time literal off the grayscale ramp, like "
                "the .text-900 utility." % (utility, core_light),
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
            "- 3.73:1 on the #111B1E panel, as on the crm.lead list "
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
        """The outline-CTA label and the contextual text tiers have a dark arm that stays on hue.

        Two accent foregrounds tuned for a white page recompile into dark. (a) `.btn-outline-primary`:
        core ships no "primary" key in $o-btns-bs-outline-override, so the class falls through to
        `button-outline-variant($theme-colors["primary"])`, which sets `--btn-color: $color`
        verbatim. With $theme-colors["primary"] pinned to the AA teal #007F8E (4.74:1 on white) the
        label is 3.69:1 on the #111B1E panel: the "New" button of every form view and the kanban
        "Load more..." control. (b) $o-theme-text-colors, core's WCAG-tuning seam for
        `.text-{success,info,warning,danger}`: four values chosen to pass AA on white, 3.71-3.85:1
        on the dark panel (`.text-danger`, the cog-menu "Delete", is 3.76:1). The same map feeds the
        invalid-state indicators through `o-text-color()`, so it matters beyond the utility class.

        Semantic identity is asserted as a hue fingerprint, not a hex: the dominant RGB channel of
        core's light value must stay dominant in the dark arm ("lighten, do not hue-shift").
        """
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
        # The ring is read from `--btn-border-color`, not `border-color`: Bootstrap paints it with the
        # shorthand `border: var(--btn-border-width) solid var(--btn-border-color)`, which no
        # single-var resolver can unwrap, and the custom property is the token the override owns.
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
            "%s. The dark arm leaked out of web.assets_web_dark, or the outline-map key was "
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
        """The black-on-light colour pills keep their own pair, even in the dark bundle.

        The gray-utility and near-black-text re-points are class-wide on four background and two text
        utilities, the right altitude for those families. A later pass that also darkens `text-bg-*`,
        `.o_badge_color_N`, `.o_tag_color_N` or the calendar chips would leave their deliberately
        dark label on a now-dark chip. The pills are correct as shipped, carrying their own bg+text
        pair at 9.8:1, so the test pins the pair rather than a value: a light chip with a darker
        label clearing AA.

        The two shapes cover the two mechanisms core uses: `.o_tag.o_tag_color_N` goes through
        o-print-color on both axes (the same `--background-color` / `--color` properties the
        `.bg-white` / `.text-dark` re-points use, the closer call) and `.badge.o_badge_color_N` uses
        direct `!important` declarations. `.text-bg-300` is not one of them: it is core's own
        color-contrast() pairing on gray rung 300, which the dark ramp makes the dark chip #25383C
        with the light label color-contrast() picks, covered by
        test_text_bg_utilities_pair_a_readable_label_with_the_dark_ramp_chip.
        """
        dark = self._compiled_css(DARK_BUNDLE)
        pills = (
            ("`.o_tag.o_tag_color_1` (o-print-color on both axes)", TAG_PILL_CLASSES),
            ("`.badge.o_badge_color_1` (direct !important declarations)", BADGE_PILL_CLASSES),
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

    def test_text_bg_utilities_pair_a_readable_label_with_the_dark_ramp_chip(self):
        """`.text-bg-300` is the dark ramp's rung-300 chip (#25383C) with a label that clears AA.

        Core builds the `text-bg-N` family from the gray ramp and picks each label with
        `color-contrast()`, so under the dark ramp the chip is dark and the label light; in the light
        bundle it stays the light chip #DEE2E6 under a dark label."""
        for arm, bundle_name, chip_expected in (
            ("dark", DARK_BUNDLE, "#25383c"),
            ("light", BACKEND_BUNDLE, "#dee2e6"),
        ):
            css = self._compiled_css(bundle_name)
            element = {
                "classes": TEXT_BG_300_CLASSES, "ancestors": UTILITY_ANCESTORS,
                "prev_sibling": frozenset(),
            }
            chip = self._resolve_colour(css, [element], BACKGROUND_PROPS, ".text-bg-300 [%s]" % arm)
            label = self._resolve_colour(css, [element], ("color",), ".text-bg-300 [%s]" % arm)
            self.assertEqual(chip, chip_expected, ".text-bg-300 chip in the %s bundle" % arm)
            ratio = _contrast_ratio(label, chip)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                ".text-bg-300 renders %s on %s = %.2f:1 in the %s bundle, below WCAG AA %.1f:1."
                % (label, chip, ratio, arm, WCAG_AA_NORMAL_TEXT),
            )

    # Bootstrap's `*-secondary` theme-color family (`$secondary-text-emphasis` /
    # `$secondary-bg-subtle`), not the $o-brand-secondary brand purple covered above.
    def test_dark_text_secondary_emphasis_clears_wcag_aa_on_control_panel_ground(self):
        """A bare `.text-secondary-emphasis` label is readable on the dark control-panel ground.

        The label (Discuss's "Saved" status pill) renders on the dark control-panel ground, not on
        the light "subtle" band Bootstrap designed it for. Core compiles
        `.text-secondary-emphasis { color: var(--secondary-text-emphasis) }` (Odoo sets
        `$variable-prefix` to '', so the custom property carries no `bs-` prefix). Without a dark
        override `--secondary-text-emphasis` is Bootstrap's stock `shade-color($secondary, 60%)`, a
        darkened shade of a light grey ($secondary stays Odoo's backend `$gray-300` #DEE2E6 in every
        bundle), which is not legible on the dark panel. Dropping the `$secondary-text-emphasis`
        alias from dark_palette.scss restores that stock value.
        """
        element = {
            "classes": frozenset({"text-secondary-emphasis"}),
            "ancestors": frozenset(),
            "prev_sibling": frozenset(),
        }
        dark_css = self._compiled_css(DARK_BUNDLE)
        emphasis = self._effective_label_colour(
            dark_css, [element], "dark `.text-secondary-emphasis`",
        )
        ratio = _contrast_ratio(emphasis, DARK_BODY_BG)
        self.assertGreaterEqual(
            ratio, WCAG_AA_NORMAL_TEXT,
            "`.text-secondary-emphasis` resolves %s in %s - %.2f:1 on the dark control-panel "
            "ground %s, below WCAG AA %.1f:1. `$secondary-text-emphasis` still resolves through "
            "Bootstrap's stock `shade-color($secondary, 60%%)` default; dark_palette.scss must "
            "alias it onto the module's own dark secondary-text token."
            % (emphasis, DARK_BUNDLE, ratio, DARK_BODY_BG, WCAG_AA_NORMAL_TEXT),
        )

    def test_dark_secondary_ladder_moves_together_for_alert_and_list_group_item(self):
        """`.alert-secondary` and `.list-group-item-secondary` share the same dark ladder tokens.

        Both must resolve to the secondary-ladder tokens dark_palette.scss aliases and not drift onto
        two different values. Bootstrap wires both variants to the identical root custom properties
        (`--secondary-text-emphasis` / `--secondary-bg-subtle`), so an own-band AA check alone is not
        sensitive to the alias: Bootstrap's stock ladder pairs a light `tint-color()` band with a
        darkened `shade-color()` label, which is AA-consistent whatever the dark theme and would
        clear AA with the alias missing. What distinguishes the two states is which values the pair
        resolves to: the ladder is committed to tokens dark_palette.scss already declares for other
        dark surfaces ($body-secondary-color / $body-tertiary-bg). So both consumers are asserted
        against those exact tokens, which catches a partial fix (one consumer re-pointed, or the two
        landing on different values), and a direct cross-consumer equality closes the same gap
        independently of that SSOT read.
        """
        dark_css = self._compiled_css(DARK_BUNDLE)
        expected_text = self._dark_palette_var("$body-secondary-color")
        expected_bg = self._dark_palette_var("$body-tertiary-bg")

        alert = {
            "classes": frozenset({"alert", "alert-secondary"}),
            "ancestors": frozenset(), "prev_sibling": frozenset(),
        }
        list_item = {
            "classes": frozenset({"list-group-item", "list-group-item-secondary"}),
            "ancestors": frozenset(), "prev_sibling": frozenset(),
        }
        alert_text, alert_bg = self._resolve_secondary_own_band(
            dark_css, alert, "dark `.alert-secondary`",
        )
        item_text, item_bg = self._resolve_secondary_own_band(
            dark_css, list_item, "dark `.list-group-item-secondary`",
        )

        for label, text, background in (
            ("`.alert-secondary`", alert_text, alert_bg),
            ("`.list-group-item-secondary`", item_text, item_bg),
        ):
            ratio = _contrast_ratio(text, background)
            self.assertGreaterEqual(
                ratio, WCAG_AA_NORMAL_TEXT,
                "dark %s resolves text %s on its own band %s - %.2f:1, below WCAG AA %.1f:1."
                % (label, text, background, ratio, WCAG_AA_NORMAL_TEXT),
            )
            self.assertEqual(
                text, expected_text,
                "dark %s resolves its text-emphasis to %s, not dark_palette.scss's own "
                "$body-secondary-color %s - `$secondary-text-emphasis` is still Bootstrap's stock "
                "shade-of-a-light-grey default, never aliased to the module's dark token."
                % (label, text, expected_text),
            )
            self.assertEqual(
                background, expected_bg,
                "dark %s resolves its subtle band to %s, not dark_palette.scss's own "
                "$body-tertiary-bg %s - `$secondary-bg-subtle` is still Bootstrap's stock "
                "tint-of-a-light-grey default, never aliased to the module's dark token."
                % (label, background, expected_bg),
            )

        self.assertEqual(
            alert_bg, item_bg,
            "`.alert-secondary` and `.list-group-item-secondary` resolve DIFFERENT subtle "
            "backgrounds (%s vs %s) even though both key off the SAME root `--secondary-bg-subtle` "
            "custom property - the three ladder values must move together as one alias, never "
            "independently." % (alert_bg, item_bg),
        )

    def test_child_combinator_matches_a_direct_child_and_not_a_deeper_descendant(self):
        """A `>` rule reaches the element it was written for, and no element below it.

        Every guard in this cluster is only as true as the candidate rules the resolver selects, and
        a wrong candidate set yields a confident, precise, wrong number no contrast assertion can
        detect. `>` states a relation a flat ancestor pool cannot express, so a rule whose parent
        chain is not modelled is read as a plain descendant, handing a rule written for a direct
        child to anything nested below it, where the extra candidate can win on specificity.

        The live case: core cancels the placeholder's dimming with
        `.o-mail-Message-body > i.text-muted.opacity-75 { opacity: 100% !important }`. It must reach
        the `<i>` core renders directly inside the body and not a `.text-muted.opacity-75` nested
        deeper in the same body.

        Both directions are asserted because neither alone is enough: a resolver reading `>` as a
        descendant passes the first subTest and fails the second; one refusing `>` outright fails
        the first. The type half is pinned too: the selector carries an `i`, and a class-only element
        model skips the rule entirely, which made the placeholder guard measure the dimmed opacity
        the rule exists to cancel.
        """
        rule = ".o-mail-Message-body > i.text-muted.opacity-75"
        ancestors = frozenset({"o-mail-Message", "o-mail-Message-body", "o-discuss-text-body"})
        body = frozenset({"o-mail-Message-body", "position-relative", "py-2"})
        direct_child = {
            "classes": frozenset({"text-muted", "opacity-75"}), "ancestors": ancestors,
            "prev_sibling": frozenset(), "parent": body, "tag": "i",
        }
        # Same element, same ancestors, one level deeper: its parent is the rich-body wrapper, so
        # core's rule was not written for it.
        deeper = dict(direct_child, parent=frozenset({"o-mail-Message-richBody", "overflow-x-auto"}))
        untagged = dict(direct_child, tag=None)

        with self.subTest(relation="direct child"):
            self.assertTrue(
                _matches_element(rule, direct_child),
                "%r does not reach an `<i class='text-muted opacity-75'>` whose immediate parent is "
                "`.o-mail-Message-body` - the exact element core wrote it for. A "
                "resolver that cannot match it reports the placeholder at the dimmed opacity this "
                "rule exists to cancel, which is a measurement no contrast assertion can catch."
                % rule,
            )
        with self.subTest(relation="deeper descendant"):
            self.assertFalse(
                _matches_element(rule, deeper),
                "%r reaches an element nested BELOW `.o-mail-Message-body` rather than a direct "
                "child of it. `>` is a relation, not a decoration: read as a plain descendant it "
                "adds a candidate a browser never applies, and an added candidate can win on "
                "specificity and hand a guard a value the element never renders." % rule,
            )
        with self.subTest(relation="type selector, tag not modelled"):
            self.assertFalse(
                _matches_element(rule, untagged),
                "%r matched an element that declares no tag. A type-bearing rule must stay "
                "unmatched until the caller models the tag, or every class-only element in the "
                "cluster silently inherits rules written for one element type." % rule,
            )
