{
    'name': "Viindoo Branding Live Chat",
    'name_vi_VN': "Ứng dụng Live Chat với thương hiệu Viindoo",

    'summary': """
Set Viindoo Brandings for Live Chat app.
""",

    'summary_vi_VN': """
Thiết lập thương hiệu Viindoo cho ứng dụng Live Chat
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
    'category': 'Website/Live Chat',
    'version': '0.1',
    'depends': ['im_livechat', 'viin_brand_base'],
    'images' : [
    	'static/description/icon.png'
	],
    'data' : [
        'data/update_icon.xml'
    ],
    'installable': False,
    'uninstall_hook': '_uninstall_brand_icon',
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
