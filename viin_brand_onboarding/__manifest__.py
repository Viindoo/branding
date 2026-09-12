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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_onboarding?force_show=1",
    'live_test_url': "https://v18demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v18demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['viin_brand_web', 'onboarding'],
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
        # 19.0 NOTE: the 18.0 version of this comment said the leak ABORTED the bundle compile,
        # because 18.0's onboarding.scss read $brand-primary-light/-dark/-darker and
        # $brand-secondary-light/-dark from viin_brand_common's primary_variables.scss. The 19.0
        # port rewrote this stylesheet (0e696bc) and it now reads NO $brand-* variable at all, so
        # on this series the directive is about test HYGIENE only - core's Hoot/QUnit pages stop
        # measuring Viindoo's design tokens - not about a broken compile.
        # Forward-port gap: on 18.0 this was one arm of a sweep that also covered
        # viin_brand_common, viin_brand_mail, web_responsive and to_backend_theme. Of those, only
        # this module survives on 19.0 under the same name, so the brand SCSS shipped by
        # viin_brand_web / viin_backend_theme / viin_brand_mail still reaches core's test bundles.
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
