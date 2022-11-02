{
    'name': "Skills Management Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Skills Management",

    'summary': """
Theme branding Viindoo for module Skills Management """,
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Skills Management 
""",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in Skills Management following Viindoo's brand
Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện module Skills Management theo thương hiệu Viindoo
Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
""",

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v15demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v15demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_skills'],

    # always loaded
    'data': [
        'views/hr_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
