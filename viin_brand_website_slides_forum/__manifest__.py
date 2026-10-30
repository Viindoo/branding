{
    'name': "Slides Forum Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho mô-đun Slides Forum",

    'summary': """
Viindoo FAQ for the forums of eLearning courses""",
    'summary_vi_VN': """
Áp dụng FAQ Viindoo cho các diễn đàn khóa học của mô-đun Slides Forum
""",

    'description': """
What it does
============
When installed, this module replaces the default FAQ of the forums that eLearning creates with its
sample data (Slides Forum) with the Viindoo FAQ provided by Forum Branding For Viindoo, so these course
forums no longer show the Odoo FAQ. It does not change colours, buttons or the logo.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Khi được cài đặt, mô-đun này thay FAQ mặc định của các diễn đàn mà eLearning tạo ra cùng dữ liệu
mẫu (Slides Forum) bằng FAQ Viindoo của mô-đun Forum Branding For Viindoo, nhờ đó các
diễn đàn khóa học này không còn hiển thị FAQ của Odoo. Mô-đun không thay đổi màu sắc, nút bấm hay logo.


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_website_slides_forum?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_slides_forum', 'viin_brand_website_forum'],
    # always loaded
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': ['website_slides_forum'],
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
