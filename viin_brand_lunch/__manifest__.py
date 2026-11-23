{
    'name': "Lunch Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Ăn trưa",

    'summary': "This module brands Lunch with Viindoo: the section icons of the product search panel follow the Viindoo palette.",
    'summary_vi_VN': "Mô-đun này thay đổi giao diện Ăn trưa theo thương hiệu Viindoo: biểu tượng các nhóm ở bảng tìm kiếm của sản phẩm theo bảng màu Viindoo.",

    'description': """
What it does
============
This module brands Lunch with Viindoo: the section icons of the product search panel follow the Viindoo palette.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này thay đổi giao diện Ăn trưa theo thương hiệu Viindoo: biểu tượng các nhóm ở bảng tìm kiếm
của sản phẩm theo bảng màu Viindoo.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_lunch",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['lunch', 'viin_brand'],

    'data': [
        'views/lunch_product_views.xml',
    ],
    # 'demo': [],
    'assets': {
        'web.assets_tests': [
            'viin_brand_lunch/static/tests/tours/**/*',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
