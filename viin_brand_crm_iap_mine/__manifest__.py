{
    'name': "Lead Mining Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho mô-đun Lead Mining",

    'summary': "Hides Lead Mining, a paid service operated by Odoo S.A.",
    'summary_vi_VN': "Ẩn Lead Mining, dịch vụ trả phí do Odoo S.A. vận hành",

    'description': """
What it does
============
This module hides the Lead Generation menus of Lead Mining, a paid service operated by Odoo S.A. The module stays
installed.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này ẩn các menu Lead Generation của Lead Mining, dịch vụ trả phí do Odoo S.A. vận hành. Mô-đun vẫn được giữ nguyên
trạng thái đã cài.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_crm_iap_mine",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['crm_iap_mine', 'viin_brand'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_ui_menu_data.xml',
    ],

    'uninstall_hook': 'uninstall_hook',

    'installable': True,
    # If this module is a bridge module that integrates 2 or more other modules,
    # auto_install must be set to True.
    # In case this module is a module that provides additional functions / features,
    # it should be activated via a setting directive of the main application related
    # to these new functions / features.
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
