{
    'name': "Zalo Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Zalo ",

    'summary': """
Theme branding Viindoo for module Zalo""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Zalo
""",

    'description': """
Problem
=======
- On version 16.0, the Web Responsive module overwrites the entire structure of the `mail.ChatterTopbar` template, leading to some xpath that cannot be performed, because if there is xpath, it will be replaced by the entire.
- For example, in the `Zalo` module, there is an xpath to the element `div hassclass o_ChatterTopbar_controllers` but when the Web Responsive module replaces the entire, it will not be able to find the element.

Solution
========
- To solve this problem, we will create a new module `viin_brand_zalo` to inherit the `mail.ChatterTopbar` template after being replaced by Web Responsive.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Vấn đề
======
- Trên phiên bản 16.0, mô đun Web Responsive thực hiện ghi đè lại toàn bộ cấu trúc của template `mail.ChatterTopbar` dẫn đến một số xpath không thể thực hiện, do có xpath rồi thì vẫn bị replace đi toàn bộ.
- Ví dụ điển hình là tại mô đun `Zalo` có thực hiện xpath tới element `div hassclass o_ChatterTopbar_controllers` nhưng khi bị mô đun Web Responsive replace toàn bộ

Giải pháp
=========
- Để giải quyết vấn đề này, chúng tôi sẽ tạo một mô đun mới `viin_brand_zalo` để thực hiện kế thừa lại template `mail.ChatterTopbar` sau khi bị Web Responsive replace.

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
    'depends': ['viin_zalo', 'web_responsive'],

    'assets': {
        'web.assets_backend': [
            'viin_brand_zalo/static/src/components/chatter_topbar/*.xml',
        ],
    },
    'installable': True,  # todo: remove me in version 17.0 because web responsive not replace the entire template
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
