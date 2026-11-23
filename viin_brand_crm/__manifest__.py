{
    'name': "CRM Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module CRM",

    'summary': "Theme branding Viindoo for module CRM",
    'summary_vi_VN': "Giao diện brand Viindoo cho module CRM",

    'description': """
What it does
============
This module will change color navigate bar, button and logo,v.v in CRM following Viindoo's brand

It also hides the Odoo IAP settings of CRM (lead enrichment, lead mining, visits to leads) and the
Lead Sourcing entry of the Generate menu, and its Mail plugins entry names Viindoo.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi giao diện module CRM theo thương hiệu Viindoo

Module này cũng ẩn các thiết lập Odoo IAP của CRM
(làm giàu dữ liệu, khai thác khách hàng tiềm năng, lượt truy cập thành khách hàng tiềm năng)
và mục Lead Sourcing của menu Generate; mục Mail plugins của menu này gọi tên Viindoo.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_crm?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.4',

    # viin_brand: owns the hook that hides the upsell settings
    'depends': ['crm', 'viin_brand', 'viin_brand_digest'],

    'data': [
        'data/digest_data.xml',
        'data/ir_config_parameter_data.xml',
        'views/crm_lead_views.xml',
        'views/crm_team_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'viin_brand_crm/static/src/components/lead_generation_dropdown/lead_generation_dropdown.js',
            'viin_brand_crm/static/src/components/promote_mail_plugins_dialog/promote_mail_plugins_dialog.xml',
            'viin_brand_crm/static/src/js/tours/crm.js',
            'viin_brand_crm/static/src/views/crm_form/crm_pls_tooltip_button.xml',
        ],
        'web.assets_unit_tests': [
            'viin_brand_crm/static/tests/crm_debrand.test.js',
            'viin_brand_crm/static/tests/lead_generation_dropdown.test.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
