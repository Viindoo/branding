{
    'name': "Lead Enrichment Branding For Viindoo",
    'name_vi_VN': "Giao diện Viindoo cho mô-đun Lead Enrichment",

    'summary': "Keeps the paid Lead Enrichment service of Odoo S.A. out of the way",
    'summary_vi_VN': "Giữ dịch vụ Lead Enrichment trả phí của Odoo S.A. ở trạng thái không hoạt động",

    'description': """
What it does
============
This module switches off the scheduled action of Lead Enrichment, a paid service operated by Odoo S.A., and keeps its
server action out of the Action menu of the leads. The module stays installed.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này tắt hành động theo lịch của Lead Enrichment, dịch vụ trả phí do Odoo S.A. vận hành, và giữ hành động máy chủ của
nó ngoài menu Hành động của khách hàng tiềm năng. Mô-đun vẫn được giữ nguyên trạng thái đã cài.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_crm_iap_enrich",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    # 'demo_video_url': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    # 'demo_video_url_vi_VN': "https://www.youtube.com/watch?v=xa8pxRnZpWs",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/20.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['crm_iap_enrich', 'viin_brand'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
    ],

    'installable': True,
    # If this module is a bridge module that integrates 2 or more other modules,
    # auto_install must be set to True.
    # In case this module is a module that provides additional functions / features,
    # it should be activated via a setting directive of the main application related
    # to these new functions / features.
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
