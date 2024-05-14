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
    'website': " https://viindoo.com",
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['viin_brand_common', 'onboarding'],
    'assets': {
        'web.assets_backend': [
            ('after', '/onboarding/static/src/scss/onboarding.scss', '/viin_brand_onboarding/static/src/scss/onboarding.scss'),
        ],
    },
    'installable': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
