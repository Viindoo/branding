{
    'name': "Viindoo Branding Common",
    'name_vi_VN': "Thiết kế với thương hiệu Viindoo",

    'summary': """
Frontend theme for Viindoo Branding
""",

    'summary_vi_VN': """
Chủ đề giao diện cho thương hiệu Viindoo
        """,

    'description': """
This module change some information for Viindoo branding

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô đun này thay đổi một vài thông tin dành riêng cho thương hiệu Viindoo

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_common?force_show=1",
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.3',
    'depends': ['viin_brand', 'web'],
    'data': [
        'views/ir_module_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/webclient_template.xml',
        'views/res_users_views.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_brand_common/static/src/scss/brand_variables.scss'),
            # Plain APPEND (bundle tail), NOT anchored: guarantees it runs AFTER html_editor's
            # top-anchored html_editor.variables.scss (which BUILDS $o-color-palettes from the
            # brand-teal $o-enterprise-color) in either module load order, without depending on
            # html_editor/website or anchoring on a non-dependency file (which would ValueError
            # when that module is absent). Resets ONLY the CONTENT swatch base-1 o-color-1 (and
            # legacy `beta`) back to core aubergine; the guarded map-merge no-ops when the palette
            # was never built. See brand_palette_reset.scss for the full rationale + compile proof.
            'viin_brand_common/static/src/scss/brand_palette_reset.scss',
        ],
        # C-2 (PR #658): recompiled dark palette (Option A Layer 1). Positioned BEFORE core consumes
        # the Sass vars in the independent dark recompile, so every core rule - incl. those inside
        # color-contrast()/mix() and the compiled Bootstrap .text-*/.bg-* utilities - recompiles
        # dark-correct. The plain name (NOT *.variables.scss / NOT *.dark.scss) avoids the auto-glob
        # landmines; it is contributed EXPLICITLY only to this dark bundle. See dark_palette.scss.
        'web.assets_web_dark': [
            ('before', 'web/static/src/scss/primary_variables.scss',
             'viin_brand_common/static/src/scss/dark_palette.scss'),
            # 2026-08-03: dark arm of the NEUTRAL button map ($o-btns-bs-override "secondary"),
            # anchored AFTER core's primary_variables.scss - the earliest point where
            # $o-component-active-bg/-border/-color exist, so the map's three ACTIVE keys can be
            # forwarded verbatim and the statusbar current-arrow + control-panel custom button stay
            # byte-identical. Still far ahead of the map's consumers (bootstrap_review_backend.scss
            # and the view SCSS). See dark_buttons.scss for the full rationale.
            ('after', 'web/static/src/scss/primary_variables.scss',
             'viin_brand_common/static/src/scss/dark_buttons.scss'),
            # FIX GROUP 1 (PR #658 review-fix): Layer-2 dark residue for secondary surfaces core
            # paints from a compile-time grayscale literal / runtime custom prop that no semantic
            # Sass var routes through (settings sidebar+section-header, search-facet band, selected
            # .table-info row). Kanban is handled by the dark_palette.scss $o-kanban-background var
            # override above. Plain APPEND lands after the web.assets_web include so it wins core on
            # source order; NOT auto-globbed (core's *.dark.scss glob only covers web/static/src/**),
            # so it is listed explicitly here and never leaks into the light bundle.
            'viin_brand_common/static/src/scss/dark_secondary_surfaces.dark.scss',
        ],
        # C-5 (PR #658): re-point the FRONTEND $theme-colors['primary'] to the AA teal AFTER
        # pre_variables.scss (where html_editor's palette-derived aubergine otherwise wins) and
        # before Bootstrap emits :root. web is a dependency, so the anchor is installability-safe.
        # See frontend_primary.scss for the full grounded leak analysis.
        'web.assets_frontend': [
            ('after', 'web/static/src/scss/pre_variables.scss',
             'viin_brand_common/static/src/scss/frontend_primary.scss'),
        ],
        'web.assets_backend': [
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
             'viin_brand_common/static/src/scss/link_tier.scss'),
            # C-7 (PR #658): a11y focus-ring base. Shared --o-viin-focus token (light #005E68;
            # dark arm #7FE0EA via dark_palette.scss) applied on :focus-visible to core interactive
            # elements. Appended so it wins core's focus styles on equal-specificity source order.
            'viin_brand_common/static/src/scss/focus_ring.scss',
            # C-2 (PR #658): native color-scheme correctness (relocated from the theme's scheme.scss).
            # Scheme-invariant base fix for core's invalid `bright` color-scheme ident; owned by the
            # base so dark mode is correct even without the redesign theme.
            'viin_brand_common/static/src/scss/color_scheme.scss',
            # Anchored, NOT appended. brand_cascade.scss' `.o_progressbar .o_progress` rule is
            # (0,2,0) against core's identical (0,2,0) in progress_bar_field.scss, so it wins on
            # SOURCE POSITION alone (every other rule in the file pins a custom property and is
            # order-immune). A plain append leaves that silent race to module load order; the
            # explicit anchor makes the dependency fail LOUD instead - ir_asset.AssetPaths.index()
            # raises ValueError("File(s) ... not found in bundle ...") the moment core moves or
            # renames the target file.
            ('after', 'web/static/src/views/fields/progress_bar/progress_bar_field.scss',
             'viin_brand_common/static/src/scss/brand_cascade.scss'),
            # Eager side-effect module: reassigns the getColor/getColors exports of
            # web/static/src/core/colors/colors.js to the Viindoo brand (teal-first) palette so the
            # graph/pivot/dashboard charts stop rendering core's blue-first series. Must be eager
            # (a bare string entry is) and load before the LAZY graph/pivot/dashboard consumers,
            # which snapshot getColor at their own factory-eval time - this module loads at
            # def-index ~1257, before any of those views is opened. See the file header for the
            # transpiler snapshot mechanism and the journal-dashboard sparkline caveat.
            'viin_brand_common/static/src/core/colors/colors.js',
            'viin_brand_common/static/src/webclient/webclient.js',
            'viin_brand_common/static/src/webclient/user_menu_item.js',
            'viin_brand_common/static/src/views/widgets/**/*',
            # 2026-08-03: numbered steps on core's ARROW statusbar (owner: the step numbers went
            # missing in both schemes when the D6 stepper was reverted, but the chevrons must stay).
            # Additive only - a class + a `data-viin-step` attribute on core's existing button and a
            # `::after` ordinal; no DOM text, no geometry, no clip-path. Plain appends: the SCSS
            # selector (0,3,0) beats Bootstrap's `.btn` display (0,1,0) on specificity, not on
            # position, and the JS/XML are order-immune. Rides web.assets_backend (NOT a *.dark.scss
            # file) because the marker is painted with `currentColor` and needs no dark arm.
            'viin_brand_common/static/src/views/fields/statusbar/statusbar_steps.js',
            'viin_brand_common/static/src/views/fields/statusbar/statusbar_steps.xml',
            'viin_brand_common/static/src/views/fields/statusbar/statusbar_steps.scss',
        ],
        'web.assets_unit_tests': [
            'viin_brand_common/static/tests/documentation_link_debrand.test.js',
            'viin_brand_common/static/tests/user_menu_debrand.test.js',
            'viin_brand_common/static/tests/colors_debrand.test.js',
            # 2026-08-03: the statusbar step ORDINALS. A DOM-level guard, because the compiled-CSS
            # sibling cannot see whether the numbers are in reading order - the statusbar's DOM
            # order is the reverse of its visual order.
            'viin_brand_common/static/tests/statusbar_steps.test.js',
        ],
    },
    'installable': True,
    'post_load': 'post_load',
    'auto_install': ['web'],
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
