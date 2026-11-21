{
    'name': "Surveys Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Khảo sát",

    'summary': """
This module brands Surveys with Viindoo: the certification sample and the onboarding tour name
Viindoo.""",
    'summary_vi_VN': """
Mô-đun này thay đổi giao diện Khảo sát theo thương hiệu Viindoo: mẫu chứng chỉ và tour hướng dẫn
nhắc tới Viindoo.
""",

    'description': """
What it does
============
This module brands Surveys with Viindoo: the certification sample and the onboarding tour name
Viindoo.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này thay đổi giao diện Khảo sát theo thương hiệu Viindoo: mẫu chứng chỉ và tour hướng dẫn
nhắc tới Viindoo.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_survey",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['survey'],

    # 'data': [],
    # 'demo': [],
    'assets': {
        'web.assets_backend': [
            'viin_brand_survey/static/src/js/tours/survey_tour.js',
        ],
        'web.assets_frontend': [
            'viin_brand_survey/static/src/js/tours/survey_tour.js',
        ],
        'web.assets_unit_tests': [
            'viin_brand_survey/static/tests/survey_tour_debrand.test.js',
        ],
    },
    'installable': False,
    # 'auto_install': True,  # TODO: Uncomment when upgrading module to production-ready status
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
