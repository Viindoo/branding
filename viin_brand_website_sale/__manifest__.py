# -*- coding: utf-8 -*-
{
    'name': "Website eCommerce Debranding for Viindoo",
    'name_vi_VN': "",

    'summary': """
Debranding Website eCommerce for Viindoo""",

    'summary_vi_VN': """
Làm lại màu sắc Phần mềm thương mại điện tử theo thương hiệu Viindoo
    	""",

    'description': """

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/Viindoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale', 'viin_brand_website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
    ],

    'images': [
    	# 'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': ['website_sale'],
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
