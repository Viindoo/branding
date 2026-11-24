{
    'name': "Discuss Debranding for Viindoo",
    'name_vi_VN': "Thảo luận với Nhận diện Thương hiệu Viindoo",
    'sequence': 145,

    'summary': "Debranding Mail Discuss for Viindoo",
    'summary_vi_VN': "Làm lại mẫu mail của Thảo luận theo Thương hiệu Viindoo",

    'description': """

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/modules/20.0/viin_brand_mail?force_show=1",
    'live_test_url': "https://v20demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v20demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.12',

    'depends': ['mail', 'viin_brand'],

    'data': [
        'data/res_partner_data.xml',
        'data/mail_templates_email_layouts.xml',
        'data/mail_groups.xml',
        'views/res_config_settings_views.xml',
        'views/discuss_public_templates.xml',
        'wizard/mail_compose_message_views.xml',
    ],
    'demo': [
        'data/discuss_channel_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # mail branding
            ('after', 'mail/static/src/core/common/core.scss', 'viin_brand_mail/static/src/core/common/core.scss'),
            ('after', 'mail/static/src/core/common/chat_window.scss', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('after', 'mail/static/src/core/common/im_status.scss', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('after', 'mail/static/src/core/common/composer.scss', 'viin_brand_mail/static/src/core/common/composer.scss'),
            ('after', 'mail/static/src/core/common/message.scss', 'viin_brand_mail/static/src/core/common/message.scss'),
            # Light-scheme contrast repair of the message metadata; the file guards itself to the light scheme.
            ('after', 'mail/static/src/core/common/message.scss', 'viin_brand_mail/static/src/core/common/message_contrast.scss'),
            ('after', 'mail/static/src/discuss/core/common/message_seen_indicator.scss', 'viin_brand_mail/static/src/core/common/message_seen_indicator.scss'),
            ('after', 'mail/static/src/core/public_web/notification_item.scss', 'viin_brand_mail/static/src/core/web/notification_item.scss'),
            # The web client of the Discuss app: permission toasts and the icon of a desktop
            # notification.
            ('after', 'mail/static/src/core/common/notification_permission_service.js', 'viin_brand_mail/static/src/core/common/notification_permission_service.js'),
            ('after', 'mail/static/src/core/common/out_of_focus_service.js', 'viin_brand_mail/static/src/core/common/out_of_focus_service.js'),
            # The two mail copies of web.StatusBarField are primary copies, which do not inherit
            # extensions registered after their own block, so each needs its own extension of the
            # numbered statusbar steps of viin_brand.
            'viin_brand_mail/static/src/views/fields/statusbar_duration/statusbar_steps_duration.xml',
        ],
        # Dark rules for what the dark palette does not reach. Plain appends land after core's own
        # mail `*.dark.scss` tail, so a same-specificity rule wins on source order.
        'web.assets_web_dark': [
            'viin_brand_mail/static/src/scss/mail_dark.scss',
            'viin_brand_mail/static/src/scss/action_panel.dark.scss',
        ],
        'web.assets_unit_tests': [
            'viin_brand_mail/static/tests/statusbar_steps_duration.test.js',
        ],
        'mail.assets_public': [
            ('after', 'mail/static/src/core/common/chat_window.scss', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('after', 'mail/static/src/core/common/im_status.scss', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('after', 'mail/static/src/core/common/composer.scss', 'viin_brand_mail/static/src/core/common/composer.scss'),
            ('after', 'mail/static/src/core/common/message.scss', 'viin_brand_mail/static/src/core/common/message_contrast.scss'),
            ('after', 'mail/static/src/core/common/notification_permission_service.js', 'viin_brand_mail/static/src/core/common/notification_permission_service.js'),
            ('after', 'mail/static/src/core/common/out_of_focus_service.js', 'viin_brand_mail/static/src/core/common/out_of_focus_service.js'),
            # The public pages of mail build on web._assets_core, so the dialogs and the error
            # dialogs of viin_brand are listed here.
            'viin_brand/static/src/core/dialog/dialog.js',
            'viin_brand/static/src/core/errors/error_dialogs.js',
            'viin_brand/static/src/core/errors/error_dialogs.xml',
        ],
        # The brand SCSS reaches the unit-test bundles through web's include of
        # web.assets_backend; removing it lets the core mail and discuss tests measure core's own
        # styles. A renamed path raises on update and must stay loud.
        'web.assets_unit_tests_setup': [
            ('remove', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/composer.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/core.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/message.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/message_contrast.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/message_seen_indicator.scss'),
            ('remove', 'viin_brand_mail/static/src/core/web/notification_item.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/notification_permission_service.js'),
            ('remove', 'viin_brand_mail/static/src/core/common/out_of_focus_service.js'),
        ],
    },
    'installable': True,
    'auto_install': True,
    'post_load': 'post_load',
    'post_init_hook': 'post_init_hook',
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
