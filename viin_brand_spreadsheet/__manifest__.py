{
    'name': "Spreadsheet Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho Bảng tính",

    'summary': """Viindoo palette and wording for the Community spreadsheet editor, in light and dark mode""",
    'summary_vi_VN': """Bảng màu và cách gọi tên Viindoo cho trình soạn thảo bảng tính Community, ở chế độ sáng và tối""",

    'description': """
What it does
============
Gives the Community spreadsheet editor the Viindoo palette in light and dark mode: the primary
button, the links and, in dark mode, the whole command chrome (menu bar, toolbar and sheet-tab bar)
come from the Viindoo colours. The names of the product in the editor (chart names, function
categories and help, dialog titles, link placeholder, error message) name Viindoo.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Đưa bảng màu Viindoo vào trình soạn thảo bảng tính Community ở chế độ sáng và tối: nút chính, liên
kết và, ở chế độ tối, toàn bộ thanh lệnh (thanh menu, thanh công cụ và thanh trang tính) theo màu
Viindoo. Mọi chỗ trình soạn thảo gọi tên sản phẩm (tên biểu đồ, nhóm và trợ giúp của hàm, tiêu đề hộp
thoại, ví dụ trong ô liên kết, thông báo lỗi) đều là Viindoo.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_spreadsheet",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.3',

    'depends': ['spreadsheet', 'viin_brand', 'viin_brand_mail'],

    'assets': {
        # The engine reads these custom properties for every colour of its chrome, so one block
        # after its stylesheet repaints the editor in both schemes, and in the public readonly
        # spreadsheet page.
        'web.assets_backend': [
            ('after', 'spreadsheet/static/src/o_spreadsheet/o_spreadsheet.css',
             'viin_brand_spreadsheet/static/src/css/spreadsheet_tokens.css'),
        ],
        'spreadsheet.public_spreadsheet': [
            ('after', 'spreadsheet/static/src/o_spreadsheet/o_spreadsheet.css',
             'viin_brand_spreadsheet/static/src/css/spreadsheet_tokens.css'),
        ],
        # The editor loads lazily as its own bundle. The core spreadsheet tests assert the stock
        # chart names, function categories, link placeholder and error text, so the test bundle
        # keeps core's own; the dialog title patch only touches the spreadsheet dialog and stays.
        'spreadsheet.o_spreadsheet': [
            'viin_brand_spreadsheet/static/src/chart/odoo_chart_core_plugin.js',
            'viin_brand_spreadsheet/static/src/chart/chart_menu.js',
            'viin_brand_spreadsheet/static/src/data_sources/server_data.js',
            'viin_brand_spreadsheet/static/src/dialog/spreadsheet_dialog_title.js',
            'viin_brand_spreadsheet/static/src/functions/function_category.js',
            'viin_brand_spreadsheet/static/src/o_spreadsheet/link_editor.xml',
        ],
        'web.assets_unit_tests': [
            'viin_brand_spreadsheet/static/tests/spreadsheet_dialog_title_debrand.test.js',
            ('remove', 'viin_brand_spreadsheet/static/src/chart/odoo_chart_core_plugin.js'),
            ('remove', 'viin_brand_spreadsheet/static/src/chart/chart_menu.js'),
            ('remove', 'viin_brand_spreadsheet/static/src/data_sources/server_data.js'),
            ('remove', 'viin_brand_spreadsheet/static/src/functions/function_category.js'),
            ('remove', 'viin_brand_spreadsheet/static/src/o_spreadsheet/link_editor.xml'),
        ],
        'web.assets_tests': [
            'viin_brand_spreadsheet/static/tests/tours/test_spreadsheet_editor_action.js',
        ],
    },

    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
