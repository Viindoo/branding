{
    'name': "Project Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Dự án",

    'summary': """
This module brands Project with Viindoo: the onboarding tour, the examples of the stage columns and
the dialogs and errors of the project sharing page name Viindoo.""",
    'summary_vi_VN': """
Mô-đun này thay đổi giao diện Dự án theo thương hiệu Viindoo: tour hướng dẫn, ví dụ về các cột giai
đoạn, hộp thoại và thông báo lỗi của trang chia sẻ dự án đều nhắc tới Viindoo.
""",

    'description': """
What it does
============
This module brands Project with Viindoo: the onboarding tour, the examples of the stage columns and
the dialogs and errors of the project sharing page name Viindoo.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này thay đổi giao diện Dự án theo thương hiệu Viindoo: tour hướng dẫn, ví dụ về các cột giai
đoạn, hộp thoại và thông báo lỗi của trang chia sẻ dự án đều nhắc tới Viindoo.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_project",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['project', 'viin_brand'],

    # 'data': [],
    # 'demo': [],
    'assets': {
        'web.assets_backend': [
            'viin_brand_project/static/src/js/tours/project_tour.js',
            'viin_brand_project/static/src/xml/project_task_kanban_examples.xml',
        ],
        'project.webclient': [
            'viin_brand/static/src/core/dialog/dialog.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
            'viin_brand/static/src/core/browser/title_service.js',
        ],
        'web.assets_unit_tests': [
            'viin_brand_project/static/tests/project_debrand.test.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
