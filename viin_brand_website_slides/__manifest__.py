{
    'name': "eLearning Debranding for Viindoo",
    'name_vi_VN': "Làm lại nhận diện thương hiệu cho eLearning",

    'summary': "Debranding eLearning for Viindoo",

    'summary_vi_VN': "Làm lại màu sắc Phần mềm eLearning theo thương hiệu Viindoo",

    'description': """

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_website_slides?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['website_slides', 'viin_brand'],

    'assets': {
        'web.assets_frontend': [
            'viin_brand_website_slides/static/src/scss/website_slides.scss',
        ],
    },
    'data': [
        'data/website_slides_templates_profile.xml',
        'views/slide_slide_views.xml',
        'views/website_slides_templates.xml',
    ],
    'demo': [
        'data/slide_slide_demo.xml',
    ],

    'installable': True,
    'auto_install': ['website_slides'],
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
