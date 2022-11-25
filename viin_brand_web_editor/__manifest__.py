{
    'name': "Viindoo Branding Web Editor",
    'name_vi_VN': "Web Editor với thương hiệu Viindoo",

    'summary': """
Debranding web editor for Viindoo software
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
    'depends': ['viin_brand', 'web_editor'],
    'data': [
    ],
    'assets' : {
        'web.assets_backend' : [
            ('after','web_editor/static/src/scss/web_editor.backend.scss','viin_brand_web_editor/static/src/scss/web_editor.backend.scss'),
        ],
    },
    'installable': False,
    'application': False,
    'auto_install': False, # set ['web_editor'] after upgrade 16.0
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
