{
    'name': "Viindoo Brand - Spreadsheet Dashboard Dark",
    'name_vi_VN': "Viindoo Brand - Spreadsheet Dashboard Dark",

    'summary': """
Dark app shell for Spreadsheet Dashboards
    """,
    'summary_vi_VN': """
Khung ứng dụng tối cho Bảng thông tin Spreadsheet
    """,

    'description': """
What it does
============
Repaints the Spreadsheet Dashboards app shell (control panel, sidebar, dashboard-list hover
state) in Viindoo's dark app band for a dark-scheme user, while leaving the spreadsheet sheet
itself untouched.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Tô lại khung ứng dụng Bảng thông tin Spreadsheet (control panel, thanh bên, trạng thái hover
danh sách bảng thông tin) theo dải màu tối của Viindoo cho người dùng dùng giao diện tối, trong
khi vẫn giữ nguyên bảng tính bên trong.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/app/19.0/viin_brand_spreadsheet_dashboard",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.0',

    'depends': ['spreadsheet_dashboard', 'viin_brand_spreadsheet'],

    'assets': {
        'web.assets_web_dark': [
            'viin_brand_spreadsheet_dashboard/static/src/scss/dashboard_action_dark.dark.scss',
        ],
    },

    'images': [
        ],

    'task_ids': [
        ],

    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
