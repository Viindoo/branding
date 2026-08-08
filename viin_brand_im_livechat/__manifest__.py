{
    'name': "Live Chat Debranding for Viindoo",
    'name_vi_VN': "",

    'summary': """
Debranding Live Chat for Viindoo""",

    'summary_vi_VN': """
Làm lại màu sắc Live Chat theo thương hiệu Viindoo
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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_im_livechat?force_show=1",
    'live_test_url': "https://v18demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v18demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/Viindoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['im_livechat', 'viin_brand_common'],

    # always loaded
    'demo': [
        'data/im_livechat_channel_demo.xml',
        'data/im_livechat_support_bot_demo.xml',
    ],
    'assets': {
        # Regression guard for BUG S39-1: a now-removed override of
        # static/src/embed/common/livechat_button.xml used to reference
        # position.top/position.left/size, none of which exist on core's
        # LivechatButton, crashing the button's Owl render on every frontend
        # page. Wired into im_livechat's OWN 'im_livechat.embed_assets_unit_tests'
        # bundle - not the generic 'web.assets_unit_tests' - because only that
        # bundle's setup ('im_livechat.embed_assets_unit_tests_setup')
        # transitively includes 'im_livechat.assets_embed_core' (via
        # 'im_livechat.assets_embed_external'), the bundle a future override of
        # this template would also need to be wired into. See
        # static/tests/embed/livechat_button_debrand.test.js for the full
        # rationale.
        'im_livechat.embed_assets_unit_tests': [
            'viin_brand_im_livechat/static/tests/embed/livechat_button_debrand.test.js',
        ],
    },
    'data': [
        'data/digest_data.xml',
        'data/im_livechat_chatbot_data.xml',
        'data/mail_templates.xml',
        'views/im_livechat_channel_templates.xml',
        'views/im_livechat_channel_views.xml'
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
