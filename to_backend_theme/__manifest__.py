# -*- coding: utf-8 -*-
# Copyright 2016, 2017 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "ERPOnline Backend Theme",
    "summary": "Mobile backend theme for Odoo community",
    "version": "11.0.1.0.23",
    "category": "Themes/Backend",
    "website": "https://www.erponline.vn",
	"description": """
		Backend theme for Odoo community edition, based on the Material/United Backend Theme by Openworx
    """,
	'images':[
        'images/erponline_theme_screen.png'
	],
    "author": "Openworx, TVTMA",
    "license": "LGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        'web_responsive',
    ],
    "data": [
        'views/assets.xml',
        'views/res_company_view.xml',
        'views/users.xml',
        'views/sidebar.xml',
        'views/web.xml',
    ],
}

