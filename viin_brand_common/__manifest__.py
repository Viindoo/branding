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
    'website': "https://viindoo.com/apps/modules/18.0/viin_brand_common?force_show=1",
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.3.3',
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
        'web._assets_bootstrap_frontend': [
            ('after', 'web/static/src/scss/bootstrap_review_frontend.scss', 'viin_brand_common/static/src/scss/bootstrap_review_frontend.scss'),
        ],
        'web._assets_secondary_variables': [
            ('prepend', 'viin_brand_common/static/src/legacy/scss/secondary_variables.scss'),
        ],
        'web._assets_backend_helpers': [
            ('after', 'web/static/src/scss/bootstrap_overridden.scss', 'viin_brand_common/static/src/scss/bootstrap_overridden.scss'),
        ],
        'web._assets_helpers': [
            'viin_brand_common/static/src/legacy/scss/bootstrap_overridden_common.scss',
        ],
        'web._assets_core': [
            ('after', 'web/static/src/core/**/*', 'viin_brand_common/static/src/core/**/*'),
        ],
        # Brand SCSS leaks into web.assets_unit_tests_setup / web.tests_assets because both bundles
        # carry ('include', 'web.assets_backend') (addons/web/__manifest__.py), so core's own
        # Hoot/QUnit unit tests were measuring Viindoo's design tokens instead of core's own. Each
        # 'remove' below strips one of this module's own SCSS files back out of those two TEST-ONLY
        # bundles; web.assets_backend itself (the real webclient) is untouched - AssetPaths.remove()
        # operates on the accumulated per-bundle path list, not on the source bundle that
        # contributed it, so this is safe. A stale/renamed path here raises ValueError on module
        # update - keep that loud, never catch it
        # (odoo/addons/base/models/ir_asset.py AssetPaths._raise_not_found).
        'web.assets_unit_tests_setup': [
            ('remove', 'viin_brand_common/static/src/core/emoji_picker/emoji_picker.scss'),
            ('remove', 'viin_brand_common/static/src/core/file_viewer/file_viewer.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/bootstrap_overridden_common.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/navbar.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/progress_bar.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/secondary_variables.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/systray.scss'),
            ('remove', 'viin_brand_common/static/src/scss/bootstrap_overridden.scss'),
            ('remove', 'viin_brand_common/static/src/scss/primary_variables.scss'),
            ('remove', 'viin_brand_common/static/src/search/search_bar/search_bar.scss'),
            ('remove', 'viin_brand_common/static/src/search/search_panel/search_view.scss'),
            ('remove', 'viin_brand_common/static/src/views/fields/fields.scss'),
            ('remove', 'viin_brand_common/static/src/views/fields/statusbar/statusbar_field.scss'),
            ('remove', 'viin_brand_common/static/src/views/form/button_box/button_box.scss'),
            ('remove', 'viin_brand_common/static/src/webclient/navbar/navbar.scss'),
            ('remove', 'viin_brand_common/static/src/webclient/settings_form_view/settings_form_view.scss'),
            ('remove', 'viin_brand_common/static/src/webclient/webclient.scss'),
        ],
        # web.tests_assets is the legacy QUnit page (/web/tests/legacy, still executed by core's
        # WebSuite.test_qunit_desktop); it includes web.assets_backend the same way
        # web.assets_unit_tests_setup does, so it needs the identical remove list.
        'web.tests_assets': [
            ('remove', 'viin_brand_common/static/src/core/emoji_picker/emoji_picker.scss'),
            ('remove', 'viin_brand_common/static/src/core/file_viewer/file_viewer.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/bootstrap_overridden_common.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/navbar.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/progress_bar.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/secondary_variables.scss'),
            ('remove', 'viin_brand_common/static/src/legacy/scss/systray.scss'),
            ('remove', 'viin_brand_common/static/src/scss/bootstrap_overridden.scss'),
            ('remove', 'viin_brand_common/static/src/scss/primary_variables.scss'),
            ('remove', 'viin_brand_common/static/src/search/search_bar/search_bar.scss'),
            ('remove', 'viin_brand_common/static/src/search/search_panel/search_view.scss'),
            ('remove', 'viin_brand_common/static/src/views/fields/fields.scss'),
            ('remove', 'viin_brand_common/static/src/views/fields/statusbar/statusbar_field.scss'),
            ('remove', 'viin_brand_common/static/src/views/form/button_box/button_box.scss'),
            ('remove', 'viin_brand_common/static/src/webclient/navbar/navbar.scss'),
            ('remove', 'viin_brand_common/static/src/webclient/settings_form_view/settings_form_view.scss'),
            ('remove', 'viin_brand_common/static/src/webclient/webclient.scss'),
        ],
        'web.assets_unit_tests': [
            'viin_brand_common/static/tests/webclient_title.test.js',
        ],
        'web.assets_backend': [
            # common branding
            'viin_brand_common/static/src/legacy/scss/navbar.scss',
            'viin_brand_common/static/src/legacy/scss/systray.scss',
            ('after', 'web/static/src/core/emoji_picker/emoji_picker.scss', 'viin_brand_common/static/src/core/emoji_picker/emoji_picker.scss'),
            ('after', 'web/static/src/webclient/webclient.scss', 'viin_brand_common/static/src/webclient/webclient.scss'),
            ('after', 'web/static/src/search/search_panel/search_view.scss', 'viin_brand_common/static/src/search/search_panel/search_view.scss'),
            ('after', 'web/static/src/search/search_bar/search_bar.scss', 'viin_brand_common/static/src/search/search_bar/search_bar.scss'),
            ('after', 'web/static/src/webclient/settings_form_view/settings_form_view.scss', 'viin_brand_common/static/src/webclient/settings_form_view/settings_form_view.scss'),
            ('after', 'web/static/src/views/fields/progress_bar/progress_bar_field.scss', 'viin_brand_common/static/src/legacy/scss/progress_bar.scss'),
            ('after', 'web/static/src/views/fields/fields.scss', 'viin_brand_common/static/src/views/fields/fields.scss'),
            ('after', 'web/static/src/views/fields/statusbar/statusbar_field.scss', 'viin_brand_common/static/src/views/fields/statusbar/statusbar_field.scss'),
            ('after', 'web/static/src/views/form/button_box/button_box.scss', 'viin_brand_common/static/src/views/form/button_box/button_box.scss'),
            'viin_brand_common/static/src/webclient/navbar/navbar.scss',
            'viin_brand_common/static/src/webclient/user_menu_item.js',
            'viin_brand_common/static/src/views/widgets/**/*',
        ],
        'mail.assets_public': [
            ('after', 'web/static/src/core/emoji_picker/emoji_picker.scss', 'viin_brand_common/static/src/core/emoji_picker/emoji_picker.scss'),
        ],
        'im_livechat.assets_embed_core': [
            ('after', 'web/static/src/core/emoji_picker/emoji_picker.scss', 'viin_brand_common/static/src/core/emoji_picker/emoji_picker.scss'),
        ],
    },
    'installable': True,
    'post_load': 'post_load',
    'auto_install': ['web'],
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
