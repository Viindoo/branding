{
    'name': "Point Of Sale Self Order Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Tự gọi món của Điểm Bán Lẻ",

    'summary': """
Do not bother users with Enterprise-only options of Point Of Sale Self Order""",
    'summary_vi_VN': """
Không làm phiền người dùng bằng các tùy chọn chỉ có ở ấn bản Enterprise của Tự gọi món Điểm Bán Lẻ
""",

    'description': """
What it does
============
This module hides the "Pay after" setting of Point Of Sale Self Order, whose selector only opens
the Enterprise upsell. The stored value keeps the core behavior.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này ẩn thiết lập "Thanh toán sau" của Tự gọi món Điểm Bán Lẻ, vì bộ chọn của nó chỉ
mở ra chào mời ấn bản Enterprise. Giá trị đã lưu vẫn giữ hành vi của core.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_pos_self_order?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['viin_brand', 'viin_brand_pos', 'pos_self_order'],

    'data': [
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
    },

    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
