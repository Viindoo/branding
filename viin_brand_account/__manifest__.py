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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_account?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['account', 'viin_brand', 'viin_brand_digest'],

    'data': [
        'data/digest_data.xml',
        'data/mail_template_data.xml',
        'views/account_move_views.xml',
        'views/account_bank_statement_views.xml',
        'views/partner_view.xml',
        'views/res_company_views.xml',
        'views/report_invoice.xml',
        'views/report_statement.xml',
        'views/terms_template.xml',
    ],
    'installable': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
