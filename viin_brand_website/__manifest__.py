{
    'name': "Website Debranding for Viindoo",
    'name_vi_VN': "Làm lại nhận diện thương hiệu cho Website",

    'summary': "Debranding Website Builder for Viindoo",

    'summary_vi_VN': "Làm lại màu sắc Bộ công cụ dựng website theo thương hiệu Viindoo",

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
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_website?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.5',

    # viin_brand owns the Apps action domain that data/ir_module_module_data.xml re-applies
    'depends': ['website', 'viin_brand'],

    'data': [
        'data/digest_data.xml',
        'data/ir_module_module_data.xml',
        'views/templates.xml',
        'views/website_templates.xml',
        'views/res_config_settings_views.xml',
        'views/snippets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'viin_brand_website/static/src/components/website_loader/website_loader.scss',
        ],
        'web.assets_frontend': [
            'viin_brand_website/static/src/js/frontend_to_backend_apps_btn.js',
        ],
        'website.assets_editor': [
            'viin_brand_website/static/src/components/dialog/seo_brand.xml',
            'viin_brand_website/static/src/components/resource_editor/resource_editor_warning.xml',
        ],
        'website.assets_inside_builder_iframe': [
            'viin_brand_website/static/src/builder/plugins/options/countdown_brand.edit.xml',
        ],
        'website.website_builder_assets': [
            'viin_brand_website/static/src/builder/plugins/options/website_info_option.xml',
            'viin_brand_website/static/src/builder/plugins/options/website_builder_brand.xml',
            'viin_brand_website/static/src/builder/plugins/options/facebook_option_plugin.js',
        ],
        'web.assets_tests': [
            'viin_brand_website/static/tests/tours/frontend_to_backend_apps_btn_wiring.js',
        ],
        'web.assets_unit_tests': [
            # The Hoot suite imports the file, so the unit-test bundle carries it as well.
            'viin_brand_website/static/src/js/frontend_to_backend_apps_btn.js',
            'viin_brand_website/static/tests/js/frontend_to_backend_apps_btn.test.js',
            # The suite reads the end message template of the countdown, which the builder bundle leaves out.
            'website/static/src/builder/plugins/options/countdown.edit.xml',
            'viin_brand_website/static/src/builder/plugins/options/countdown_brand.edit.xml',
            'viin_brand_website/static/tests/builder/website_builder_brand.test.js',
            # Core's builder tests compare the computed palette with core's own colours, read from
            # the production frontend bundle the builder iframe loads, which must stay branded.
            # Each copy is the core file with the literals the brand changes realigned
            # (tests/test_core_test_copies.py keeps it equal to core otherwise).
            ('replace', 'website/static/tests/builder/s_tabs.test.js',
             'viin_brand_website/static/tests/builder/core_copies/s_tabs.test.js'),
            ('replace', 'website/static/tests/builder/image_shape.test.js',
             'viin_brand_website/static/tests/builder/core_copies/image_shape.test.js'),
        ],
    },
    'installable': True,
    'auto_install': True,
    # Brands the favicon of websites a field default cannot reach (see __init__._brand_untouched_favicons).
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
