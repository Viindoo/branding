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
    'version': '0.1.2',

    'depends': ['im_livechat', 'viin_brand', 'viin_brand_mail'],

    'demo': [
        'data/im_livechat_channel_demo.xml',
        'data/im_livechat_support_bot_demo.xml',
    ],
    'assets': {
        # im_livechat's embed drops core's title service from the frontend bundles that include it,
        # so the title patch of viin_brand that web.assets_frontend lists goes with it.
        'web.assets_frontend': [
            ('remove', 'viin_brand/static/src/core/browser/title_service.js'),
        ],
        'web.assets_backend': [
            ('after', 'im_livechat/static/src/core/web/livechat_channel_info_list.scss',
             'viin_brand_im_livechat/static/src/core/web/livechat_channel_info_list.scss'),
        ],
        # The dark bundle's `$purple` is the lighter Viindoo purple; core derives the label colour
        # from `lighten($purple, 15%)`, which is not a brand tone.
        'web.assets_web_dark': [
            'viin_brand_im_livechat/static/src/core/web/livechat_channel_info_list.dark.scss',
        ],
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
            ('after', 'mail/static/src/core/common/notification_permission_service.js', 'viin_brand_mail/static/src/core/common/notification_permission_service.js'),
            ('after', 'mail/static/src/core/common/out_of_focus_service.js', 'viin_brand_mail/static/src/core/common/out_of_focus_service.js'),
        ],
        # The embed bundle builds on web._assets_core and never includes web.assets_backend or
        # web.assets_frontend, so the dialogs and error dialogs of viin_brand are listed here.
        'im_livechat.assets_embed_external': [
            'viin_brand/static/src/core/dialog/dialog.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
        ],
    },
    'data': [
        'data/digest_data.xml',
        'data/im_livechat_chatbot_data.xml',
        'data/mail_templates.xml',
        'views/im_livechat_channel_templates.xml',
        'views/im_livechat_channel_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
