{
    'name': "Mail Discuss Debranding for Viindoo",
    'name_vi_VN': "Mail của Thảo luận với Thương hiệu Viindoo",

    'summary': """
Debranding Mail Discuss for Viindoo
    """,
    'summary_vi_VN': """
Làm lại mẫu mail của Thảo luận theo Thương hiệu Viindoo
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
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'viin_brand_common'],

    # always loaded
    'data': [
        'views/assets.xml',
        'views/mail_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
