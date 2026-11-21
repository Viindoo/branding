{
    'name': "Snail Mail Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho mô-đun Snail Mail",

    'summary': """
Hides Snail Mail, a paid service operated by Odoo S.A.""",
    'summary_vi_VN': """
Ẩn Snail Mail, dịch vụ trả phí do Odoo S.A. vận hành
""",

    'description': """
What it does
============
This module hides Snail Mail, which sends letters through a paid service operated by Odoo S.A.: the
Snailmail Letters menu is hidden and the queue of letters is not processed. The module stays installed.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này ẩn Snail Mail, tính năng gửi thư bưu điện qua dịch vụ trả phí do Odoo S.A. vận hành: menu
Snailmail Letters bị ẩn và hàng đợi thư không được xử lý. Mô-đun vẫn được giữ nguyên trạng thái đã cài.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_snailmail?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['snailmail', 'viin_brand'],

    'data': [
        'data/ir_cron_data.xml',
        'data/ir_ui_menu_data.xml',
    ],

    'uninstall_hook': 'uninstall_hook',
    'installable': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
