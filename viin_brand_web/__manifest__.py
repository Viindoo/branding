{
    'name': "Web Debranding for Viindoo",
    'name_vi_VN': "",

    'summary': """
Debranding Web Builder for Viindoo""",

    'summary_vi_VN': """
Làm lại màu sắc Bộ công cụ dựng web theo thương hiệu Viindoo
        """,

    'description': """

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_web?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/Viindoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # viin_brand is needed because the moved views/webclient_template.xml (brand_promotion_message
    # and login_layout) serves /viin_brand/static/img/viindoo_logo_tiny.png and .../favicon.ico -
    # the dependency edge follows the file that needs it, not the other way round.
    'depends': ['web', 'viin_brand'],
    'data': [
        'views/webclient_template.xml',
        'views/report_templates.xml',
        'views/res_users_views.xml',
    ],

    # always loaded
    'assets': {
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_brand_web/static/src/scss/brand_variables.scss'),
            # Plain APPEND (bundle tail), NOT anchored: guarantees it runs AFTER html_editor's
            # top-anchored html_editor.variables.scss (which BUILDS $o-color-palettes from the
            # brand-teal $o-enterprise-color) in either module load order, without depending on
            # html_editor/website or anchoring on a non-dependency file (which would ValueError
            # when that module is absent). Resets ONLY the CONTENT swatch base-1 o-color-1 (and
            # legacy `beta`) back to core aubergine; the guarded map-merge no-ops when the palette
            # was never built. See brand_palette_reset.scss for the full rationale + compile proof.
            'viin_brand_web/static/src/scss/brand_palette_reset.scss',
        ],
        # C-2 (PR #658): recompiled dark palette (Option A Layer 1). Positioned BEFORE core consumes
        # the Sass vars in the independent dark recompile, so every core rule - incl. those inside
        # color-contrast()/mix() and the compiled Bootstrap .text-*/.bg-* utilities - recompiles
        # dark-correct. The plain name (NOT *.variables.scss / NOT *.dark.scss) avoids the auto-glob
        # landmines; it is contributed EXPLICITLY only to this dark bundle. See dark_palette.scss.
        'web.assets_web_dark': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_brand_web/static/src/scss/dark_palette.scss'),
            # 2026-08-03: dark arm of the NEUTRAL button map ($o-btns-bs-override "secondary"),
            # anchored AFTER core's primary_variables.scss - the earliest point where
            # $o-component-active-bg/-border/-color exist, so the map's three ACTIVE keys can be
            # forwarded verbatim and the statusbar current-arrow + control-panel custom button stay
            # byte-identical. Still far ahead of the map's consumers (bootstrap_review_backend.scss
            # and the view SCSS). See dark_buttons.scss for the full rationale.
            ('after', 'web/static/src/scss/primary_variables.scss',
             'viin_brand_web/static/src/scss/dark_buttons.scss'),
            # FIX GROUP 1 (PR #658 review-fix): Layer-2 dark residue for secondary surfaces core
            # paints from a compile-time grayscale literal / runtime custom prop that no semantic
            # Sass var routes through (settings sidebar+section-header, search-facet band, selected
            # .table-info row). Kanban is handled by the dark_palette.scss $o-kanban-background var
            # override above. Plain APPEND lands after the web.assets_web include so it wins core on
            # source order; NOT auto-globbed (core's *.dark.scss glob only covers web/static/src/**),
            # so it is listed explicitly here and never leaks into the light bundle.
            'viin_brand_web/static/src/scss/dark_secondary_surfaces.dark.scss',
        ],
        # C-5 (PR #658): re-point the FRONTEND $theme-colors['primary'] to the AA teal AFTER
        # pre_variables.scss (where html_editor's palette-derived aubergine otherwise wins) and
        # before Bootstrap emits :root. web is a dependency, so the anchor is installability-safe.
        # See frontend_primary.scss for the full grounded leak analysis.
        'web.assets_frontend': [
            ('after', 'web/static/src/scss/pre_variables.scss',
             'viin_brand_web/static/src/scss/frontend_primary.scss'),
            # De-brand the PUBLIC error notifications. Core's counterpart
            # web/static/src/public/error_notifications.js ships _t("Odoo Session Expired") and
            # _t("Your Odoo session expired...") at 19.0. Ours RE-registers the same keys with
            # {force: true}, so it MUST evaluate after core's registration - a plain append (bundle
            # tail) is the only placement that guarantees that. Frontend, matching core's own
            # public/ surface.
            'viin_brand_web/static/src/core/errors/error_notifications.js',
            # PWA scoped-app install page. FRONTEND on purpose, and a deliberate CORRECTION to the
            # feature branch, which filed it under web._assets_core: core's web.webclient_scoped_app
            # (addons/web/views/webclient_templates.xml) loads only web.assets_frontend_minimal plus
            # web.assets_frontend_lazy and never a backend bundle, so on any backend bundle this
            # template extension would never load on the one page it targets.
            'viin_brand_web/static/src/core/install_scoped_app/install_scoped_app.xml',
        ],
        'web.assets_backend': [
            'viin_brand_web/static/src/core/dialog/dialog.js',
            'viin_brand_web/static/src/core/webclient/settings_form_view/widgets/res_config_edition.xml',
            # 2026-08-03 TEXT-LINK TIER (owner: links -> Viindoo secondary). Splits Bootstrap's
            # conflated link token: $link-color becomes the HYPERLINK colour (brand purple in LIGHT,
            # unchanged teal in dark), while the `.nav-link` / `.btn-link` / `.pagination` borrowers
            # are re-anchored onto the interactive teal so no BUTTON or TAB picks up purple.
            # ANCHORED, not appended - the file must land after core's bootstrap_overridden.scss
            # (which declares $link-color) and before Bootstrap's _variables.scss (which derives the
            # hover rung and the borrowers' defaults). The explicit anchor makes a core rename fail
            # LOUD via ir_asset.AssetPaths.index() instead of silently mis-ordering the cascade.
            # BACKEND-ONLY on purpose: web._assets_primary_variables is shared with
            # web.assets_frontend, so declaring it there would repaint the login + portal links too.
            ('before', 'web/static/lib/bootstrap/scss/_variables.scss',
             'viin_brand_web/static/src/scss/link_tier.scss'),
            # C-7 (PR #658): a11y focus-ring base. Shared --o-viin-focus token (light #005E68;
            # dark arm #7FE0EA via dark_palette.scss) applied on :focus-visible to core interactive
            # elements. Appended so it wins core's focus styles on equal-specificity source order.
            'viin_brand_web/static/src/scss/focus_ring.scss',
            # C-2 (PR #658): native color-scheme correctness (relocated from the theme's scheme.scss).
            # Scheme-invariant base fix for core's invalid `bright` color-scheme ident; owned by the
            # base so dark mode is correct even without the redesign theme.
            'viin_brand_web/static/src/scss/color_scheme.scss',
            # Anchored, NOT appended. brand_cascade.scss' `.o_progressbar .o_progress` rule is
            # (0,2,0) against core's identical (0,2,0) in progress_bar_field.scss, so it wins on
            # SOURCE POSITION alone (every other rule in the file pins a custom property and is
            # order-immune). A plain append leaves that silent race to module load order; the
            # explicit anchor makes the dependency fail LOUD instead - ir_asset.AssetPaths.index()
            # raises ValueError("File(s) ... not found in bundle ...") the moment core moves or
            # renames the target file.
            ('after', 'web/static/src/views/fields/progress_bar/progress_bar_field.scss',
             'viin_brand_web/static/src/scss/brand_cascade.scss'),
            # Eager side-effect module: reassigns the getColor/getColors exports of
            # web/static/src/core/colors/colors.js to the Viindoo brand (teal-first) palette so the
            # graph/pivot/dashboard charts stop rendering core's blue-first series. Must be eager
            # (a bare string entry is) and load before the LAZY graph/pivot/dashboard consumers,
            # which snapshot getColor at their own factory-eval time - this module loads at
            # def-index ~1257, before any of those views is opened. See the file header for the
            # transpiler snapshot mechanism and the journal-dashboard sparkline caveat.
            'viin_brand_web/static/src/core/colors/colors.js',
            # De-brand core's v19 error DIALOGS (web.SessionExpiredDialog, and the
            # WarningDialog/RedirectWarningDialog "Odoo Warning" title fallbacks). RE-HOMED here
            # from web._assets_core, a bundle key this module retired
            # (tests/test_asset_upgrade.py RETIRED_BUNDLE_KEYS). Plain appends are correct for both:
            # the .js only patch()es OWL prototypes and assigns static class fields, so it is
            # order-immune once the web.assets_web include at the top of this bundle has run; the
            # .xml carries t-inherit="web.SessionExpiredDialog" and so must simply share a bundle
            # with the component it extends. Grouped next to colors.js, the other eager core/
            # side-effect module.
            'viin_brand_web/static/src/core/errors/error_dialogs.js',
            'viin_brand_web/static/src/core/errors/error_dialogs.xml',
            # De-brand core's web.UpgradeDialog (the Enterprise-upsell dialog opened from any
            # `upgrade_boolean` field). RELOCATED here from the retired
            # `webclient/settings_form_view/` path (tests/test_asset_upgrade.py
            # RETIRED_ASSET_FRAGMENTS) so it no longer needs an allow-list entry. The .js also
            # closes PR #633 rebase verdict c2-common.md finding R-7: the template was de-branded
            # but the primary CTA still opened odoo.com - now patched to open viindoo.com instead.
            # Wordmark is "System" per owner decision D3. Both are plain appends, order-immune,
            # grouped with this module's other eager core/ side-effect modules.
            'viin_brand_web/static/src/core/upgrade_dialog/upgrade_dialog.js',
            'viin_brand_web/static/src/core/upgrade_dialog/upgrade_dialog.xml',
            'viin_brand_web/static/src/webclient/webclient.js',
            'viin_brand_web/static/src/webclient/user_menu_item.js',
            'viin_brand_web/static/src/views/widgets/**/*',
            # 2026-08-03: numbered steps on core's ARROW statusbar (owner: the step numbers went
            # missing in both schemes when the D6 stepper was reverted, but the chevrons must stay).
            # Additive only - a class + a `data-viin-step` attribute on core's existing button and a
            # `::after` ordinal; no DOM text, no geometry, no clip-path. Plain appends: the SCSS
            # selector (0,3,0) beats Bootstrap's `.btn` display (0,1,0) on specificity, not on
            # position, and the JS/XML are order-immune. Rides web.assets_backend (NOT a *.dark.scss
            # file) because the marker is painted with `currentColor` and needs no dark arm.
            'viin_brand_web/static/src/views/fields/statusbar/statusbar_steps.js',
            'viin_brand_web/static/src/views/fields/statusbar/statusbar_steps.xml',
            'viin_brand_web/static/src/views/fields/statusbar/statusbar_steps.scss',
        ],
        'web.assets_unit_tests': [
            'viin_brand_web/static/tests/dialog_debrand.test.js',
            'viin_brand_web/static/tests/action_dialog_debrand.test.js',
            'viin_brand_web/static/tests/documentation_link_debrand.test.js',
            'viin_brand_web/static/tests/user_menu_debrand.test.js',
            'viin_brand_web/static/tests/colors_debrand.test.js',
            # 2026-08-03: the statusbar step ORDINALS. A DOM-level guard, because the compiled-CSS
            # sibling cannot see whether the numbers are in reading order - the statusbar's DOM
            # order is the reverse of its visual order.
            'viin_brand_web/static/tests/statusbar_steps.test.js',
            # 2026-08-07: RED test-first guard for PR #633 rebase finding R-7 (web.UpgradeDialog
            # de-brand is only half done) + owner decision D3 (wordmark = "System"). Protects two
            # rules: the CTA must never open odoo.com, and the dialog copy must never carry the
            # Odoo/Viindoo wordmark. Authored before the production fix lands - see
            # upgrade_dialog_debrand.test.js's header for the static RED argument.
            'viin_brand_web/static/tests/upgrade_dialog_debrand.test.js',
            # 2026-08-08: RED test-first guard for BUG S13-1 + BUG S14-1 (rb633-accept-20260808-k4x9
            # acceptance report) + owner decision D3 (wordmark = "System" for the whole error/crash
            # dialog family). Protects: ClientErrorDialog/NetworkErrorDialog technical-details titles
            # must carry the "System " prefix (error_dialogs.js:16-17 currently drop "Odoo" instead
            # of prefixing "System"), and RPCErrorDialog's server-error message/traceback must never
            # leak core's raw "Odoo Server Error" string (no setup() override exists yet to normalize
            # it). Authored before the production fix lands - see error_dialogs_debrand.test.js's
            # header for the static RED argument.
            'viin_brand_web/static/tests/error_dialogs_debrand.test.js',
        ],
        'web.assets_tests': [
            'viin_brand_web/static/tests/tours/about_debrand_tour.js',
        ],
    },
    'images': [
        # 'static/description/main_screenshot.png'
        ],
    'installable': True,
    'post_load': 'post_load',
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
