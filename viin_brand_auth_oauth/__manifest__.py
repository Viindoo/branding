{
    'name': "OAuth2 Authentication Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module OAuth2 Authentication",

    'summary': "Theme branding Viindoo for module OAuth2 Authentication",
    'summary_vi_VN': "Giao diện brand Viindoo cho module OAuth2 Authentication",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in module OAuth2 Authentication following Viindoo's brand

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện module OAuth2 Authentication theo thương hiệu Viindoo

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_auth_oauth?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['auth_oauth'],

    'data': [
        'data/auth_oauth_data.xml',
    ],
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
