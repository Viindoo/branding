{
    'name': "Discuss Debranding for Viindoo",
    'name_vi_VN': "Thảo luận với Nhận diện Thương hiệu Viindoo",
    'sequence': 145,

    'summary': """
Debranding Mail Discuss for Viindoo
    """,
    'summary_vi_VN': """
Làm lại mẫu mail của Thảo luận theo Thương hiệu Viindoo
    """,

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
    'website': "https://viindoo.com/apps/modules/18.0/viin_brand_mail?force_show=1",
    'live_test_url': "https://v18demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v18demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.7',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'viin_brand_common'],

    # always loaded
    'data': [
        'data/res_partner_data.xml',
        'data/discuss_channel_data.xml',
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
            ('after', 'mail/static/src/core/common/message_seen_indicator.scss', 'viin_brand_mail/static/src/core/common/message_seen_indicator.scss'),
            ('after', 'mail/static/src/core/public_web/discuss_sidebar.scss', 'viin_brand_mail/static/src/core/web/discuss_sidebar.scss'),
            ('after', 'mail/static/src/core/public_web/messaging_menu.scss', 'viin_brand_mail/static/src/core/web/messaging_menu.scss'),
            ('after', 'mail/static/src/discuss/core/public_web/discuss_sidebar_categories.scss', 'viin_brand_mail/static/src/discuss/core/web/discuss_sidebar_categories.scss'),
        ],
        'mail.assets_public': [
            ('after', 'mail/static/src/core/common/chat_window.scss', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('after', 'mail/static/src/core/common/im_status.scss', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('after', 'mail/static/src/core/common/composer.scss', 'viin_brand_mail/static/src/core/common/composer.scss'),
        ],
        'im_livechat.assets_embed_core': [
            ('after', 'mail/static/src/core/common/chat_window.scss', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('after', 'mail/static/src/core/common/im_status.scss', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('after', 'mail/static/src/core/common/composer.scss', 'viin_brand_mail/static/src/core/common/composer.scss'),
        ],
        # viin_brand_mail's own SCSS leaks into web.assets_unit_tests_setup / web.tests_assets via
        # web's ('include', 'web.assets_backend') (addons/web/__manifest__.py); each 'remove'
        # strips it back out of the two TEST-ONLY bundles so core's own mail/discuss Hoot/QUnit
        # tests measure core's own metrics, not Viindoo's. web.assets_backend itself (the real
        # webclient) is untouched - AssetPaths.remove() operates on the accumulated per-bundle
        # path list, not on the source bundle. A stale/renamed path here raises ValueError on
        # module update - keep that loud, never catch it
        # (odoo/addons/base/models/ir_asset.py AssetPaths._raise_not_found).
        'web.assets_unit_tests_setup': [
            ('remove', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/composer.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/core.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/message.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/message_seen_indicator.scss'),
            ('remove', 'viin_brand_mail/static/src/core/web/discuss_sidebar.scss'),
            ('remove', 'viin_brand_mail/static/src/core/web/messaging_menu.scss'),
            ('remove', 'viin_brand_mail/static/src/discuss/core/web/discuss_sidebar_categories.scss'),
        ],
        # web.tests_assets is the legacy QUnit page; it includes web.assets_backend the same way
        # web.assets_unit_tests_setup does, so it needs the identical remove list.
        'web.tests_assets': [
            ('remove', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/composer.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/core.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/message.scss'),
            ('remove', 'viin_brand_mail/static/src/core/common/message_seen_indicator.scss'),
            ('remove', 'viin_brand_mail/static/src/core/web/discuss_sidebar.scss'),
            ('remove', 'viin_brand_mail/static/src/core/web/messaging_menu.scss'),
            ('remove', 'viin_brand_mail/static/src/discuss/core/web/discuss_sidebar_categories.scss'),
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
