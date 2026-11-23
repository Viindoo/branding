{
    'name': "Attendances Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Chấm công",

    'summary': "Viindoo brand on the attendance kiosk logo, the empty state, dialogs, errors and documentation links",
    'summary_vi_VN': "Thương hiệu Viindoo trên logo kiosk chấm công, màn hình trống, hộp thoại, thông báo lỗi và liên kết tài liệu",

    'description': """
What it does
============
This module brands the attendance kiosk and the attendance settings with Viindoo: the kiosk is
powered by the Viindoo logo, the empty state shows a Viindoo kiosk, and dialogs, errors and
documentation links name Viindoo.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này thay đổi giao diện kiosk chấm công và cài đặt chấm công theo thương hiệu Viindoo: kiosk
hiển thị logo Viindoo, màn hình trống hiển thị kiosk Viindoo, hộp thoại, thông báo lỗi và liên kết
tài liệu đều nhắc tới Viindoo.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_hr_attendance",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['hr_attendance', 'viin_brand'],

    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'viin_brand_hr_attendance/static/src/views/attendance_helper_view.xml',
            # The kiosk bundle is public; the template extension is also listed here so that the
            # Hoot unit tests, which load this bundle only, find its parent template.
            'viin_brand_hr_attendance/static/src/public_kiosk/public_kiosk_app.xml',
        ],
        'hr_attendance.assets_public_attendance': [
            'viin_brand_hr_attendance/static/src/public_kiosk/public_kiosk_app.xml',
            'viin_brand/static/src/core/dialog/dialog.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
            'viin_brand/static/src/views/widgets/documentation_link/documentation_link.js',
            'viin_brand/static/src/views/widgets/documentation_link/documentation_link.xml',
            'viin_brand/static/src/views/widgets/documentation_link/viindoo_mapping_url.js',
        ],
        'web.assets_unit_tests': [
            'viin_brand_hr_attendance/static/tests/kiosk_debrand.test.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
