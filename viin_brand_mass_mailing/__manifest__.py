{
    'name': "Email Marketing Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Email Marketing",

    'summary': "Theme branding Viindoo for module Email Marketing",
    'summary_vi_VN': "Giao diện brand Viindoo cho module Email Marketing",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in Email Marketing following Viindoo's brand

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện các module Email Marketing theo thương hiệu Viindoo

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_mass_mailing?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.2',

    'depends': ['mass_mailing', 'viin_brand'],

    'data': [
        'views/mailing_mailing_views.xml',
        'views/mailing_list_views.xml',
        'views/res_config_settings_views.xml',
        'views/mailing_templates_portal_layouts.xml',
        'views/mailing_view_generic.xml',
        'views/themes_templates_blocks.xml',
    ],
    'demo': [
        'demo/mailing_trace_demo.xml',
    ],
    'assets': {
        'mass_mailing.assets_builder': [
            'viin_brand_mass_mailing/static/src/snippets/mass_mailing_snippets.xml',
            'viin_brand_mass_mailing/static/src/builder/components/company_update_dialog.js',
            'viin_brand_mass_mailing/static/src/builder/plugins/social_media_option_plugin.js',
        ],
        'web.assets_unit_tests': [
            'viin_brand_mass_mailing/static/tests/**/*',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
