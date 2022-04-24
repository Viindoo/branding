{
    'name': "Discuss Debranding for Viindoo",
    'name_vi_VN': "Thảo luận với Nhận diện Thương hiệu Viindoo",

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
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'viin_brand_common'],

    # always loaded
    'data': [
        'views/mail_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # mail branding
            ('after', 'mail/static/src/components/chat_window/chat_window.scss', 'viin_brand_mail/static/src/scss/chat_window.scss'),
            ('after', 'mail/static/src/components/chat_window_header/chat_window_header.scss', 'viin_brand_mail/static/src/scss/chat_window_header.scss'),
            ('after', 'mail/static/src/components/discuss_sidebar_mailbox/discuss_sidebar_mailbox.scss', 'viin_brand_mail/static/src/scss/discuss_sidebar_mailbox.scss'),
            ('after', 'mail/static/src/components/discuss_sidebar_category_item/discuss_sidebar_category_item.scss', 'viin_brand_mail/static/src/scss/discuss_sidebar_category_item.scss'),
            ('after', 'mail/static/src/components/message/message.scss', 'viin_brand_mail/static/src/scss/message.scss'),
            ('after', 'mail/static/src/components/partner_im_status_icon/partner_im_status_icon.scss', 'viin_brand_mail/static/src/scss/partner_im_status_icon.scss'),
            ('after', 'mail/static/src/components/thread_icon/thread_icon.scss', 'viin_brand_mail/static/src/scss/thread_icon.scss'),
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
