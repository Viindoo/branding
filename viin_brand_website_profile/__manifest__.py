# -*- coding: utf-8 -*-
{
    'name': "Website profile Debranding for Viindoo",
    'name_vi_VN': "",

    'summary': """
Debranding Website profile for Viindoo""",

    'summary_vi_VN': """
Làm lại màu sắc Phần mềm Website profile theo thương hiệu Viindoo
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
    'live_test_url': "https://v15demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v15demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/Viindoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_profile'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'assets' : {
        'web.assets_frontend' : [
            ('after','website_profile/static/src/scss/website_profile.scss','viin_brand_website_profile/static/src/scss/website_profile.scss')
        ],
    },
    'images': [
    	# 'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': ['website_profile'],
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
