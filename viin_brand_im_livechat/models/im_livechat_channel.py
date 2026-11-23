from odoo import fields, models

from odoo.addons.viin_brand.controllers.webmanifest import VIINDOO_BRAND_COLOR


class ImLivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'

    header_background_color = fields.Char(default=VIINDOO_BRAND_COLOR)
    button_background_color = fields.Char(default=VIINDOO_BRAND_COLOR)
