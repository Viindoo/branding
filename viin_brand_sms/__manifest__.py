{
    'name': "SMS Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module SMS",

    'summary': "This module makes SMS go through the Twilio account of the customer: Twilio is installed wherever SMS is.",
    'summary_vi_VN': "Mô-đun này đưa việc gửi SMS về tài khoản Twilio của khách hàng: Twilio được cài ở mọi nơi có SMS.",

    'description': """
What it does
============
This module makes SMS go through the Twilio account of the customer: Twilio is installed wherever
SMS is.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này đưa việc gửi SMS về tài khoản Twilio của khách hàng: Twilio được cài ở mọi nơi có SMS.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_sms",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['sms', 'sms_twilio'],

    # 'data': [],
    # 'demo': [],
    'assets': {
        'web.assets_backend': [
            'viin_brand_sms/static/src/components/sms_widget/fields_sms_widget.xml',
        ],
        'web.assets_unit_tests': [
            'viin_brand_sms/static/tests/sms_widget_pricing_link.test.js',
        ],
    },
    'installable': True,
    'auto_install': ['sms'],
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
