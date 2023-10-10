{
    'name': "Viindoo Branding Common",
    'name_vi_VN': "Thiết kế với thương hiệu Viindoo",

    'summary': """
Frontend theme for Viindoo Branding
""",

    'summary_vi_VN': """
Chủ đề giao diện cho thương hiệu Viindoo
        """,

    'description': """
This module change some information for Viindoo branding

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô đun này thay đổi một vài thông tin dành riêng cho thương hiệu Viindoo

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': " https://viindoo.com",
    'live_test_url': "https://v15demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v15demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['viin_brand', 'web'],
    'data': [
        'views/ir_module_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/webclient_template.xml'
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss', 'viin_brand_common/static/src/scss/primary_variables.scss'),
        ],
        'web._assets_secondary_variables': [
            ('prepend', 'viin_brand_common/static/src/legacy/scss/secondary_variables.scss'),
        ],
        'web._assets_backend_helpers': [
            ('after', 'web/static/src/scss/bootstrap_overridden.scss', 'viin_brand_common/static/src/scss/bootstrap_overridden.scss'),
        ],
        'web._assets_helpers': [
            'viin_brand_common/static/src/legacy/scss/bootstrap_overridden_common.scss'
        ],
        'web.assets_common': [
            'viin_brand_common/static/src/legacy/scss/navbar.scss',
            'viin_brand_common/static/src/legacy/scss/systray.scss'
        ],
        'web.assets_backend': [
            # common branding
            'viin_brand_common/static/src/views/graph/colors.js',
            ('after', 'web/static/src/webclient/webclient.scss', 'viin_brand_common/static/src/webclient/webclient.scss'),
            ('after', 'web/static/src/legacy/scss/fields_extra.scss', 'viin_brand_common/static/src/legacy/scss/fields_extra.scss'),
            ('after', 'web/static/src/legacy/scss/form_view.scss', 'viin_brand_common/static/src/legacy/scss/form_view.scss'),
            ('after', 'web/static/src/legacy/scss/form_view_extra.scss', 'viin_brand_common/static/src/legacy/scss/form_view_extra.scss'),
            ('after', 'web/static/src/legacy/scss/kanban_view.scss', 'viin_brand_common/static/src/legacy/scss/kanban_view.scss'),
            ('after', 'web/static/src/search/search_panel/search_view.scss', 'viin_brand_common/static/src/search/search_panel/search_view.scss'),
            ('after', 'base/static/src/scss/onboarding.scss', 'viin_brand_common/static/src/scss/onboarding.scss'),
            ('after', 'web/static/src/webclient/settings_form_view/settings_form_view.scss', 'viin_brand_common/static/src/webclient/settings_form_view/settings_form_view.scss'),
            ('after', 'web/static/src/views/fields/progress_bar/progress_bar_field.scss', 'viin_brand_common/static/src/legacy/scss/progress_bar.scss'),
            ('after', 'web/static/src/views/form/button_box/button_box.scss', 'viin_brand_common/static/src/views/form/button_box/button_box.scss'),
            ('after', 'web/static/src/webclient/webclient.js', 'viin_brand_common/static/src/webclient/webclient.js'),
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': ['web'],
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
