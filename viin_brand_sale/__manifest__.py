{
    'name': "Sale Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Sale",

    'summary': "Theme branding Viindoo for module Sale",
    'summary_vi_VN': "Giao diện brand Viindoo cho module Sale",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in Sale following Viindoo's brand

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện các module Sale theo thương hiệu Viindoo

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_sale?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    # The bridge installs wherever the Viindoo branding and sale are both present.
    'depends': ['sale', 'viin_brand'],

    'assets': {
        'web.assets_backend': [
            'viin_brand_sale/static/src/js/sale_action_helper/sale_action_helper.js',
            'viin_brand_sale/static/src/views/sale_file_upload_kanban/sale_file_upload_kanban_renderer.js',
            'viin_brand_sale/static/src/views/sale_file_upload_list/sale_file_upload_list_renderer.js',
        ],
        'web.assets_unit_tests': [
            'viin_brand_sale/static/tests/**/*.test.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
