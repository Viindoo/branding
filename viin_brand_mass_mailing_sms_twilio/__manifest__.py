{
    'name': "SMS Marketing Twilio Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module SMS Marketing qua Twilio",

    'summary': """
Stops the sending of an SMS campaign while the company has no Twilio account""",
    'summary_vi_VN': """
Dừng việc gửi chiến dịch SMS khi công ty chưa có tài khoản Twilio
""",

    'description': """
What it does
============
Sending an SMS campaign by hand (Send, Schedule, Send Now, Test) while the company has no Twilio
account is stopped with a message that points to the settings. Campaigns that run unattended are
not stopped: each of their SMS fails with the same message.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Gửi chiến dịch SMS bằng tay (Send, Schedule, Send Now, Test) khi công ty chưa có tài khoản Twilio sẽ
bị dừng kèm thông báo chỉ tới phần Cài đặt. Chiến dịch chạy tự động không bị dừng: từng SMS của chiến
dịch lỗi kèm cùng thông báo.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_mass_mailing_sms_twilio",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1',

    'depends': ['viin_brand_mass_mailing_sms', 'viin_brand_sms_twilio'],

    # 'data': [],
    # 'demo': [],
    'installable': False,
    # 'auto_install': True,  # TODO: Uncomment when upgrading module to production-ready status
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
