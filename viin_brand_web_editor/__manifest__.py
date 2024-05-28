# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Viindoo Debranding Web Editor',
    'category': 'Hidden',
    'description': """
""",
    'depends': ['web_editor'],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            ('after', 'web_editor/static/src/scss/web_editor.common.scss', 'viin_brand_web_editor/static/src/scss/web_editor.common.scss'),
        ],
        'web.assets_frontend': [
            ('after', 'web_editor/static/src/scss/web_editor.common.scss', 'viin_brand_web_editor/static/src/scss/web_editor.common.scss'),
        ],
        'web.report_assets_common': [
            ('after', 'web_editor/static/src/scss/web_editor.common.scss', 'viin_brand_web_editor/static/src/scss/web_editor.common.scss'),
        ],
    },
    'auto_install': True,
    'license': 'LGPL-3',
}
