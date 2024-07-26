{
    'name': "Invoicing Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Invoicing",

    'summary': """
Theme branding Viindoo for module Invoicing""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Invoicing
""",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in module Invoicing following Viindoo's brand


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện module Invoicing theo thương hiệu Viindoo


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
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'data/digest_data.xml',
        'views/account_move_views.xml',
        'views/account_bank_statement_views.xml',
        'views/partner_view.xml',
        'views/report_invoice.xml',
        'views/report_statement.xml',
        'views/terms_template.xml',
        'wizard/account_tour_upload_bill.xml'
    ],
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
