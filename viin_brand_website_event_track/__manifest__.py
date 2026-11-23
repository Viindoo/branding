{
    'name': "Events Online Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Sự kiện trực tuyến",

    'summary': "Viindoo colour for the events app and the theme colour of the event pages",
    'summary_vi_VN': "Màu Viindoo cho ứng dụng sự kiện và màu giao diện của các trang sự kiện",

    'description': """
What it does
============
The events app of the website, which visitors can install on their device, and the browser bar on
the event pages take the Viindoo content purple instead of the Odoo purple.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng sự kiện của website, mà khách truy cập có thể cài lên thiết bị, và thanh trình duyệt trên
các trang sự kiện dùng màu tím nội dung của Viindoo thay cho màu tím của Odoo.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_website_event_track?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['website_event_track', 'viin_brand'],

    'data': [
        'views/event_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # Same specificity as core's rule: it wins on source position.
            ('after', 'website_event_track/static/src/scss/event_track_templates_online.scss',
             'viin_brand_website_event_track/static/src/scss/event_track_templates_online.scss'),
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
