{
    'name': "Website Profile Debranding for Viindoo",
    'name_vi_VN': "Thương hiệu Viindoo cho mô-đun Website Profile",

    'summary': """
Debranding Website Profile for Viindoo""",

    'summary_vi_VN': """
Thay thế thương hiệu Odoo bằng Viindoo trong mô-đun Website Profile
""",

    'description': """
What it does
============
This module replaces Odoo branding with Viindoo in the Website Profile module:
SCSS theming for the profile pages and Odoo references in the account validation email.


Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
====================
Mô-đun này thay thế thương hiệu Odoo bằng Viindoo trong mô-đun Website Profile:
SCSS chỉnh giao diện trang hồ sơ và thay thế chuỗi Odoo trong email xác thực tài khoản.


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v17demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v17demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/Viindoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_profile', 'viin_brand_mail'],

    'data': [
        'data/mail_template_data.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            ('after', 'website_profile/static/src/scss/website_profile.scss', 'viin_brand_website_profile/static/src/scss/website_profile.scss')
        ],
    },
    'images': [
        # 'static/description/main_screenshot.png'
        ],
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
