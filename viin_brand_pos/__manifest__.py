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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_brand_web', 'point_of_sale'],

    # always loaded
    'data': [
        'views/pos_assets_index.xml',
        'views/res_config_settings_views.xml',
        'views/report_saledetails_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # v19 asset-path repair (git-rebase PR #633 replay). Both dead entries this replaces
            # pointed at 18.0-era files (viin_brand_common's primary_variables.scss and
            # legacy/scss/bootstrap_overridden_common.scss) that commit a251e97 deleted when
            # viin_brand_common moved to the 19.0 brand_variables.scss SSOT.
            #
            # A bare ('prepend', '.../brand_variables.scss') here would be a NO-OP: that file is
            # already pulled into THIS SAME bundle automatically via
            # point_of_sale.base_app -> web._assets_helpers -> web._assets_primary_variables,
            # where viin_brand_web's own manifest anchors it 'before'
            # web/static/src/scss/primary_variables.scss. odoo/addons/base/models/ir_asset.py's
            # AssetPaths dedups by resolved file path (`if path not in self.memo`), so a second
            # directive on an already-included path never re-inserts it - and 'prepend' always
            # targets the bundle's fixed start index regardless of processing order, so it can
            # never pull an already-included file back to the front either. The only directive
            # that both (a) sees $o-brand-primary / $o-brand-secondary / $o-viin-chrome-base /
            # $o-viin-chrome-deep already defined and (b) still lands before every consumer of
            # $primary/$success/$danger in this bundle (web/static/src/scss/
            # bootstrap_overridden.scss, only reachable via later entries) is to anchor the new
            # POS-local bridge file 'after' brand_variables.scss's own (already-wired) position.
            # See static/src/scss/pos_variables.scss for the five variable bindings this repairs.
            ('after', 'viin_brand_web/static/src/scss/brand_variables.scss',
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
            # where viin_brand_web ships its error-dialog de-brand (the "Odoo Error" /
            # "Odoo Client Error" / "Odoo Network Error" headings, "Odoo Warning" fallbacks and the
            # session-expired dialog). Reuse those two files instead of copying them: they only
            # touch classes and templates of web/static/src/core/errors, which this bundle holds.
            'viin_brand_web/static/src/core/errors/error_dialogs.js',
            'viin_brand_web/static/src/core/errors/error_dialogs.xml',
            # What viin_brand_web's backend patches do not reach here: default Dialog title and the
            # generic error dialog's technical details.
            'viin_brand_pos/static/src/app/errors/dialog_default_title.js',
            'viin_brand_pos/static/src/app/errors/error_dialogs.js',
            'viin_brand_pos/static/src/app/screens/product_screen/product_screen.js',
            'viin_brand_pos/static/src/app/services/report_service.js',
        ],
        'point_of_sale.customer_display_assets': [
            # The public customer display page bundles its own subset of point_of_sale
            # (core's OdooLogo component and template included), not _assets_pos, so the
            # Viindoo logo extension and the IoT notice patch must be listed here as well.
            'viin_brand_pos/static/src/app/components/odoo_logo/odoo_logo.xml',
            'viin_brand_pos/static/src/customer_display/iot_notice.js',
            'viin_brand_pos/static/src/customer_display/customer_display_data_service.js',
            # Same error-dialog de-brand as the POS bundle above (this bundle is built from
            # web._assets_core too).
            'viin_brand_web/static/src/core/errors/error_dialogs.js',
            'viin_brand_web/static/src/core/errors/error_dialogs.xml',
            'viin_brand_pos/static/src/app/errors/dialog_default_title.js',
            'viin_brand_pos/static/src/app/errors/error_dialogs.js',
        ],
        'web.assets_backend': [
            # The printer checklist widget of the POS configuration form lives in the backend.
            'viin_brand_pos/static/src/backend/lna_checklist/lna_checklist.xml',
        ],
        'point_of_sale.assets_prod': [
            'viin_brand_pos/static/src/css/**/*',
        ],
        'web.assets_tests': [
            # Files in /static/tests/tours are loaded in the backend in test
            # mode - the same bundle core's own point_of_sale POS tours load
            # from (point_of_sale/__manifest__.py). Mirrors
            # ViinBrandPosSaverScreenLogoTour's own header comment.
            'viin_brand_pos/static/tests/tours/**/*',
        ],
        'web.assets_unit_tests_setup': [
            # The unit-test bundle merges the POS bundle with web.assets_backend, which no real page
            # does. Two files only make sense on one side of that merge:
            # - viin_brand_web's own dialog.js checks that the default Dialog title still holds the
            #   brand and console.errors when this module's POS-only patch got there first;
            # - core's backend lna_checklist template is removed from this bundle by point_of_sale
            #   (`remove` of src/backend/**), so an extension of it has no parent here.
            ('remove', 'viin_brand_pos/static/src/app/errors/dialog_default_title.js'),
            ('remove', 'viin_brand_pos/static/src/backend/lna_checklist/lna_checklist.xml'),
        ],
        'web.assets_unit_tests': [
            # navbar_favicon_guard.test.js mounts the REAL point_of_sale Navbar via
            # setupPosEnv()/mountWithCleanup() (point_of_sale's own web.assets_unit_tests_setup
            # bundle already loads the real navbar.js transitively through
            # point_of_sale.assets_prod -> point_of_sale._assets_pos, so no mock/stand-in is
            # needed or possible here - see the test file's header comment for the full grounding).
            # This entry is harmless redundancy (Odoo's module loader no-ops a duplicate define()).
            'viin_brand_pos/static/src/app/navbar/navbar.js',
            'viin_brand_pos/static/tests/navbar_favicon_guard.test.js',
            # The IoT notice swap lives in its own file because core's customer display service
            # is not part of the POS unit test bundle (point_of_sale removes customer_display/**).
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
