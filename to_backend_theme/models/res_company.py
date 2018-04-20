# -*- coding: utf-8 -*-
# Copyright 2016, 2017 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    dashboard_background = fields.Binary(attachment=True)
    sidebar_visible = fields.Boolean(string="Show App Sidebar", default=False, help="Changing this will affect new users only.")
