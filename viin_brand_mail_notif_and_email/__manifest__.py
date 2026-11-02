{
    'name': "Inbox Notifications and Emails Branding For Viindoo",
    'name_vi_VN': "Thông Báo Hệ Thống Và Email Theo Thương hiệu Viindoo",

    'summary': """
Viindoo wording for the notification policy help, including the By Emails and Inbox choice""",
    'summary_vi_VN': """
Diễn giải chính sách nhận thông báo theo thương hiệu Viindoo, gồm cả lựa chọn Bằng email và hộp thư đến""",

    'description': """
What it does
============
Bridge module between ``viin_brand_mail`` and ``to_mail_notif_and_email``. The tooltip of the user's *Notification* preference describes all three choices with the Viindoo wording, including **By Emails and Inbox**.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module cầu nối giữa ``viin_brand_mail`` và ``to_mail_notif_and_email``. Chú thích của tùy chọn *Thông báo* trên người dùng mô tả cả ba lựa chọn theo thương hiệu Viindoo, gồm cả **Bằng email và hộp thư đến**.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_mail_notif_and_email?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_brand_mail', 'to_mail_notif_and_email'],

    'installable': True,
    'auto_install': True,
    'license': 'OPL-1',
}
