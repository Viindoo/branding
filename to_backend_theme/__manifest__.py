# -*- coding: utf-8 -*-
# Copyright 2016, 2019 Openworx - Mario Gielissen
# Copyright 2012, 2019 Openworx - T.V.T Marine Automation
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Viindoo Backend Theme",
    "summary": "Mobile backend theme for Odoo community",
    "version": "13.0.1.0.23",
    "category": "Website/Theme/Backend",
    'author': 'Openworx, Viindoo',
    'website': 'https://www.erponline.vn',
    'live_test_url': 'https://v13demo-int.erponline.vn',
    'support': 'apps.support@viindoo.com',
	"description": """Backend theme for Viindoo, based on the Openworx Backend Theme""",
	'images':[
        'images/screen.png'
	],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": ['web'],
    "depends": [
        'web',
        'web_editor',
        'web_responsive',
        'viin_brand_common',
    ],
    "data": [
        'views/assets.xml',
		'views/res_company_view.xml',
		# 'views/users.xml',
        # 'views/sidebar.xml',
    ],
}

