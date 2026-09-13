{
    'name': "Viindoo Branding",
    'name_vi_VN': "Ứng dụng với thương hiệu Viindoo",

    'summary': """
Set Viindoo Brandings.
""",

    'summary_vi_VN': """
Thiết lập thương hiệu Viindoo.
        """,

    'description': """
This module change some information for Viindoo branding

* Replace Odoo's module icons and favicon with Viindoo's

  * icons live in `viin_brand/static/img/apps/<module_name>.png`, or in a
    module named `viin_brand_<module_name>` shipping `static/description/icon.png`
  * the favicon lives in `viin_brand/static/img/favicon.ico` and is applied to every company
  * load the module server wide (`--load=base,web,viin_brand`) so the branding
    is in place from the first module installation


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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    # 0.1 -> 0.2: this module now OWNS the module-icon/favicon branding mechanism
    # (moved out of tvtmaaddons' to_base, 18.0 f57498c/56b2c7252e), so it gains
    # models, data, views, assets and four hooks. It needs -u to take effect.
    'version': '0.2',
    # 'web': load-order dependency, NOT unused - controllers/database.py does
    # `from odoo.addons.web.controllers.database import Database` at MODULE-LOAD
    # time to subclass the database-manager controller. Do not remove.
    # 'base_setup': views/res_config_settings_views.xml xpaths into
    # base_setup.res_config_settings_view_form.
    'depends': ['base', 'web', 'base_setup'],
    'data': [
        'data/viin_brand_data.xml',
        'data/res_company_data.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'viin_brand/static/src/webclient/*',
            'viin_brand/static/src/js/settings_page.js',
            'viin_brand/static/src/xml/settings_page.xml',
        ],
        'web.tests_assets': [
            'viin_brand/static/tests/viin_brand_mock_server.js',
        ],
    },
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'post_load': 'post_load',
    'installable': True,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
