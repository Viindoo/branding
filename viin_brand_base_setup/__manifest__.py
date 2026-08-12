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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_base_setup?force_show=1",
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.3',
    # Renamed to viin_brand_base_setup for 19.0: wave 1 of this module-boundary refactor moved
    # this module's entire web-client half into viin_brand_web, leaving only the base/base_setup
    # de-brand behind. `old_technical_name` is a truthful marker of that rename plus the to_base
    # test_lint manifest-key whitelist entry (to_base/__init__.py:235) - it performs NO
    # install-state migration; core Odoo reads this key nowhere.
    'old_technical_name': 'viin_brand_common',
    # base_setup is a HARD dependency, not a convenience: views/res_config_settings_views.xml
    # resolves ref="base_setup.res_config_settings_view_form" at load time. base_setup is
    # auto_install with depends base+web, i.e. the SAME graph depth as this module, so without the
    # explicit edge the loader does not guarantee it lands first and the install fails
    # intermittently with ValueError: External ID not found in the system.
    'depends': ['base_setup', 'viin_brand'],
    'data': [
        'views/ir_module_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
