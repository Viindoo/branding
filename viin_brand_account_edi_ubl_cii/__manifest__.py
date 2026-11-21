{
    'name': "Electronic Invoicing UBL/CII Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho module Hóa đơn điện tử UBL/CII",

    'summary': """
Theme branding Viindoo for module Electronic Invoicing UBL/CII""",
    'summary_vi_VN': """
Giao diện brand Viindoo cho module Hóa đơn điện tử UBL/CII
""",

    'description': """
What it does
============
This module brands as Viindoo the name of the invoice PDF that is generated for a vendor bill
received without one, and the name of its report. The metadata of the PDF documents, Factur-X
invoices included, is set by the Viindoo branding module.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này đặt thương hiệu Viindoo cho tên tệp PDF hóa đơn được tạo cho hóa đơn nhà cung cấp nhận về
không kèm PDF và cho tên báo cáo của nó. Siêu dữ liệu của các tệp PDF, gồm cả hóa đơn Factur-X,
do module thương hiệu Viindoo thiết lập.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_account_edi_ubl_cii?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'viin_brand' writes the metadata of the PDF documents that the tests of this module read.
    'depends': ['account_edi_ubl_cii', 'viin_brand'],

    # always loaded
    'data': [
        'report/account_edi_ubl_cii_report_templates.xml',
    ],

    # 'images': [
    #     'static/description/main_screenshot.png',
    #     'static/description/another_screenshot_1.png',
    #     'static/description/another_screenshot_2.png',
    # ],

    # The list of IDs of the project tasks in Viindoo Company's database that require
    # this module development.
    # 'task_ids': [
    #     1292, 1294,
    # ],

    'installable': False,
    # If this module is a bridge module that integrates 2 or more other modules,
    # auto_install must be set to True.
    # In case this module is a module that provides additional functions / features,
    # it should be activated via a setting directive of the main application related
    # to these new functions / features.
    # 'auto_install': True,  # TODO: Uncomment when upgrading module to production-ready status
    # 99.9 EURO is a good start for an application while bridge modules should be free of charge
    # as we usually have pricing for the others that are bridged by this module.
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
