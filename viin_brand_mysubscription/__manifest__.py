{
    'name': "My Subscription Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module My Subscription",

    'summary': "Hide the My Subscription entry of the user menu",
    'summary_vi_VN': "Ẩn mục My Subscription trong menu người dùng",

    'description': """
What it does
============
This module removes the "My Subscription" entry from the user menu: it opens the Odoo plan
dashboard (Community and Enterprise plans, In-App Purchases, upgrade), which is not a Viindoo
offer.

* It is installed automatically with `mysubscription` and `viin_brand`, and carries no feature.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này gỡ mục "My Subscription" khỏi menu người dùng: mục này mở bảng điều khiển gói của Odoo
(gói Community và Enterprise, mua trong ứng dụng, nâng cấp), không phải dịch vụ của Viindoo.

* Tự động cài cùng `mysubscription` và `viin_brand`, không có tính năng nào.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_mysubscription?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['mysubscription', 'viin_brand'],

    'assets': {
        'web.assets_backend': [
            'viin_brand_mysubscription/static/src/user_menu.js',
        ],
        'web.assets_unit_tests': [
            'viin_brand_mysubscription/static/tests/user_menu_debrand.test.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
