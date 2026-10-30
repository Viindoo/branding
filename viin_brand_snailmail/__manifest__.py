{
    'name': "Snail Mail Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho mô-đun Snail Mail",

    'summary': """
Removes the Odoo brand from Snail Mail messages""",
    'summary_vi_VN': """
Gỡ thương hiệu Odoo khỏi các thông báo của Snail Mail
""",

    'description': """
What it does
============
This module removes the Odoo brand from the messages of Snail Mail. The error shown when a letter
cannot be sent because the database has no IAP account no longer names an Odoo website.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này gỡ thương hiệu Odoo khỏi các thông báo của Snail Mail. Lỗi hiển thị khi thư không gửi được
vì cơ sở dữ liệu chưa có tài khoản IAP không còn nhắc đến website của Odoo.


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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['snailmail'],

    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
