{
    'name': "Event Exhibitors Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Event Exhibitors",

    'summary': "Theme branding Viindoo for module Event Exhibitors",
    'summary_vi_VN': "Giao diện brand Viindoo cho module Event Exhibitors",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in module Event Exhibitors following Viindoo's brand

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện module Event Exhibitors theo thương hiệu Viindoo

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_website_event_exhibitor?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.1',

    'depends': ['website_event_exhibitor', 'viin_brand'],

    'data': [
        'views/event_sponsor_views.xml',
    ],
    'demo': [
        'data/event_sponsor_demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # Same specificity as core's rule: it wins on source position.
            ('after', 'website_event_exhibitor/static/src/scss/event_exhibitor_templates.scss',
             'viin_brand_website_event_exhibitor/static/src/scss/event_exhibitor_templates.scss'),
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
