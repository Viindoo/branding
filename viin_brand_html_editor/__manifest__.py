{
    'name': "Viindoo debranding for HTML Editor",
    'name_vi_VN': "Làm lại nhận diện thương hiệu cho HTML Editor",

    'summary': """This module debrands the HTML Editor module for Viindoo brand""",

    'summary_vi_VN': """Mô-đun này làm lại nhận diện thương hiệu Viindoo cho HTML Editor""",

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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_html_editor?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',
    # Renamed from `viin_brand_web_editor` for 19.0: it now de-brands `html_editor`, the 19.0
    # replacement of the removed core `web_editor`. `old_technical_name` carries the old module's
    # install state over on upgrade - the standard Viindoo module-rename key.
    'old_technical_name': 'viin_brand_web_editor',
    'depends': ['html_editor', 'web'],
    'assets': {
        'web.assets_frontend': [
            ('after', 'html_editor/static/src/scss/html_editor.common.scss', 'viin_brand_html_editor/static/src/scss/viin_brand_html_editor.common.scss'),
        ],
    },
    'installable': True,
    'auto_install': ['html_editor'],
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
