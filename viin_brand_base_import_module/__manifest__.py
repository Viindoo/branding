{
    'name': "Import Module Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Nhập module",

    'summary': """
Theme branding Viindoo for module Import Module""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Nhập module
""",

    'description': """
What it does
============
This module brands the messages of the module import as Viindoo and keeps the Enterprise offer out of them.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này thương hiệu hóa các thông điệp khi nhập module theo Viindoo và không đưa lời chào mời bản Enterprise vào đó.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_base_import_module?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_import_module'],

    # 'images': [
    #     'static/description/main_screenshot.png',
    #     'static/description/another_screenshot_1.png',
    #     'static/description/another_screenshot_2.png',
    # ],

    # The list of IDs of the project tasks in Viindoo Company's database that require
    # this module development.
    # 'task_ids': [
    #     1292, 1294,
    # ],

    'installable': False,
    # If this module is a bridge module that integrates 2 or more other modules,
    # auto_install must be set to True.
    # In case this module is a module that provides additional functions / features,
    # it should be activated via a setting directive of the main application related
    # to these new functions / features.
    # 'auto_install': True,  # TODO: Uncomment when upgrading module to production-ready status
    # 99.9 EURO is a good start for an application while bridge modules should be free of charge
    # as we usually have pricing for the others that are bridged by this module.
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
