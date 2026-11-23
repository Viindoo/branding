{
    'name': "[TEST] Viindoo Branding",
    'name_vi_VN': "[TEST] Thương hiệu Viindoo",

    'summary': "Keep the core test suites of test_base aligned with the Viindoo branding.",
    'summary_vi_VN': "Giữ các bộ kiểm thử lõi của test_base khớp với thương hiệu Viindoo.",

    'description': """
What it does
============
The core test suites of `test_base` assert the Odoo branding that Viindoo Branding replaces:
the stock icon of a module manifest and the Odoo creator and producer of a written PDF document.
This test-only module realigns those expectations to Viindoo, so the suites keep guarding the
behaviour they are written for while both modules are installed.

* It is installed automatically with `viin_brand` and `test_base`, and carries no feature.
* Load it server wide together with `viin_brand` (`--load=base,web,viin_brand,test_viin_brand`),
  so the realignment is in place before the `at_install` tests of `test_base` run.
    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Các bộ kiểm thử lõi của `test_base` khẳng định thương hiệu Odoo mà Viindoo Branding thay thế:
biểu tượng mặc định trong manifest của module và người tạo, nhà sản xuất Odoo của tài liệu PDF.
Module chỉ dùng cho kiểm thử này chỉnh các kỳ vọng đó sang Viindoo, để các bộ kiểm thử vẫn bảo vệ
đúng hành vi mà chúng được viết ra khi cả hai module cùng được cài đặt.

* Tự động cài cùng `viin_brand` và `test_base`, không có tính năng nào.
* Nạp ở chế độ server wide cùng `viin_brand` (`--load=base,web,viin_brand,test_viin_brand`),
  để việc chỉnh có hiệu lực trước khi các kiểm thử `at_install` của `test_base` chạy.
""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/test_viin_brand?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden/Tests',
    'version': '0.1.0',

    'depends': ['viin_brand', 'test_base'],

    'post_load': 'post_load',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
