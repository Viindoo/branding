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
    'website': "https://viindoo.com/apps/app/19.0/viin_brand_spreadsheet",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['spreadsheet', 'viin_brand_web'],

    # always loaded
    # 'data': [
    #     'security/ir.model.access.csv',
    #     'views/views.xml',
    #     'views/templates.xml',
    # ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],

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
        ],
        'web.assets_tests': [
            'viin_brand_spreadsheet/static/tests/tours/test_spreadsheet_editor_action.js',
        ],
    },

    'images': [
        # 'static/description/main_screenshot.png',
        # 'static/description/another_screenshot_1.png',
        # 'static/description/another_screenshot_2.png',
        ],

    # The list of IDs of the project tasks in Viindoo Company's database that require
    # this module development.
    'task_ids': [
        # 1292, 1294,
        ],

    'installable': True,
    # If this module is a bridge module that integrates 2 or more other modules,
    # auto_install must be set to True.
    # In case this module is a module that provides additional functions / features,
    # it should be activated via a setting directive of the main application related
    # to these new functions / features.
    'auto_install': True,
    # 99.9 EURO is a good start for an application while bridge modules should be free of charge
    # as we usually have pricing for the others that are bridged by this module.
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
