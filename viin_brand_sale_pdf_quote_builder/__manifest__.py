{
    'name': "Quotation Builder Debranding for Viindoo",
    'name_vi_VN': "",

    'summary': """
Debranding Quotation Builder for Viindoo""",

    'summary_vi_VN': """
Làm lại màu sắc Quotation Builder theo thương hiệu Viindoo
        """,

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
    'website': "https://viindoo.com",
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/Viindoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_pdf_quote_builder'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_template_views.xml',
        'views/res_config_setting_views.xml',
    ],

    'images': [
        # 'static/description/main_screenshot.png'
        ],
    'installable': True,
    'auto_install': True, # set auto_install True after upgrading for v17 after upgrading for v17
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
