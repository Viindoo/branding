{
    'name': "Viindoo Branding Onboarding",
    'name_vi_VN': "Tiến độ hướng dẫn với thương hiệu Viindoo",

    'summary': """
Debranding Onboarding for Viindoo
""",

    'summary_vi_VN': """
Làm lại Tiến độ hướng dẫn theo Thương hiệu Viindoo
        """,

    'description': """

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/18.0/viin_brand_onboarding?force_show=1",
    'live_test_url': "https://v18demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v18demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['viin_brand_common', 'onboarding'],
    'assets': {
        # Brand SCSS leaks into web.assets_unit_tests_setup / web.tests_assets because both bundles
        # carry ('include', 'web.assets_backend') (addons/web/__manifest__.py), so core's own
        # Hoot/QUnit unit tests were measuring Viindoo's design tokens instead of core's own. The
        # 'remove' below strips this module's own SCSS file back out of those two TEST-ONLY
        # bundles; web.assets_backend itself (the real webclient) is untouched - AssetPaths.remove()
        # operates on the accumulated per-bundle path list, not on the source bundle that
        # contributed it, so this is safe. A stale/renamed path here raises ValueError on module
        # update - keep that loud, never catch it
        # (odoo/addons/base/models/ir_asset.py AssetPaths._raise_not_found).
        # Specific to this module: onboarding.scss consumes $brand-primary-light/-dark/-darker and
        # $brand-secondary-light/-dark, which only viin_brand_common's primary_variables.scss
        # defines - and which these two test bundles no longer carry once viin_brand_common removes
        # its own primary_variables.scss from them. So this leak did not merely pollute core's
        # tests with Viindoo's design tokens, it ABORTED the compile of the whole bundle
        # ("Undefined variable: $brand-primary-light").
        'web.assets_unit_tests_setup': [
            ('remove', 'viin_brand_onboarding/static/src/scss/onboarding.scss'),
        ],
        # web.tests_assets is the legacy QUnit page (/web/tests/legacy, still executed by core's
        # WebSuite.test_qunit_desktop); it includes web.assets_backend the same way
        # web.assets_unit_tests_setup does, so it needs the identical remove entry.
        'web.tests_assets': [
            ('remove', 'viin_brand_onboarding/static/src/scss/onboarding.scss'),
        ],
        'web.assets_backend': [
            ('after', '/onboarding/static/src/scss/onboarding.scss', '/viin_brand_onboarding/static/src/scss/onboarding.scss'),
        ],
    },
    'installable': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
