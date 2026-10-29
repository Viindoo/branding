{
    'name': "Payment Provider Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Payment Provider",

    'summary': """
Theme branding Viindoo for module Payment Provider""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Payment Provider
""",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in Payment Provider following Viindoo's brand

It also hides the Enterprise payment providers that are not available in the system from the Payment Providers list.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện các module Payment Provider theo thương hiệu Viindoo

Module này cũng ẩn các nhà cung cấp thanh toán Enterprise không có sẵn trong hệ thống
khỏi danh sách Nhà cung cấp thanh toán.


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_payment?force_show=1",
    'live_test_url': "https://v18demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v18demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['payment'],

    # always loaded
    'data': [
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'uninstall_hook': 'uninstall_hook',
}
