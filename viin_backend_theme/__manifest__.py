# -*- coding: utf-8 -*-
{
    'name': "Viindoo Backend Shell",
    'summary': "Backend navigation, personalisation, typography and accessibility - inventions, never repaints",
    'description': """
Viindoo Backend Shell (viin_backend_theme)
===========================================
The backend SHELL layer on top of the Viindoo branding base (``viin_brand_web`` +
``viin_brand_mail``), which already own the de-brand and the AA teal chrome cascade. Every
capability here is an INVENTION Odoo 19 CE does not ship - none of it repaints an existing core
surface:

* the flat "Applications" home menu, and the apps-menu icon repurposed into its launcher
  (navigation);
* a density toggle and an appearance systray for the light/dark scheme switch, backed by a
  dedicated personalisation service (personalisation);
* Montserrat / Roboto typography, with the rich-text editor reverted to core's portable font
  stack so an outgoing mail body is never inlined with a face the recipient does not have
  (typography);
* a "Skip to main content" bypass-blocks link (accessibility);
* a pure-CSS loading skeleton (perceived-performance affordance).

It re-declares NO brand hex and owns NO color cascade: the AA teal chrome and the dark-mode
recompile live in ``viin_brand_web``, read from its brand-primary SSOT.
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
    # viin_brand reached transitively via viin_brand_web. mail reached via viin_brand_mail
    # (which depends on mail): discuss_onboarding_patch.js patches mail's Discuss tour, and
    # home_menu.js reads mail.activity for the header's activity count.
    'depends': ['web', 'viin_brand_web', 'viin_brand_mail'],
    # Server QWeb inherit on web.webclient_bootstrap (theme-owned): the density boot stamp
    # (data-viin-density on <html> for FOUC-free first render) + the pinch-to-zoom viewport override
    # (WCAG SC 1.4.4). This is a SERVER template rendered at boot, so it loads via 'data', not an OWL
    # asset bundle. The D16 login redesign was removed (owner: theme over-reach + blank on Chrome) -
    # login reverts to core Odoo, still de-branded by viin_brand.
    'data': [
        'views/webclient_templates.xml',
    ],
    'assets': {
        # Loads BEFORE core primary_variables.scss, and AFTER viin_brand_web's brand_variables.scss
        # (a dependency, so it is earlier in this same bundle) - so $o-brand-primary is already defined
        # when this file reads it. Adds ONLY the typography the base lacks.
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
        # ($o-border-radius / -sm / -lg in web/static/src/scss/primary_variables.scss, fed into
        # $border-radius* by core bootstrap_overridden.scss). Guarded by
        # tests/test_theme_radius_is_core.py - re-adding any radius declaration turns it RED.
        # C-5 (PR #658): the frontend (login) $primary de-brand lives in viin_brand_web (the web
        # de-brand owner), which re-points $theme-colors['primary'] to the AA teal on
        # web.assets_frontend as an OVERRIDABLE default. This theme contributes NOTHING to the public
        # frontend bundle: the D16 login redesign (login.scss split-screen) was removed (owner: theme
        # over-reach + blank login on Chrome), so login renders as core Odoo, de-branded by viin_brand.
        'web.assets_backend': [
            'viin_backend_theme/static/src/scss/fonts.scss',
            # D2 (owner, 2026-08-17): the brand heading font stops at the rich-text editor's edge.
            # mail's convert_inline bakes the editor's COMPUTED font-family into the saved mail body,
            # so a brand face in there is asserted on the RECIPIENT's mail client - which does not
            # have it (and neither do we yet: the woff2 subsets above are still pending). Puts the
            # editor's headings back on core's portable system stack. Pure cascade, no variable
            # override, so it cannot affect backend chrome.
            'viin_backend_theme/static/src/scss/editor_content_font.scss',
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
            # T-4 (PR #658): t-inherit web.WebClient to prepend the skip-link (home_menu.js's header
            # covers why it is no longer the shell's first Tab stop).
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
            # OWNER REVERT 2026-08-03 - TWO form-view surfaces went back to Odoo CE:
            #  * D6 statusbar->stepper (statusbar_field.{js,xml,scss,dark.scss}) is GONE. The owner
            #    wants core's ARROW/chevron statusbar back ("Cho state tren form view tao van muon
            #    giu cai mui ten nhu mac dinh"): the theme's `clip-path: none` + gap + numbered
            #    markers turned core's chevron chain into rectangles. Deleting the whole unit -
            #    rather than re-tuning it - is what restores core exactly; the brand-teal current
            #    arrow the owner DOES want is untouched, because it is painted by viin_brand_web
            #    through core's own --o-statusbar-border-active token, not by this theme.
            #  * D7 button-box stat strip (views/form/button_box/button_box.scss) is GONE. Its teal
            #    icon holder + uppercase label + border-0/gap reflow pushed the label outside the
            #    button and added a stray hairline rule. Core's default layout (icon left, label
            #    above value, inside the bordered box) is restored; the Viindoo purple stat TEXT
            #    stays, owned by viin_brand_web's --o-stat-text-color (light-only).
            # Guarded by tests/test_theme_core_chrome_untouched.py.
            # W3 unit-4 - skeleton (LAYOUT-only, ZERO Viindoo custom properties, TDD §4b
            # upgrade-safety NF2). Reads only the scheme-aware runtime props (--tertiary-bg /
            # --emphasis-color), so it needs no $o-* Sass helper and file order here is
            # irrelevant to compilation.
            # D15 skeleton (reusable pure-CSS skeleton shimmer; ViinSkeleton OWL component
            # deferred - see report).
            'viin_backend_theme/static/src/skeleton/skeleton.scss',
            # W4 unit-b - frontend dark-mode UX + appearance systray. NEW components + a service (NO new
            # patch()); all colors ride native unprefixed runtime props / $o-brand teal - ZERO --viin-*
            # custom properties.
            #  - viin_theme service (PR #658 T-1): the SCHEME toggle PERSISTS (color_scheme cookie +
            #    res.users.viin_color_scheme ORM write) then RELOADS - dark is the recompiled
            #    web.assets_web_dark bundle owned by viin_brand_web, which a server-selected bundle
            #    cannot swap without a reload. DENSITY stays INSTANT (dataset.viinDensity +
            #    viin_density cookie, no reload).
            'viin_backend_theme/static/src/webclient/viin_theme_service.js',
            #  - ViinAppearanceSystray: navbar systray dropdown (scheme + density), registry
            #    'systray' with explicit sequence.
            'viin_backend_theme/static/src/webclient/appearance_systray/appearance_systray.scss',
            'viin_backend_theme/static/src/webclient/appearance_systray/appearance_systray.js',
            'viin_backend_theme/static/src/webclient/appearance_systray/appearance_systray.xml',
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
