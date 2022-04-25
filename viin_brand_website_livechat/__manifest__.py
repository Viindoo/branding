# -*- coding: utf-8 -*-
{
    'name': "Website Live Chat Debranding for Viindoo",
    'name_vi_VN': "",

    'summary': """
Debranding Website Live Chat for Viindoo""",

    'summary_vi_VN': """
Làm lại màu sắc Website Live Chat theo thương hiệu Viindoo
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
    'depends': ['website_livechat', 'viin_brand_im_livechat'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],

    'assets' : {
        'web.assets_frontend' : [
            '/viin_brand_im_livechat/static/src/legacy/public_livechat.scss'
        ],
    },
    'images': [
    	# 'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
