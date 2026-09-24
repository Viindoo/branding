{
    'name': "Website Debranding for Viindoo",
    'name_vi_VN': "",

    'summary': """
Debranding Website Builder for Viindoo""",

    'summary_vi_VN': """
Làm lại màu sắc Bộ công cụ dựng website theo thương hiệu Viindoo
        """,

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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_website?force_show=1",
    'live_test_url': "https://v18demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v18demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/Viindoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.2',

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/digest_data.xml',
        'views/templates.xml',
        'views/website_templates.xml',
        'views/res_config_settings_views.xml',
        'views/snippets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'viin_brand_website/static/src/components/configurator/configurator.scss',
            'viin_brand_website/static/src/components/website_loader/website_loader.scss',
        ],
        'web.assets_frontend': [
            'viin_brand_website/static/src/js/frontend_to_backend_apps_btn.js',
        ],
        'website.assets_editor': [
            'viin_brand_website/static/src/components/resource_editor/resource_editor_warning.xml',
        ],
        'website.website_builder_assets': [
            'viin_brand_website/static/src/builder/plugins/options/website_info_option.xml',
        ],
        'web.assets_tests': [
            'viin_brand_website/static/tests/tours/colorpicker_brand_override.js',
            'viin_brand_website/static/tests/tours/frontend_to_backend_apps_btn_wiring.js',
        ],
        'web.assets_unit_tests': [
            # frontend_to_backend_apps_btn.js is listed here so the Hoot suite's own `import` of
            # it resolves; the module's separate web.assets_frontend entry (production delivery
            # to a real website page) is added independently and is not this bundle's concern.
            'viin_brand_website/static/src/js/frontend_to_backend_apps_btn.js',
            'viin_brand_website/static/tests/js/frontend_to_backend_apps_btn.test.js',
        ],
    },
    'images': [
        # 'static/description/main_screenshot.png'
        ],
    'installable': True,
    'auto_install': True,
    # Brands websites that already existed when this module landed - a field
    # default cannot reach them. See __init__._brand_untouched_favicons.
    'post_init_hook': 'post_init_hook',
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
