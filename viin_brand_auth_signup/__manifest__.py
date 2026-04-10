{
    'name': "Sign Up Debranding for Viindoo",
    'name_vi_VN': "Thương hiệu Viindoo cho mô-đun Đăng ký",

    'summary': """
Debranding Sign Up email templates for Viindoo""",
    'summary_vi_VN': """
Thay thế thương hiệu Odoo bằng Viindoo trong các mẫu email đăng ký
""",

    'description': """
What it does
============
This module replaces Odoo branding with Viindoo in auth_signup email templates
(new user invite, portal invite, password reset).


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
====================
Mô-đun này thay thế thương hiệu Odoo bằng Viindoo trong các mẫu email đăng ký
(mời người dùng mới, mời cổng thông tin, đặt lại mật khẩu).


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v18demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v18demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['auth_signup', 'viin_brand_mail'],

    'data': [
        'data/auth_signup_templates_email.xml',
    ],

    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
