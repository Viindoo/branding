# Copyright 2016-2017 LasLabs Inc.
# Copyright 2017-2018 Tecnativa - Jairo Llopis
# Copyright 2018-2019 Tecnativa - Alexandre Díaz
# Copyright 2021 ITerra - Sergey Shebanin
# Copyright 2023 Onestein - Anjeel Haria
# Copyright 2023 Taras Shabaranskyi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Web Responsive",
    "summary": "Responsive web client, community-supported",
    "version": "18.0.1.0.11",
    "category": "Website",
    "website": "https://github.com/OCA/web",
    "author": "LasLabs, Tecnativa, ITerra, Onestein, "
    "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["web", "web_tour", "mail"],
    "development_status": "Production/Stable",
    "maintainers": ["Tardo", "SplashS"],
    "excludes": ["web_enterprise"],
    "data": [
        "views/res_users_views.xml",
    ],
    "assets": {
        "web._assets_primary_variables": {
            "/web_responsive/static/src/legacy/scss/form_variable.scss",
            "/web_responsive/static/src/legacy/scss/primary_variable.scss",
        },
        "web.assets_backend": [
            "web_responsive/static/src/lib/fuse/fuse.basic.min.js",
            "/web_responsive/static/src/legacy/scss/web_responsive.scss",
            "/web_responsive/static/src/legacy/scss/big_boxes.scss",
            "/web_responsive/static/src/legacy/scss/list_sticky_header.scss",
            "/web_responsive/static/src/legacy/js/web_responsive.esm.js",
            "/web_responsive/static/src/legacy/xml/form_buttons.xml",
            "/web_responsive/static/src/legacy/xml/custom_favorite_item.xml",
            "/web_responsive/static/src/components/apps_menu_tools.esm.js",
            "/web_responsive/static/src/components/apps_menu/*",
            "/web_responsive/static/src/components/apps_menu_item/*",
            "/web_responsive/static/src/components/menu_canonical_searchbar/*",
            "/web_responsive/static/src/components/menu_odoo_searchbar/*",
            "/web_responsive/static/src/components/menu_fuse_searchbar/*",
            "/web_responsive/static/src/components/menu_searchbar/*",
            "/web_responsive/static/src/components/navbar/*",
            "/web_responsive/static/src/components/webclient/*",
            "/web_responsive/static/src/components/hotkey/*",
            "/web_responsive/static/src/components/file_viewer/*",
            "/web_responsive/static/src/components/chatter/*",
            "/web_responsive/static/src/components/control_panel/*",
            "/web_responsive/static/src/components/command_palette/*",
            "/web_responsive/static/src/views/form/*",
        ],
        "web.assets_clickbot": [
            "/web_responsive/static/src/clickbot/clickbot.esm.js",
        ],
        # The checkbox-metrics reset is declared on BOTH test pages, because 18.0 runs both:
        # web.tests_assets is the legacy QUnit page (WebSuite.test_qunit_desktop) and
        # web.assets_unit_tests is the Hoot page (WebSuite.test_unit_desktop). The Hoot entry is
        # the load-bearing one - see the commit message for the A/B measurement.
        "web.tests_assets": [
            "/web_responsive/static/tests/qunit_reset.css",
        ],
        # Explicit file list only - never a glob over static/tests/**: an unresolved module id in
        # this shared bundle is a FATAL module-loader error that aborts the entire web unit-test
        # suite before any test body runs (see viin_brand_pos/static/tests/
        # navbar_favicon_guard.test.js:23-37 for a live-run-confirmed instance of this failure
        # mode).
        "web.assets_unit_tests": [
            "/web_responsive/static/tests/qunit_reset.css",
            "/web_responsive/static/tests/apps_menu.test.js",
            "/web_responsive/static/tests/apps_menu_search.test.js",
            "/web_responsive/static/tests/webclient.test.js",
        ],
    },
    "sequence": 1,
}
