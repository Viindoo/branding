{
    'name': "Stock Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Stock",

    'summary': "Theme branding Viindoo for module Stock",
    'summary_vi_VN': "Giao diện brand Viindoo cho module Stock",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in Stock following Viindoo's brand

Editions Supported
==================
1. Community Edition
2. Viindoo Cloud

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện các module Stock theo thương hiệu Viindoo

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Viindoo Cloud

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_stock?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.3',

    # viin_brand: owns the hook that hides the Enterprise upsell of the settings
    'depends': ['stock', 'viin_brand', 'viin_brand_digest'],

    'data': [
        'data/digest_data.xml',
        'views/stock_orderpoint_views.xml',
        'views/stock_location_views.xml',
        'views/stock_picking_type_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
