{
    'name': "Events Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Events",

    'summary': "Viindoo branding of the sample data of Events",
    'summary_vi_VN': "Thương hiệu Viindoo cho dữ liệu mẫu của Sự kiện",

    'description': """
What it does
============
This module replaces the Odoo brand with Viindoo in the sample events and the sample speaker profile
of the demo data of Events.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này thay thương hiệu Odoo bằng Viindoo trong sự kiện mẫu và hồ sơ diễn giả mẫu
của dữ liệu demo của Sự kiện.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_website_event?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['website_event', 'viin_brand'],

    'demo': [
        'data/event_demo.xml',
        'data/res_partner_demo.xml',
    ],
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
