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
    'website': "https://viindoo.com/apps/modules/19.0/viin_brand_mail?force_show=1",
    'live_test_url': "https://v19demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v19demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.6',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'viin_brand_web'],

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
            # Light-scheme AA repair of the message METADATA tier (timestamp, in-body muted
            # markers, the two opacity-thinned nodes). Rides every bundle a mail message renders
            # in; guarded to the light scheme inside the file, so the dark bundle this one is
            # recompiled into emits none of it. See message_contrast.scss.
            ('after', 'mail/static/src/core/common/message.scss', 'viin_brand_mail/static/src/core/common/message_contrast.scss'),
            ('after', 'mail/static/src/discuss/core/common/message_seen_indicator.scss', 'viin_brand_mail/static/src/core/common/message_seen_indicator.scss'),
            ('after', 'mail/static/src/core/public_web/discuss_sidebar.scss', 'viin_brand_mail/static/src/core/web/discuss_sidebar.scss'),
            ('after', 'mail/static/src/core/public_web/messaging_menu.scss', 'viin_brand_mail/static/src/core/web/messaging_menu.scss'),
            ('after', 'mail/static/src/discuss/core/public_web/discuss_sidebar_categories.scss', 'viin_brand_mail/static/src/discuss/core/web/discuss_sidebar_categories.scss'),
            # 2026-08-03: carry viin_brand_web's numbered statusbar steps onto mail's two
            # PRIMARY copies of web.StatusBarField (statusbar_duration and the CRM
            # rotting_statusbar_duration). A primary copy does not inherit extensions registered
            # after its own blockId, so each copy needs its own attributes-only extension - see the
            # file header. Plain append: template extensions are order-immune here (both xpaths
            # only set attributes, and re-setting them is idempotent).
            'viin_brand_mail/static/src/views/fields/statusbar_duration/statusbar_steps_duration.xml',
        ],
        # M-1 (PR #658): mail-owned dark surfaces the recompiled dark palette (C-2) cannot reach -
        # core `mail` sculpts them from the raw Bootstrap grayscale ramp / literals no overridable
        # Sass var touches, in BOTH its light *.scss AND its own *.dark.scss tail, so they do NOT
        # recompile dark-correct (rotting kanban card, chatter timestamp, and the Discuss sidebar /
        # messaging-menu / conversation-header surfaces). Core's dark tail glob is web/mail-only,
        # never this module, so this file is contributed EXPLICITLY here. A PLAIN APPEND (no anchor)
        # lands it at the very END of web.assets_web_dark - after core's own mail *.dark.scss tail
        # (viin_brand_mail loads after mail) - so every same-specificity override in it wins on
        # source order, which several Discuss surfaces re-pointed by core's dark tail require. See
        # static/src/scss/mail_dark.scss.
        'web.assets_web_dark': [
            'viin_brand_mail/static/src/scss/mail_dark.scss',
        ],
        'mail.assets_public': [
            ('after', 'mail/static/src/core/common/chat_window.scss', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('after', 'mail/static/src/core/common/im_status.scss', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('after', 'mail/static/src/core/common/composer.scss', 'viin_brand_mail/static/src/core/common/composer.scss'),
            ('after', 'mail/static/src/core/common/message.scss', 'viin_brand_mail/static/src/core/common/message_contrast.scss'),
        ],
        'im_livechat.assets_embed_core': [
            ('after', 'mail/static/src/core/common/chat_window.scss', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('after', 'mail/static/src/core/common/im_status.scss', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('after', 'mail/static/src/core/common/composer.scss', 'viin_brand_mail/static/src/core/common/composer.scss'),
            ('after', 'mail/static/src/core/common/message.scss', 'viin_brand_mail/static/src/core/common/message_contrast.scss'),
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
            # 19.0-only file (the port's message-contrast fix), added after the 18.0 sweep
            # drew this list - without it one brand stylesheet still reached core's pages.
            ('remove', 'viin_brand_mail/static/src/core/common/message_contrast.scss'),
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
            # 19.0-only file (the port's message-contrast fix), added after the 18.0 sweep
            # drew this list - without it one brand stylesheet still reached core's pages.
            ('remove', 'viin_brand_mail/static/src/core/common/message_contrast.scss'),
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
