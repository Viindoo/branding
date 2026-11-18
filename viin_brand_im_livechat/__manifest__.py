{
    'name': "Live Chat Debranding for Viindoo",
    'name_vi_VN': "Làm lại nhận diện thương hiệu cho Live Chat",

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
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1.1',

    'depends': ['im_livechat', 'viin_brand_mail'],

    'demo': [
        'data/im_livechat_channel_demo.xml',
        'data/im_livechat_support_bot_demo.xml',
    ],
    'assets': {
        # im_livechat's embed test bundle transitively includes 'im_livechat.assets_embed_core',
        # which this module extends; 'web.assets_unit_tests' does not.
        'im_livechat.embed_assets_unit_tests': [
            'viin_brand_im_livechat/static/tests/embed/livechat_button_debrand.test.js',
        ],
        'im_livechat.assets_embed_core': [
            ('after', 'mail/static/src/core/common/chat_window.scss', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('after', 'mail/static/src/core/common/im_status.scss', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('after', 'mail/static/src/core/common/composer.scss', 'viin_brand_mail/static/src/core/common/composer.scss'),
            ('after', 'mail/static/src/core/common/message.scss', 'viin_brand_mail/static/src/core/common/message_contrast.scss'),
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
