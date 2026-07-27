# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Per-user home-menu app ordering (PR #658 item 7): a comma-separated list of app ROOT-MENU
    # xmlids in the user's preferred tile order. Empty (default) means "use the menu-service default
    # sequence". Stored as portable xmlids (not integer menu ids) so the order survives DB
    # restore/reinstall - the same SSOT the tours and clickbot key on. Machine-written by the home
    # menu's drag-reorder only (never user-typed), so no @api.constrains on the format is needed; the
    # JS read path parses it defensively (unknown xmlids ignored, missing apps appended in default
    # sequence), so a stale value can never hide an accessible app. The 'viin_' prefix mirrors
    # viin_color_scheme (viin_brand_common).
    viin_home_app_order = fields.Char(
        string="Home App Order",
        help="Comma-separated application root-menu xmlids giving this user's preferred home-menu "
             "tile order. Empty falls back to the default application sequence.",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        # A user may read their own home-menu app order (no admin rights needed). Composes additively
        # with viin_brand_common's own SELF_READABLE_FIELDS override through the MRO.
        return super().SELF_READABLE_FIELDS + ['viin_home_app_order']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        # A user may set their OWN home-menu app order; the SELF scope pins the write to the current
        # user, so writing another user's order still raises AccessError.
        return super().SELF_WRITEABLE_FIELDS + ['viin_home_app_order']
