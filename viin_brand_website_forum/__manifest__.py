{
    'name': "Forum Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho mô-đun Forum",

    'summary': """
Theme branding Viindoo for module Forum""",
    'summary_vi_VN': """
Giao diện Viindoo cho mô-đun Forum
""",

    'description': """
What it does
============
This module replaces the Odoo brand with Viindoo in the help content of the forums: the default FAQ
given to every new forum, the karma page, and the sample question and answer of the demo forum.
It does not change colours, buttons or the logo.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này thay thương hiệu Odoo bằng Viindoo trong nội dung trợ giúp của các diễn đàn: FAQ mặc định
dành cho mỗi diễn đàn mới, trang điểm karma, cùng câu hỏi và câu trả lời mẫu của diễn đàn demo.
Mô-đun không thay đổi màu sắc, nút bấm hay logo.


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_website_forum?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['website_forum'],
    'data': [
        'views/forum_forum_template_faq.xml',
        'views/forum_forum_templates_tools.xml',
    ],
    # always loaded
    'demo': [
        'data/forum_demo.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
