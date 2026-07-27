# -*- coding: utf-8 -*-
{
    'name': "Viindoo Backend Theme",
    'summary': "Viindoo backend redesign: dark mode, vertical rail, home menu, mobile - additive on the branding base",
    'description': """
Viindoo Backend Theme (viin_backend_theme)
==========================================
A PURELY ADDITIVE Odoo 19 backend redesign layer on top of the Viindoo branding base
(``viin_brand_common`` + ``viin_brand_mail``), which already own the de-brand and the AA teal
chrome cascade. This theme adds ONLY what the base does not:

* an instant, no-reload dark mode (native ``[data-bs-theme]`` on Bootstrap's own ``--bs-*``);
* the always-dark vertical navigation rail and the flat "Applications" home menu (later waves);
* a mobile bottom navigation and a density toggle (later waves);
* Montserrat / Roboto typography.

It re-declares NO brand hex and re-implements NONE of the base cascade: the brand-primary SSOT is
read from ``viin_brand_common``. There is ZERO ``--viin-*`` parallel token system - Viindoo supplies
values to native Odoo ``$o-*`` / Bootstrap ``--bs-*`` levers only.
""",
    'author': "Viindoo",
    'website': "https://viindoo.com",
    'category': 'Hidden',        # not an app - a theme layer
    'version': '0.1',            # short-form, no series prefix (Viindoo Standard/Internal profile)
    'installable': True,
    'auto_install': True,        # the de-branded redesign is the unconditional default on every Viindoo 19 DB
    'license': 'OPL-1',
    # This module supersedes the legacy Viindoo backend theme `to_backend_theme` (which depended on
    # the OCA `web_responsive`, both dropped from the repo). `old_technical_name` carries the old
    # module's install state over to this one on upgrade - the standard Viindoo module-rename key.
    'old_technical_name': 'to_backend_theme',
    # viin_brand reached transitively via viin_brand_common; mail chrome (chat window etc.) via viin_brand_mail.
    'depends': ['web', 'viin_brand_common', 'viin_brand_mail'],
    # Server QWeb inherit on web.webclient_bootstrap (theme-owned): the density boot stamp
    # (data-viin-density on <html> for FOUC-free first render) + the pinch-to-zoom viewport override
    # (WCAG SC 1.4.4). This is a SERVER template rendered at boot, so it loads via 'data', not an OWL
    # asset bundle. The D16 login redesign was removed (owner: theme over-reach + blank on Chrome) -
    # login reverts to core Odoo, still de-branded by viin_brand.
    'data': [
        'views/webclient_templates.xml',
    ],
    'assets': {
        # Loads BEFORE core primary_variables.scss, and AFTER viin_brand_common's brand_variables.scss
        # (a dependency, so it is earlier in this same bundle) - so $o-brand-primary is already defined
        # when this file reads it. Adds ONLY the dark-surface rebinds + typography the base lacks.
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_backend_theme/static/src/scss/primary_variables.scss'),
        ],
        # NO 'web._assets_backend_helpers' entry, deliberately (owner revision 2026-08-03 "bo hết").
        # This theme used to append its own bootstrap_overridden.scss there to raise the Bootstrap
        # radius map (D13: $border-radius 0.5rem / -sm 0.375rem / -lg 0.75rem). That single override
        # is what made every button, card, input, modal, dropdown, popover, tooltip, alert and badge
        # rounder than Odoo CE, so the file was deleted rather than re-tuned: the cluster now owns
        # ZERO radius overrides and every surface inherits core's own scale
        # ($o-border-radius / -sm / -lg, web/static/src/scss/primary_variables.scss:218-220, fed into
        # $border-radius* by core bootstrap_overridden.scss:99-101). Guarded by
        # tests/test_theme_radius_is_core.py - re-adding any radius declaration turns it RED.
        # C-5 (PR #658): the frontend (login) $primary de-brand lives in viin_brand_common (the base
        # de-brand owner), which re-points $theme-colors['primary'] to the AA teal on
        # web.assets_frontend as an OVERRIDABLE default. This theme contributes NOTHING to the public
        # frontend bundle: the D16 login redesign (login.scss split-screen) was removed (owner: theme
        # over-reach + blank login on Chrome), so login renders as core Odoo, de-branded by viin_brand.
        'web.assets_backend': [
            'viin_backend_theme/static/src/scss/fonts.scss',
            # C-2 (PR #658): the no-reload dark layer (scheme.scss runtime [data-bs-theme] var flip +
            # the 426-line dark_surfaces.scss allow-list) is RETIRED. Dark now recompiles through
            # viin_brand_common/static/src/scss/dark_palette.scss on web.assets_web_dark (Option A
            # Layer 1), so core's own rules recompile dark-correct with no allow-list and no
            # !important war. The color-scheme correctness fix from scheme.scss moved to the base
            # (viin_brand_common/static/src/scss/color_scheme.scss).
            # W4 unit-b - density size rules ([data-viin-density] attribute-scoped, 44px/34px rows;
            # NO custom property, NO color). Attribute stamped by W4a boot + flipped by viin_theme.
            'viin_backend_theme/static/src/scss/density.scss',
            # W2 - D3 flat home menu (P1 WebClient landing + client action) + the apps-menu -> home
            # repurpose (PR #658 item 1: the flat home menu is the SOLE app switcher; the vertical rail
            # and the mobile bottom-nav are removed, and apps_menu_home.scss re-centres the repurposed
            # apps icon). SCSS uses only native $o-* / $primary levers + brand teal; all $o-* Sass vars,
            # $zindex-*, and mixins come from web._assets_backend_helpers, included at the top of this
            # bundle - so file order here is irrelevant to compilation.
            'viin_backend_theme/static/src/webclient/apps_menu_home.scss',
            # T-4 (PR #658): "Skip to main content" bypass-blocks link (visually hidden until focused).
            'viin_backend_theme/static/src/webclient/skip_link.scss',
            'viin_backend_theme/static/src/home_menu/home_menu.scss',
            'viin_backend_theme/static/src/webclient/app_icons.js',
            'viin_backend_theme/static/src/webclient/apps_menu_home.js',
            'viin_backend_theme/static/src/webclient/apps_menu_home.xml',
            'viin_backend_theme/static/src/webclient/webclient_patch.js',
            # T-4 (PR #658): t-inherit web.WebClient to prepend the skip-link as the first focusable node.
            'viin_backend_theme/static/src/webclient/webclient.xml',
            # PR #658 test-infra/onboarding adaptations to the theme's app-switcher repurpose + flat
            # home-menu landing (both must affect real runtime AND the HttpCase suites, so they ride
            # web.assets_backend). R1: make core's clickbot (lazy web.assets_clickbot) walk apps via the
            # home menu instead of the removed apps-menu <Dropdown>. R2: prepend a Discuss-open step to
            # core's discuss_channel_tour so the onboarding reaches Discuss under the flat landing.
            'viin_backend_theme/static/src/webclient/clickbot_home_menu.js',
            'viin_backend_theme/static/src/webclient/discuss_onboarding_patch.js',
            'viin_backend_theme/static/src/home_menu/home_menu.js',
            'viin_backend_theme/static/src/home_menu/home_menu.xml',
            # W3 unit-1 - form-view chrome (LAYOUT + native/cluster levers only, ZERO --viin-*):
            # D5 control panel, D11 notebook tabs.
            # SCSS reads $o-* / cluster teal from web._assets_backend_helpers (top of this bundle),
            # so file order here is irrelevant to compilation.
            #
            # OWNER REVERT 2026-08-03 - TWO form-view surfaces went back to Odoo CE:
            #  * D6 statusbar->stepper (statusbar_field.{js,xml,scss,dark.scss}) is GONE. The owner
            #    wants core's ARROW/chevron statusbar back ("Cho state tren form view tao van muon
            #    giu cai mui ten nhu mac dinh"): the theme's `clip-path: none` + gap + numbered
            #    markers turned core's chevron chain into rectangles. Deleting the whole unit -
            #    rather than re-tuning it - is what restores core exactly; the brand-teal current
            #    arrow the owner DOES want is untouched, because it is painted by viin_brand_common
            #    through core's own --o-statusbar-border-active token, not by this theme.
            #  * D7 button-box stat strip (views/form/button_box/button_box.scss) is GONE. Its teal
            #    icon holder + uppercase label + border-0/gap reflow pushed the label outside the
            #    button and added a stray hairline rule. Core's default layout (icon left, label
            #    above value, inside the bordered box) is restored; the Viindoo purple stat TEXT
            #    stays, owned by viin_brand_common's --o-stat-text-color (light-only).
            # Guarded by tests/test_theme_core_chrome_untouched.py.
            'viin_backend_theme/static/src/search/control_panel/control_panel.scss',
            'viin_backend_theme/static/src/core/notebook/notebook.scss',
            # W3 unit-2 - list + kanban chrome (LAYOUT + native/cluster levers only, ZERO --viin-*,
            # NO JS patch): D10 list chrome + bulk-selection bar, D9 kanban card. SCSS reads $o-* /
            # cluster teal from web._assets_backend_helpers (top of this bundle), so file order here
            # is irrelevant to compilation.
            'viin_backend_theme/static/src/views/kanban/kanban_record.scss',
            'viin_backend_theme/static/src/views/list/list_renderer.scss',
            'viin_backend_theme/static/src/views/view_components/selection_box.scss',
            # D10 - bulk bar t-inherit (adds the .o_viin_selection_bar hook the scss above tints).
            'viin_backend_theme/static/src/views/view_components/selection_box.xml',
            # W3 unit-4 - overlays + loading/skeleton + empty states (LAYOUT + native/cluster
            # levers only, ZERO Viindoo custom properties, NO JS patch on the overlay components -
            # TDD §4b upgrade-safety NF2). SCSS reads $o-* / cluster teal ($o-viin-chrome-base /
            # -deep) from web._assets_backend_helpers (top of this bundle) and the scheme-aware
            # UNPREFIXED runtime props scheme.scss flips, so file order here is irrelevant to
            # compilation.
            # D12 overlays (SCSS-only restyle of dialog/dropdown/popover/tooltip/notification/
            # command-palette surfaces, borders, radius + teal accents).
            'viin_backend_theme/static/src/core/dialog/dialog.scss',
            'viin_backend_theme/static/src/core/dropdown/dropdown.scss',
            'viin_backend_theme/static/src/core/popover/popover.scss',
            'viin_backend_theme/static/src/core/tooltip/tooltip.scss',
            'viin_backend_theme/static/src/core/notifications/notification.scss',
            'viin_backend_theme/static/src/core/commands/command_palette.scss',
            # D15 loading / skeleton (loading-indicator de-brand teal, brand-tinted BlockUI scrim,
            # reusable pure-CSS skeleton shimmer; ViinSkeleton OWL component deferred - see report).
            'viin_backend_theme/static/src/webclient/loading_indicator/loading_indicator.scss',
            'viin_backend_theme/static/src/core/ui/block_ui.scss',
            'viin_backend_theme/static/src/skeleton/skeleton.scss',
            # D14 empty states (token-only restyle of the core nocontent helper; own SVG set
            # deferred as a separate asset task).
            'viin_backend_theme/static/src/views/view_components/nocontent_helper.scss',
            # W4 unit-b - frontend dark-mode UX + appearance systray. NEW components + a service (NO new
            # patch()); all colors ride native unprefixed runtime props / $o-brand teal - ZERO --viin-*
            # custom properties.
            #  - viin_theme service (PR #658 T-1): the SCHEME toggle PERSISTS (color_scheme cookie +
            #    res.users.viin_color_scheme ORM write) then RELOADS - dark is the recompiled
            #    web.assets_web_dark bundle owned by viin_brand_common, which a server-selected bundle
            #    cannot swap without a reload. DENSITY stays INSTANT (dataset.viinDensity +
            #    viin_density cookie, no reload).
            'viin_backend_theme/static/src/webclient/viin_theme_service.js',
            #  - ViinAppearanceSystray: navbar systray dropdown (scheme + density), registry
            #    'systray' with explicit sequence.
            'viin_backend_theme/static/src/webclient/appearance_systray/appearance_systray.scss',
            'viin_backend_theme/static/src/webclient/appearance_systray/appearance_systray.js',
            'viin_backend_theme/static/src/webclient/appearance_systray/appearance_systray.xml',
        ],
        # T-3 (PR #658): dark arms for the theme's OWN widget surfaces that paint the AA teal
        # ($o-viin-chrome-base #007F8E) as FOREGROUND text - only 3.69:1 on the dark panel. These
        # .dark.scss files re-point ONLY that foreground teal to the base dark-mode teal
        # (--link-color) and are contributed EXPLICITLY to the recompiled dark bundle. They are NOT
        # auto-globbed: core's `web/static/src/**/*.dark.scss` glob (web/__manifest__.py) only covers
        # core's own tree, so a theme dark file must be listed here. A plain append lands AFTER the
        # web.assets_web include, so it wins on source order at equal specificity; being absent from
        # web.assets_backend, it never leaks the dark teal into light mode.
        # (statusbar_field.dark.scss was removed with the D6 stepper revert above - core's arrow
        # statusbar needs no dark arm from us: viin_brand_common's dark bundle recompiles it.)
        'web.assets_web_dark': [
            'viin_backend_theme/static/src/views/view_components/nocontent_helper.dark.scss',
            'viin_backend_theme/static/src/views/view_components/selection_box.dark.scss',
            'viin_backend_theme/static/src/core/notebook/notebook.dark.scss',
        ],
        # W5 - JS unit (Hoot) test files. The production JS/XML under test rides web.assets_backend
        # (included by web.assets_unit_tests_setup), so the viin_theme service + StatusBarField patch
        # + t-inherit template are live in the Hoot runtime. Tours are EXCLUDED here - they run in the
        # browser via web.assets_tests, not the headless unit runner.
        'web.assets_unit_tests': [
            'viin_backend_theme/static/tests/**/*',
            ('remove', 'viin_backend_theme/static/tests/tours/**/*'),
        ],
        # W5 - full-stack HttpCase tour files (driven by tests/test_tours.py).
        'web.assets_tests': [
            'viin_backend_theme/static/tests/tours/**/*',
        ],
    },
}
