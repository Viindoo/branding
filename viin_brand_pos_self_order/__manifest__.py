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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # viin_brand_pos: the branding of Point Of Sale this module completes
    'depends': ['viin_brand_pos', 'pos_self_order'],

    'installable': True,
    # Bridge module: installed together with the two modules it bridges.
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
