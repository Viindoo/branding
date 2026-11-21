{
    'name': "Lunch Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Ăn trưa",

    'summary': """
This module brands Lunch with Viindoo: the order mail sent to the supplier is powered by Viindoo.""",
    'summary_vi_VN': """
Mô-đun này thay đổi giao diện Ăn trưa theo thương hiệu Viindoo: thư đặt món gửi nhà cung cấp hiển
thị Viindoo ở chân thư.
""",

    'description': """
What it does
============
This module brands Lunch with Viindoo: the order mail sent to the supplier is powered by Viindoo.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này thay đổi giao diện Ăn trưa theo thương hiệu Viindoo: thư đặt món gửi nhà cung cấp hiển
thị Viindoo ở chân thư.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_lunch",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['lunch'],

    'data': [
        'data/mail_template_data.xml',
    ],
    # 'demo': [],
    'installable': False,
    # 'auto_install': True,  # TODO: Uncomment when upgrading module to production-ready status
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
