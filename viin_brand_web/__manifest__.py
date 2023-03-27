{
    'name': "Viindoo Branding Web",
    'name_vi_VN': "Web với thương hiệu Viindoo",

    'summary': """
Debranding web for Viindoo software
""",

    'summary_vi_VN': """
Làm lại nhận diện thương hiệu theo Viindoo
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
    'live_test_url': "https://v15demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v15demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['viin_brand', 'web'],
    'data': [
    ],
    'assets' : {
        'web.assets_backend' : [
            'viin_brand_web/static/src/js/colors.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': ['web'],
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
