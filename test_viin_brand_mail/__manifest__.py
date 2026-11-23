{
    'name': "[TEST] Viindoo Mail Branding",
    'name_vi_VN': "[TEST] Thương hiệu Viindoo cho Mail",

    'summary': "Keep the core Mail-related test suites aligned with Viindoo Mail",
    'summary_vi_VN': "Giữ các bộ kiểm thử lõi liên quan tới Mail khớp với Viindoo Mail",

    'description': """
What it does
============
The core test suites of `test_mail`, `test_mail_full`, `google_calendar` and `cloud_storage` assert the
Odoo branding that Viindoo Mail Branding replaces: the Odoo icon of a web push notification without an
author, the OdooBot partner that organizes a synchronized calendar event, the `@OdooBot` mention of the
first answer of the bot onboarding and the sentence of the email that announces a call recording. This
test-only module realigns those expectations to Viindoo, so the suites keep guarding the behaviour they
are written for while the modules are installed together.

* It is installed automatically with `viin_brand_mail`, `viin_brand_mail_bot`, `test_mail`,
  `test_mail_full`, `google_calendar` and `cloud_storage`, and carries no feature.
* Load it server wide together with `viin_brand`
  (`--load=base,web,viin_brand,test_viin_brand_mail`), so the realignment is in place before the
  `at_install` tests of `google_calendar` run.
    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Các bộ kiểm thử lõi của `test_mail`, `test_mail_full`, `google_calendar` và `cloud_storage` khẳng định
thương hiệu Odoo mà Viindoo Mail Branding thay thế: biểu tượng Odoo của thông báo web push không có tác
giả, đối tác OdooBot tổ chức sự kiện lịch được đồng bộ, lời nhắc `@OdooBot` trong câu trả lời đầu tiên
của bot hướng dẫn và câu trong email thông báo bản ghi cuộc gọi. Module chỉ dùng cho kiểm thử này chỉnh
các kỳ vọng đó sang Viindoo, để các bộ kiểm thử vẫn bảo vệ đúng hành vi mà chúng được viết ra khi các
module cùng được cài đặt.

* Tự động cài cùng `viin_brand_mail`, `viin_brand_mail_bot`, `test_mail`, `test_mail_full`,
  `google_calendar` và `cloud_storage`, không có tính năng nào.
* Nạp ở chế độ server wide cùng `viin_brand`
  (`--load=base,web,viin_brand,test_viin_brand_mail`), để việc chỉnh có hiệu lực trước khi các kiểm
  thử `at_install` của `google_calendar` chạy.
""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/test_viin_brand_mail?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden/Tests',
    'version': '0.1.0',

    'depends': [
        'viin_brand_mail',
        'viin_brand_mail_bot',
        'test_mail',
        'test_mail_full',
        'google_calendar',
        'cloud_storage',
    ],

    'post_load': 'post_load',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
