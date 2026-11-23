{
    'name': "Events Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Sự kiện",

    'summary': "Theme branding Viindoo for module Events",
    'summary_vi_VN': "Giao diện brand Viindoo cho module Sự kiện",

    'description': """
What it does
============
This module brands the stages, the website field placeholder and the onboarding tour of the events as Viindoo.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này đặt thương hiệu Viindoo cho các giai đoạn, gợi ý trường website và hướng dẫn làm quen của sự kiện.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_event?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1',

    'depends': ['event', 'viin_brand'],

    'data': [
        'data/event_stage_data.xml',
        'views/event_event_views.xml',
        'views/event_report_templates.xml',
    ],
    'demo': [
        'data/event_ticket_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'viin_brand_event/static/src/js/tours/event_tour.js',
        ],
        'web.assets_unit_tests': [
            'viin_brand_event/static/tests/event_tour.test.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
