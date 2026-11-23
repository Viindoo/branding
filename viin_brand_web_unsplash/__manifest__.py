{
    'name': "Unsplash Image Library Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Unsplash Image Library ",

    'summary': "Theme branding Viindoo for module Unsplash Image Library",
    'summary_vi_VN': "Giao diện brand Viindoo cho module Unsplash Image Library",

    'description': """
What it does
============
This module will change color in navigate bar, button and logo,v.v following Viindoo's brand

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện cuả Unsplash Image Library theo thương hiệu Viindoo

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_web_unsplash?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.1',

    'depends': ['web_unsplash'],

    'assets': {
        'html_editor.assets_media_dialog': [
            'viin_brand_web_unsplash/static/src/components/media_dialog/*.xml',
        ],
        'web.assets_unit_tests': [
            'viin_brand_web_unsplash/static/tests/unsplash_credentials_brand.test.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
