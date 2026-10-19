{
    'name': "Point Of Sale Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Điểm Bán Lẻ",

    'summary': """
Theme branding Viindoo for module Point Of Sale """,
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Point Of Sale
""",

    'description': """
What it does
============
This module will change color in navigate bar, button and logo following Viindoo's brand


Editions Supported
==================
1. Community Edition
2. Viindoo Cloud

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thay đổi màu sắc của thanh điều hướng (navbar), các nút(button) và logo theo thương hiệu Viindoo


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Viindoo Cloud

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/18.0/viin_brand_pos?force_show=1",
    'live_test_url': "https://v18demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v18demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_brand_common', 'point_of_sale'],

    # always loaded
    'data': [
        'views/pos_assets_index.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            ('prepend', 'viin_brand_common/static/src/scss/primary_variables.scss'),
            ('prepend', 'viin_brand_common/static/src/legacy/scss/bootstrap_overridden_common.scss'),
            ('after', 'point_of_sale/static/src/scss/pos.scss', 'viin_brand_pos/static/src/scss/style.scss'),
            'viin_brand_pos/static/src/app/screens/receipt/order_receipt.xml',
            'viin_brand_pos/static/src/app/screens/saver_screen.xml',
            'viin_brand_pos/static/src/app/navbar/navbar.xml',
            'viin_brand_pos/static/src/app/navbar/navbar.js',
            ('after', 'point_of_sale/static/src/app/errors/error_handlers.js', 'viin_brand_pos/static/src/app/popups/offline_error_popup.js'),
            ('after', 'point_of_sale/static/src/app/errors/error_handlers.js', 'viin_brand_pos/static/src/app/popups/rpc_error_popup.js'),
            'viin_brand_pos/static/src/app/printer/base_printer.js',
        ],
        'point_of_sale.customer_display_assets': [
            'viin_brand_pos/static/src/customer_display/odoo_logo.xml',
            'viin_brand_pos/static/src/customer_display/customer_display_data_service.js',
        ],
        'point_of_sale.assets_prod': [
            'viin_brand_pos/static/src/css/**/*',
        ],
        'web.assets_unit_tests': [
            # A stand-in for point_of_sale/static/src/app/navbar/navbar.js registered under the
            # SAME module name (see mock_navbar_module.js for why): the real file drags in 9
            # transitive POS-app files (cashier_name, proxy_status, sync_popup,
            # sale_details_button, product_screen + its own large fan-out, input, order_tabs,
            # customer_display/utils, pos_hook) that are not part of this shared bundle and
            # cannot be added without pulling in effectively the whole POS UI tree.
            'viin_brand_pos/static/tests/mock_navbar_module.js',
            # the module under test - its only deps are the mock above and
            # @web/core/utils/patch, both resolvable in this bundle
            'viin_brand_pos/static/src/app/navbar/navbar.js',
            'viin_brand_pos/static/tests/navbar_favicon_guard.test.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
