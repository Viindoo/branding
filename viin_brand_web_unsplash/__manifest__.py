{
    'name': "Unsplash Image Library Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Unsplash Image Library ",

    'summary': """
Theme branding Viindoo for module Unsplash Image Library""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Unsplash Image Library
""",

    'description': """
What it does
============
This module will change color in navigate bar, button and logo,v.v following Viindoo's brand


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện cuả Unsplash Image Library theo thương hiệu Viindoo


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web_unsplash'],

    # always loaded
    'data': [
        'views/res_config_settings_view.xml',
    ],
<<<<<<< HEAD
    'installable': False, # set auto_install True after upgrading for v17 after upgrading for v17
=======
    'assets': {
        'web_editor.assets_media_dialog': [
            'viin_brand_web_unsplash/static/src/components/media_dialog/*.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
>>>>>>> a562c89 ([IMP] viin_brand_web_unsplash: update branding for media_dialog)
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
