{
    'name': "Viindoo Branding Surveys",
    'name_vi_VN': "Ung dụng Surveys với thương hiệu Viindoo",

    'summary': """
Set Viindoo Brandings for Surveys app.
""",

    'summary_vi_VN': """
Thiết lập thương hiệu Viindoo cho ứng dụng Surveys
    	""",

    'description': """
This module change some information for Viindoo branding
 
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô đun này thay đổi một vài thông tin dành riêng cho thương hiệu Viindoo

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': "https://www.tvtmarine.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'support': "support@ma.tvtmarine.com",
    'category': 'Marketing/Survey',
    'version': '0.1',
    'depends': ['survey'],
    'data': [
        'views/menu.xml'
    ],
    'images' : [
    	'static/description/icon.png'
	],
    'installable': True,
    'post_init_hook': 'update_module_icon',
    'uninstall_hook': 'uninstall_brand_icon',
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
