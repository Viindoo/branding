{
    'name': "Viindoo Brand - Spreadsheet Chrome Dark",
    'name_vi_VN': "Viindoo Brand - Spreadsheet Chrome Dark",

    'summary': """Dark command chrome for the Community spreadsheet editor in Viindoo dark mode""",
    'summary_vi_VN': """Thanh lệnh tối cho trình soạn thảo bảng tính Community trong giao diện tối Viindoo""",

    'description': """
What it does
============
Repaints the CE spreadsheet editor's command chrome (menu bar, toolbar and sheet-tab bar) in
Viindoo's dark app band for a dark-scheme user, while the grid, side panels, chart figures and
every popover stay light like a document.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Tô lại thanh lệnh của trình soạn thảo bảng tính (thanh menu, thanh công cụ và thanh trang tính)
theo dải màu tối của Viindoo cho người dùng giao diện tối, trong khi lưới ô, bảng bên, biểu đồ và
mọi popover vẫn sáng như một tài liệu.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_spreadsheet",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.3',

    'depends': ['spreadsheet', 'viin_brand', 'viin_brand_mail'],

    'assets': {
        # Layer 1 re-points the one compile-time variable the engine's mobile chrome still reads;
        # anchored 'after' so it lands past the original declaration, which carries no `!default`
        # and would otherwise silently keep it. Layer 2 is a plain tail append - the desktop
        # topbar/bottombar backgrounds it repaints are runtime-injected by the engine itself, so
        # only its selectors' own specificity (never bundle position) decides the outcome.
        'web.assets_web_dark': [
            ('after', 'spreadsheet/static/src/o_spreadsheet/o_spreadsheet_variables.scss',
             'viin_brand_spreadsheet/static/src/scss/spreadsheet_chrome_dark.scss'),
            'viin_brand_spreadsheet/static/src/scss/spreadsheet_chrome_dark.dark.scss',
            # The mail Chatter embedded in the editor's side panel, on the engine's light tokens.
            # A plain append: it lands after viin_brand_mail's mail_dark.scss, whose bubble map it
            # reads.
            'viin_brand_spreadsheet/static/src/scss/spreadsheet_chatter_island.dark.scss',
        ],
        # The editor loads lazily as its own bundle. The core spreadsheet tests assert the stock
        # chart names, function categories and link placeholder, so the test bundle keeps core's
        # own; the dialog title patch only touches the spreadsheet dialog and stays.
        'spreadsheet.o_spreadsheet': [
            'viin_brand_spreadsheet/static/src/chart/odoo_chart_core_plugin.js',
            'viin_brand_spreadsheet/static/src/dialog/confirmation_dialog.js',
            'viin_brand_spreadsheet/static/src/functions/function_category.js',
            'viin_brand_spreadsheet/static/src/o_spreadsheet/link_editor.xml',
        ],
        'web.assets_unit_tests': [
            'viin_brand_spreadsheet/static/tests/spreadsheet_dialog_title_debrand.test.js',
            ('remove', 'viin_brand_spreadsheet/static/src/chart/odoo_chart_core_plugin.js'),
            ('remove', 'viin_brand_spreadsheet/static/src/functions/function_category.js'),
            ('remove', 'viin_brand_spreadsheet/static/src/o_spreadsheet/link_editor.xml'),
        ],
        'web.assets_tests': [
            'viin_brand_spreadsheet/static/tests/tours/test_spreadsheet_editor_action.js',
        ],
    },

    'installable': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
