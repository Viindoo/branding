{
    'name': "Portal Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Portal",

    'summary': "Theme branding Viindoo for module Portal",
    'summary_vi_VN': "Giao diện brand Viindoo cho module Portal",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in Portal following Viindoo's brand
Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện các module Portal theo thương hiệu Viindoo
Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_portal?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['portal', 'viin_brand'],

    'data': [
        'views/portal_templates.xml',
    ],
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
