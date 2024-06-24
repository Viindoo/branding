from odoo import fields, models


class ImLivechatChannel(models.Model):
    _inherit = ['im_livechat.channel']

    header_background_color = fields.Char(default="#00a4b5")
    button_background_color = fields.Char(default="#7f4282")
