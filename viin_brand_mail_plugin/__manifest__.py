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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_mail_plugin?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['mail_plugin', 'viin_brand'],

    'data': [
        'data/ir_ui_menu_data.xml',
        'views/mail_plugin_login.xml',
    ],
    'uninstall_hook': 'uninstall_hook',
    'installable': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
