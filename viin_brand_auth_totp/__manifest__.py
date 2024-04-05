{
    'name': "Two-Factor Authentication Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Two-Factor Authentication",

    'summary': """
Theme branding Viindoo for module Two-Factor Authentication""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Two-Factor Authentication
""",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in module Two-Factor Authentication following Viindoo's brand


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện module Two-Factor Authentication theo thương hiệu Viindoo


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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['auth_totp'],

    # always loaded
    'data': [
        'views/user_perferences.xml',
        'views/templates.xml',
    ],
    'installable': False, # set auto_install True after upgrading for v17 after upgrading for v17
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
