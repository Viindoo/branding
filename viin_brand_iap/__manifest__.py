{
    'name': "Odoo IAP Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Odoo IAP",

    'summary': "Removes the credit-based services of Odoo S.A.: calls are refused, the IAP settings block, menu and buy-credit buttons are hidden; the free background services of Odoo keep working",
    'summary_vi_VN': "Gỡ các dịch vụ tính phí bằng credit của Odoo S.A.: lời gọi bị từ chối, khối IAP trong Cài đặt, menu IAP và nút mua credit bị ẩn; các dịch vụ nền miễn phí của Odoo vẫn hoạt động",

    'description': """
What it does
============
This module removes the credit-based services of Odoo S.A. from Viindoo: calls to those services are
refused with a clear message, the IAP block of the settings, the IAP menu and every button to buy
credits are hidden. The free background services of Odoo keep working.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này gỡ các dịch vụ tính phí bằng credit của Odoo S.A. khỏi Viindoo: mọi lời gọi tới các dịch
vụ đó bị từ chối kèm thông báo rõ ràng; khối IAP trong Cài đặt, menu IAP và mọi nút mua credit đều
bị ẩn. Các dịch vụ nền miễn phí của Odoo vẫn hoạt động.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_iap",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['iap_mail', 'viin_brand'],

    'data': [
        'data/ir_ui_menu_data.xml',
        'views/iap_account_views.xml',
        'views/res_config_settings_views.xml',
    ],
    # 'demo': [],
    'assets': {
        'web.assets_backend': [
            'viin_brand_iap/static/src/action_buttons_widget/no_credits_widget.js',
            'viin_brand_iap/static/src/action_buttons_widget/no_credits_widget.xml',
            'viin_brand_iap/static/src/services/iap_notification_service.js',
        ],
        'web.assets_unit_tests': [
            'viin_brand_iap/static/tests/iap_credit_surfaces.test.js',
        ],
    },
    'post_load': 'post_load',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
