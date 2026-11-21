{
    'name': "Twilio SMS Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Twilio SMS",

    'summary': """
This module makes Twilio the way SMS are sent: new companies send through Twilio, companies that
sent through Odoo are moved to it, and a company without a Twilio account is told, with a way to the
settings, that sending is not configured.""",
    'summary_vi_VN': """
Mô-đun này đặt Twilio làm cách gửi SMS: công ty mới gửi qua Twilio, công ty đang gửi qua Odoo được
chuyển sang Twilio, và công ty chưa có tài khoản Twilio được báo rõ rằng chưa cấu hình gửi SMS, kèm
lối đi tới Cài đặt.
""",

    'description': """
What it does
============
This module makes Twilio the way SMS are sent: new companies send through Twilio, companies that
sent through Odoo are moved to it, and a company without a Twilio account is told, with a way to the
settings, that sending is not configured.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này đặt Twilio làm cách gửi SMS: công ty mới gửi qua Twilio, công ty đang gửi qua Odoo được
chuyển sang Twilio, và công ty chưa có tài khoản Twilio được báo rõ rằng chưa cấu hình gửi SMS, kèm
lối đi tới Cài đặt.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_sms_twilio",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
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
    'installable': False,
    # 'auto_install': True,  # TODO: Uncomment when upgrading module to production-ready status
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
