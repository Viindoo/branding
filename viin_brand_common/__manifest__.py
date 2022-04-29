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
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
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
    'assets' : {
        'web._assets_primary_variables' : [
            'viin_brand_common/static/src/legacy/scss/primary_variables.scss',
        ],
        'web._assets_secondary_variables' : [
            ('prepend','viin_brand_common/static/src/legacy/scss/secondary_variables.scss'),
        ],
        'web._assets_backend_helpers' : [
            ('replace','web/static/src/legacy/scss/bootstrap_overridden.scss','viin_brand_common/static/src/legacy/scss/bootstrap_overridden.scss'),
        ],
        'web._assets_helpers' : [
            'viin_brand_common/static/src/legacy/scss/bootstrap_overridden_common.scss'
        ],
        'web.assets_common' : [
            'viin_brand_common/static/src/legacy/scss/navbar.scss',
            'viin_brand_common/static/src/legacy/scss/systray.scss'
        ],
        'web.assets_backend' : [
            # common branding
            ('after','web/static/src/legacy/scss/fields_extra.scss','viin_brand_common/static/src/legacy/scss/fields_extra.scss'),
            ('after','web/static/src/legacy/scss/form_view_extra.scss','viin_brand_common/static/src/legacy/scss/form_view_extra.scss'),
            ('after','web/static/src/legacy/scss/kanban_view.scss','viin_brand_common/static/src/legacy/scss/kanban_view.scss'),
            ('after','web/static/src/search/search_panel/search_view_extra.scss','viin_brand_common/static/src/search/search_panel/search_view.scss'),
            ('after','base/static/src/scss/onboarding.scss','viin_brand_common/static/src/scss/onboarding.scss'),
            ('after','web/static/src/legacy/scss/base_settings.scss','viin_brand_common/static/src/legacy/scss/base_settings.scss'),
            ('after','web/static/src/legacy/scss/progress_bar.scss','viin_brand_common/static/src/legacy/scss/progress_bar.scss'),
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': ['web'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
