{
    'name': "Mail Plugin Debranding for Viindoo",
    'name_vi_VN': "Plugin thư với Thương hiệu Viindoo",

    'summary': """
Debranding mail plugin for Viindoo software
    """,
    'summary_vi_VN': """
Làm lại plugin thư theo Thương hiệu Viindoo
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
    'website': "https://viindoo.com",
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['mail_plugin', 'viin_brand_common'],

    # always loaded
    'data': [
        'views/mail_plugin_login.xml',
    ],
    'installable': False, # set auto_install True after upgrading for v17 after upgrading for v17
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
