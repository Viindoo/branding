{
    'name': "Point Of Sale Self Order Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Tự gọi món của Điểm Bán Lẻ",

    'summary': "Viindoo identity on the kiosk and the self order pages of Point Of Sale Self Order",
    'summary_vi_VN': "Mang nhận diện Viindoo lên màn hình kiosk và các trang tự gọi món của Điểm Bán Lẻ",

    'description': """
What it does
============
This module shows the Viindoo identity on the kiosk and the self order pages of Point Of Sale
Self Order:

* the kiosk landing images say "Powered by Viindoo", for the kiosks created from now on and for
  the ones already created;
* the self order page title carries no product name;
* the entry points to the QR stands ordered from a page hosted by another vendor are hidden;
* the "Pay after" setting, whose selector only opens the Enterprise upsell, is hidden. The stored
  value keeps the core behavior.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này mang nhận diện Viindoo lên màn hình kiosk và các trang tự gọi món của Điểm Bán Lẻ:

* ảnh trang chờ của kiosk ghi "Powered by Viindoo", cho kiosk tạo từ nay và cho kiosk đã tạo;
* tiêu đề trang tự gọi món không mang tên sản phẩm;
* ẩn các lối vào đặt giá đỡ mã QR từ trang do nhà cung cấp khác lưu trữ;
* ẩn thiết lập "Thanh toán sau", vì bộ chọn của nó chỉ mở ra chào mời ấn bản Enterprise. Giá trị
  đã lưu vẫn giữ hành vi của core.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_pos_self_order?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['viin_brand', 'viin_brand_pos', 'pos_self_order'],

    'data': [
        'data/pos_config_data.xml',
        'views/custom_link_views.xml',
        'views/pos_self_order_index.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'viin_brand_pos_self_order/static/src/overrides/screens/floor_screen/floor_screen.xml',
            'viin_brand_pos_self_order/static/src/overrides/components/navbar/navbar.xml',
        ],
        'pos_self_order.assets': [
            # The self order app bundles the core of the web client but not web.assets_backend,
            # so the dialog and error de-brand of viin_brand is listed here.
            'viin_brand/static/src/core/dialog/dialog.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
        ],
        'web.assets_unit_tests': [
            'viin_brand_pos_self_order/static/tests/qr_stands_debrand.test.js',
        ],
    },

    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
