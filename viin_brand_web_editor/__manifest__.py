{
    'name': "Viindoo debranding for Web Editor",
    'name_vi_VN': "Làm lại nhận diện thương hiệu cho Web Editor",

    'summary': """This module debrands the Web Editor module for Viindoo brand""",

    'summary_vi_VN': """Mô-đun này làm lại nhận diện thương hiệu Viindoo cho Web Editor""",

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
    'website': " https://viindoo.com",
    'live_test_url': "https://v17demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v17demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['web_editor', 'web'],
    'assets': {
        'web.assets_backend': [
            ('after', 'web_editor/static/src/scss/web_editor.common.scss', 'viin_brand_web_editor/static/src/scss/web_editor.common.scss'),
        ],
        'web.assets_frontend': [
            ('after', 'web_editor/static/src/scss/web_editor.common.scss', 'viin_brand_web_editor/static/src/scss/web_editor.common.scss'),
        ],
        'web.report_assets_common': [
            ('after', 'web_editor/static/src/scss/web_editor.common.scss', 'viin_brand_web_editor/static/src/scss/web_editor.common.scss'),
        ],
    },
    'installable': True,
    'auto_install': ['web_editor'],
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
