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
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.1',
    'depends': ['viin_brand', 'onboarding'],
    'assets': {
        # The brand SCSS is removed from the two test-only bundles that include
        # web.assets_backend, so core's Hoot and QUnit unit tests measure core's own design tokens.
        # A stale path here raises ValueError on module update: keep it loud, never catch it.
        'web.assets_unit_tests_setup': [
            ('remove', 'viin_brand_onboarding/static/src/scss/onboarding.scss'),
        ],
        # The legacy QUnit page /web/tests/legacy includes web.assets_backend the same way.
        'web.tests_assets': [
            ('remove', 'viin_brand_onboarding/static/src/scss/onboarding.scss'),
        ],
        'web.assets_backend': [
            ('after', '/onboarding/static/src/scss/onboarding.scss', '/viin_brand_onboarding/static/src/scss/onboarding.scss'),
        ],
    },
    'installable': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
