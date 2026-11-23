{
    'name': "Website eCommerce Debranding for Viindoo",
    'name_vi_VN': "Làm lại nhận diện thương hiệu cho Website eCommerce",

    'summary': "Debranding Website eCommerce for Viindoo",

    'summary_vi_VN': "Làm lại màu sắc Phần mềm thương mại điện tử theo thương hiệu Viindoo",

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
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_website_sale?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.2.2',

    'depends': ['website_sale'],

    'data': [
        'views/res_config_settings_views.xml',
        'views/templates.xml',
    ],

    'installable': True,
    'auto_install': ['website_sale'],
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
