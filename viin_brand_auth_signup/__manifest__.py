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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_auth_signup?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.2',

    # any module necessary for this one to work correctly
    'depends': ['auth_signup'],

    # always loaded
    'data': [
        'data/mail_template_data.xml',
        'data/auth_signup_templates_email.xml',
    ],
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
