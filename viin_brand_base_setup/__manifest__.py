{
    'name': "Initial Setup Tools Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Initial Setup Tools",

    'summary': """
Theme branding Viindoo for module Initial Setup Tools""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Initial Setup Tools
""",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in module Initial Setup Tools following Viindoo's brand


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện module Initial Setup Tools theo thương hiệu Viindoo


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
    'depends': ['base_setup'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'viin_brand_base_setup/static/src/xml/res_config_edition.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
