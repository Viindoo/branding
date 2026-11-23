{
    'name': "Twilio SMS Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Twilio SMS",

    'summary': "Makes Twilio the way SMS are sent and debrands its wording",
    'summary_vi_VN': "Đặt Twilio làm cách gửi SMS và thay thế thương hiệu Odoo trong nội dung",

    'description': """
What it does
============
This module makes Twilio the way SMS are sent: new companies send through Twilio, companies that
sent through Odoo are moved to it, the choice of Odoo as the provider is hidden, and the messages and
the SMS errors name Viindoo instead of Odoo.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này đặt Twilio làm cách gửi SMS: công ty mới gửi qua Twilio, công ty đang gửi qua Odoo được
chuyển sang Twilio, lựa chọn Odoo làm nhà cung cấp bị ẩn, và các thông báo cùng lỗi gửi SMS nhắc tới
Viindoo thay vì Odoo.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_sms_twilio",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['sms_twilio'],

    'data': [
        'views/res_config_settings_views.xml',
        'views/sms_twilio_account_manage_views.xml',
    ],
    # 'demo': [],
    'post_load': 'post_load',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
