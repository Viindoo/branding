# -*- coding: utf-8 -*-
# Copyright 2016, 2017 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "ERPOnline Backend Theme",
    "summary": "Mobile backend theme for Odoo community",
    "version": "10.0.1.0.23",
    "category": "Theme/Backend",
    'author' : 'Openworx, T.V.T Marine Automation (aka TVTMA)',
    'website': 'https://www.tvtmarine.com',
    'live_test_url': 'https://v10demo-int.erponline.vn',
    'support': 'support@ma.tvtmarine.com',
	"description": """
		Backend theme for Odoo community edition, based on the Material/United Backend Theme by Openworx
    """,
	'images':[
        'images/erponline_theme_screen.png'
	],
    "license": "LGPL-3",
    "installable": True,
    "depends": [
	'web_responsive',
    ],
    "data": [
        'views/assets.xml',
        'views/res_company_view.xml',
        'views/users.xml',
        'views/sidebar.xml',
    ],
}

