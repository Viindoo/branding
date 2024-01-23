{
    'name': "Stock Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Stock",

    'summary': """
Theme branding Viindoo for module Stock""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Stock
""",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in Stock following Viindoo's brand


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện các module Stock theo thương hiệu Viindoo


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
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'viin_brand_digest'],

    # always loaded
    'data': [
        'data/digest_data.xml',
        'views/res_config_settings_views.xml',
        'views/stock_orderpoint_views.xml',
        'views/stock_location_views.xml',
        'wizard/stock_immediate_transfer_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
