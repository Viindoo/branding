{
    'name': "Gamification Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Gamification",

    'summary': """
Theme branding Viindoo for module Gamification""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Gamification
""",

    'description': """
What it does
============
This module replaces Odoo branding with Viindoo in Gamification email templates.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này thay thế thương hiệu Odoo bằng Viindoo trong các mẫu email của module Gamification.


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v17demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v17demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1',

    'depends': ['gamification', 'viin_brand_mail'],

    'data': [
        'data/mail_template_data.xml',
    ],

    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
