{
    'name': "Viin Brand Mass Mailing Themes",
    'name_vi_VN': "Giao diện Viindoo cho Mass Mailing Themes",

    'summary': """
Theme branding Viindoo for module Mass Mailing Themes""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Mass Mailing Themes""",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in Mass Mailing Themes following Viindoo's brand
Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện module Mass Mailing Themes theo thương hiệu Viindoo
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
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mass_mailing_themes'],

    # always loaded
    'data': [
        'views/mass_mailing_themes_templates.xml',
    ],
    'installable': False, # set auto_install True after upgrading for v17 after upgrading for v17
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
