# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Menu xmlids rather than ids, so the order survives a database restore.
    viin_home_app_order = fields.Char(
        string="Home App Order",
        help="Comma-separated application root-menu xmlids giving this user's preferred home-menu "
             "tile order. Empty falls back to the default application sequence.",
        user_writeable=True,
    )
