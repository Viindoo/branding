{
    'name': "Signup Authentication Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Signup Authentication",

    'summary': """
Theme branding Viindoo for module Signup Authentication""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Signup Authentication
""",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in module Signup Authentication following Viindoo's brand


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện module Signup Authentication theo thương hiệu Viindoo


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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['auth_signup'],

    # always loaded
    'data': [
        'data/mail_template_data.xml',
    ],
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
