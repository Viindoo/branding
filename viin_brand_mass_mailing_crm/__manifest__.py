{
    'name': "Mass Mailing On Lead / Opportunities Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Mass Mailing On Lead / Opportunities",

    'summary': """
Theme branding Viindoo for module Mass Mailing On Lead / Opportunities""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Mass Mailing On Lead / Opportunities
""",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in Mass Mailing On Lead / Opportunities following Viindoo's brand


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện các module Mass Mailing On Lead / Opportunities theo thương hiệu Viindoo


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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mass_mailing_crm'],

    # always loaded
    'data': [
        'data/mass_mailing_demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
