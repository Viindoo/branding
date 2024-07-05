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
    'website': "https://viindoo.com",
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.1',

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
            ('after', 'mail/static/src/core/common/chat_window.scss', 'viin_brand_mail/static/src/core/common/chat_window.scss'),
            ('after', 'mail/static/src/core/common/core.scss', 'viin_brand_mail/static/src/core/common/core.scss'),
            ('after', 'mail/static/src/core/common/im_status.scss', 'viin_brand_mail/static/src/core/common/im_status.scss'),
            ('after', 'mail/static/src/core/web/discuss_sidebar.scss', 'viin_brand_mail/static/src/core/web/discuss_sidebar.scss'),
            ('after', 'mail/static/src/discuss/core/web/discuss_sidebar_categories.scss', 'viin_brand_mail/static/src/discuss/core/web/discuss_sidebar_categories.scss'),
        ],
    },
    'installable': True,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
