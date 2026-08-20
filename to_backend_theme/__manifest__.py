# Copyright 2016, 2019 Openworx - Mario Gielissen
# Copyright 2012, 2019 Openworx - T.V.T Marine Automation
# Copyright 2019,2021 Viindoo
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Viindoo Backend Theme",
    "summary": "Mobile backend theme for Odoo community",

    "description": """
Backend theme for Viindoo, based on the Openworx Backend Theme

    """,

    'author': 'Openworx,T.V.T Marine Automation,Viindoo',
    'website': 'https://viindoo.com/apps/modules/18.0/to_backend_theme?force_show=1',
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    'category': 'Website/Theme/Backend',
    'version': '1.0.24',

    "depends": [
        'web',
        'web_editor',
        'web_responsive',
        'viin_brand_common',
    ],
    'images': [
        'static/description/main_screenshot.png'
    ],
    'assets': {
        'web.assets_backend': [
            ('after', 'web/static/src/views/form/form_controller.scss', 'to_backend_theme/static/src/views/form/form_controller.scss'),
            ('after', '/web_responsive/static/src/components/apps_menu/*', '/to_backend_theme/static/src/components/apps_menu/*'),
            ('after', '/web_responsive/static/src/components/apps_menu_item/*', '/to_backend_theme/static/src/components/apps_menu_item/*'),
            ('after', '/web_responsive/static/src/components/menu_canonical_searchbar/*', '/to_backend_theme/static/src/components/menu_canonical_searchbar/*'),
            'to_backend_theme/static/src/scss/style.scss',
            ('after', 'web/static/src/views/kanban/kanban_dashboard.scss', 'to_backend_theme/static/src/views/kanban/kanban_dashboard.scss'),
        ],
        'web.assets_backend_lazy': [
            ('after', 'web/static/src/views/pivot/pivot_view.scss', 'to_backend_theme/static/src/views/pivot/pivot_view.scss'),
        ],
        # to_backend_theme's own SCSS leaks into web.assets_unit_tests_setup / web.tests_assets via
        # web's ('include', 'web.assets_backend') + ('include', 'web.assets_backend_lazy')
        # (addons/web/__manifest__.py); each 'remove' strips it back out of the two TEST-ONLY
        # bundles so core's own Hoot/QUnit tests measure core's own theme metrics, not Viindoo's.
        # web.assets_backend / web.assets_backend_lazy themselves (the real webclient) are
        # untouched - AssetPaths.remove() operates on the accumulated per-bundle path list, not on
        # the source bundle. A stale/renamed path here raises ValueError on module update - keep
        # that loud, never catch it (odoo/addons/base/models/ir_asset.py AssetPaths._raise_not_found).
        'web.assets_unit_tests_setup': [
            ('remove', 'to_backend_theme/static/src/components/apps_menu/apps_menu.scss'),
            ('remove', 'to_backend_theme/static/src/components/apps_menu_item/apps_menu_item.scss'),
            ('remove', 'to_backend_theme/static/src/components/menu_canonical_searchbar/searchbar.scss'),
            ('remove', 'to_backend_theme/static/src/scss/style.scss'),
            ('remove', 'to_backend_theme/static/src/views/form/form_controller.scss'),
            ('remove', 'to_backend_theme/static/src/views/kanban/kanban_dashboard.scss'),
            ('remove', 'to_backend_theme/static/src/views/pivot/pivot_view.scss'),
        ],
        # web.tests_assets is the legacy QUnit page; it includes web.assets_backend +
        # web.assets_backend_lazy the same way, so it needs the identical remove list.
        'web.tests_assets': [
            ('remove', 'to_backend_theme/static/src/components/apps_menu/apps_menu.scss'),
            ('remove', 'to_backend_theme/static/src/components/apps_menu_item/apps_menu_item.scss'),
            ('remove', 'to_backend_theme/static/src/components/menu_canonical_searchbar/searchbar.scss'),
            ('remove', 'to_backend_theme/static/src/scss/style.scss'),
            ('remove', 'to_backend_theme/static/src/views/form/form_controller.scss'),
            ('remove', 'to_backend_theme/static/src/views/kanban/kanban_dashboard.scss'),
            ('remove', 'to_backend_theme/static/src/views/pivot/pivot_view.scss'),
        ],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': ['web'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'LGPL-3',
}
