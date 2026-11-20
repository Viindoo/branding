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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_pos?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.3',

    'depends': ['viin_brand', 'point_of_sale'],

    'data': [
        'data/pos_config_data.xml',
        'views/pos_assets_index.xml',
        'views/res_config_settings_views.xml',
        'views/report_saledetails_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # The brand variables already reach this bundle through web._assets_primary_variables,
            # and a repeated directive on an included path is ignored, so the bridge file is
            # anchored after the brand file instead.
            ('after', 'viin_brand/static/src/scss/brand_variables.scss',
             'viin_brand_pos/static/src/scss/pos_variables.scss'),
            ('after', 'point_of_sale/static/src/scss/pos.scss', 'viin_brand_pos/static/src/scss/style.scss'),
            'viin_brand_pos/static/src/app/screens/receipt/order_receipt.xml',
            'viin_brand_pos/static/src/app/screens/saver_screen.xml',
            'viin_brand_pos/static/src/app/navbar/navbar.xml',
            'viin_brand_pos/static/src/app/components/odoo_logo/odoo_logo.xml',
            'viin_brand_pos/static/src/app/navbar/navbar.js',
            ('after', 'point_of_sale/static/src/app/utils/error_handlers.js', 'viin_brand_pos/static/src/app/popups/offline_error_popup.js'),
            ('after', 'point_of_sale/static/src/app/utils/error_handlers.js', 'viin_brand_pos/static/src/app/popups/rpc_error_popup.js'),
            # Core also builds the "Odoo Server Error" dialog outside the registry handler:
            # exported handleRPCError (payment validation) and the cash move deletion.
            'viin_brand_pos/static/src/app/utils/order_payment_validation.js',
            'viin_brand_pos/static/src/app/components/popups/cash_move_popup/cash_move_list_popup/cash_move_list_popup.js',
            # The POS bundles are built from web._assets_core and never include web.assets_backend,
            # so the dialog de-brand of viin_brand is listed here: it only touches classes and
            # templates that this bundle holds.
            'viin_brand/static/src/core/dialog/dialog.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
            # The camera permission sentence of every consumer of BarcodeVideoScanner.
            'viin_brand/static/src/core/barcode/barcode_video_scanner.js',
            'viin_brand_pos/static/src/app/services/report_service.js',
        ],
        'point_of_sale.customer_display_assets': [
            # The public customer display page bundles its own subset of point_of_sale
            # (core's OdooLogo component and template included), not _assets_pos, so the
            # Viindoo logo extension and the IoT notice patch must be listed here as well.
            'viin_brand_pos/static/src/app/components/odoo_logo/odoo_logo.xml',
            'viin_brand_pos/static/src/customer_display/iot_notice.js',
            'viin_brand_pos/static/src/customer_display/customer_display_data_service.js',
            'viin_brand/static/src/core/dialog/dialog.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
        ],
        'web.assets_backend': [
            # The printer checklist widget of the POS configuration form lives in the backend.
            'viin_brand_pos/static/src/backend/lna_checklist/lna_checklist.xml',
        ],
        'web.assets_tests': [
            # Tours load in the backend in test mode, like the tours of point_of_sale.
            'viin_brand_pos/static/tests/tours/**/*',
        ],
        'web.assets_unit_tests_setup': [
            # point_of_sale removes its backend templates from this bundle, so an extension of
            # the lna_checklist template has no parent here.
            ('remove', 'viin_brand_pos/static/src/backend/lna_checklist/lna_checklist.xml'),
        ],
        'web.assets_unit_tests': [
            # navbar_favicon_guard.test.js mounts the real navbar, which the unit bundle already
            # loads through point_of_sale._assets_pos; the listing is a harmless duplicate.
            'viin_brand_pos/static/src/app/navbar/navbar.js',
            'viin_brand_pos/static/tests/navbar_favicon_guard.test.js',
            # The IoT notice lives in its own file because point_of_sale removes customer_display/** from the unit bundle.
            'viin_brand_pos/static/src/customer_display/iot_notice.js',
            'viin_brand_pos/static/tests/pos_error_debrand.test.js',
            'viin_brand_pos/static/tests/pos_core_wording_debrand.test.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
