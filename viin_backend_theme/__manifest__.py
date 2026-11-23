# -*- coding: utf-8 -*-
{
    'name': "Viindoo Backend Shell",
    'summary': "Backend navigation, personalisation, typography and accessibility - inventions, never repaints",
    'description': """
Viindoo Backend Shell (viin_backend_theme)
===========================================
The backend SHELL layer on top of the Viindoo branding base (``viin_brand`` and
``viin_brand_mail``), which already own the de-brand and the purple chrome cascade. Every
capability here is an INVENTION Odoo 20 CE does not ship - none of it repaints an existing core
surface:

* the flat "Applications" home menu, and the apps-menu icon repurposed into its launcher
  (navigation);
* a density toggle and an appearance systray for the light/dark scheme switch, backed by a
  dedicated personalisation plugin (personalisation);
* Montserrat / Roboto typography, with the rich-text editor reverted to core's portable font
  stack so an outgoing mail body is never inlined with a face the recipient does not have
  (typography);
* a "Skip to main content" bypass-blocks link (accessibility);
* a pure-CSS loading skeleton (perceived-performance affordance).

It re-declares NO brand hex and owns NO color cascade: the purple chrome and the dark-mode
recompile live in ``viin_brand``, read from its brand-primary SSOT.
""",
    'author': "Viindoo",
    'website': "https://viindoo.com",
    'category': 'Hidden',
    'version': '0.1.2',
    'installable': True,
    'auto_install': True,
    'license': 'OPL-1',
    'old_technical_name': 'to_backend_theme',
    # mail is reached via viin_brand_mail: discuss_onboarding_patch.js patches mail's Discuss tour
    # and home_menu.js reads mail.activity for the header's activity count.
    'depends': ['web', 'viin_brand', 'viin_brand_mail'],
    # A server QWeb inherit on web.webclient_bootstrap rendered at boot, so it loads via 'data'.
    'data': [
        'views/webclient_templates.xml',
    ],
    'assets': {
        # Placed before core's primary_variables.scss and after viin_brand's brand_variables.scss in
        # the same bundle, so $o-brand-primary is defined when this file reads it.
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_backend_theme/static/src/scss/primary_variables.scss'),
        ],
        # No 'web._assets_backend_helpers' entry: the theme declares no radius override, every
        # surface inherits core's radius scale (guarded by tests/test_theme_radius_is_core.py).
        'web.assets_backend': [
            'viin_backend_theme/static/src/scss/fonts.scss',
            # mail's convert_inline bakes the editor's computed font-family into the saved mail body,
            # so the editor keeps core's portable system stack instead of the brand face.
            'viin_backend_theme/static/src/scss/editor_content_font.scss',
            'viin_backend_theme/static/src/scss/density.scss',
            # The $o-* Sass variables, $zindex-* and mixins come from web._assets_backend_helpers,
            # included at the top of this bundle, so file order here does not matter.
            'viin_backend_theme/static/src/webclient/apps_menu_home.scss',
            'viin_backend_theme/static/src/webclient/skip_link.scss',
            'viin_backend_theme/static/src/home_menu/home_menu.scss',
            'viin_backend_theme/static/src/webclient/app_icons.js',
            'viin_backend_theme/static/src/webclient/apps_menu_home.js',
            'viin_backend_theme/static/src/webclient/apps_menu_home.xml',
            'viin_backend_theme/static/src/webclient/webclient_patch.js',
            'viin_backend_theme/static/src/webclient/webclient.xml',
            # Rides web.assets_backend so it applies to the real webclient and to HttpCase suites:
            # core's Discuss tour opens Discuss first under the flat landing.
            'viin_backend_theme/static/src/webclient/discuss_onboarding_patch.js',
            'viin_backend_theme/static/src/home_menu/home_menu.js',
            'viin_backend_theme/static/src/home_menu/home_menu.xml',
            'viin_backend_theme/static/src/skeleton/skeleton.scss',
            # The scheme toggle persists (cookie and res.users.viin_color_scheme) then reloads,
            # because dark is a server-selected bundle that cannot be swapped without a reload.
            # Density is applied instantly.
            'viin_backend_theme/static/src/webclient/viin_theme_plugin.js',
            'viin_backend_theme/static/src/webclient/appearance_systray/appearance_systray.scss',
            'viin_backend_theme/static/src/webclient/appearance_systray/appearance_systray.js',
            'viin_backend_theme/static/src/webclient/appearance_systray/appearance_systray.xml',
        ],
        # The production JS/XML under test rides web.assets_backend, which web.assets_unit_tests_setup
        # includes; tours run in the browser through web.assets_tests, not in the headless runner.
        'web.assets_unit_tests': [
            'viin_backend_theme/static/tests/**/*',
            ('remove', 'viin_backend_theme/static/tests/tours/**/*'),
        ],
        'web.assets_tests': [
            'viin_backend_theme/static/tests/tours/**/*',
        ],
    },
}
