from odoo import models


class ChatRoom(models.Model):
    _inherit = 'chat.room'

    def _default_name(self, objname='room'):
        res = super()._default_name(objname=objname)
        if 'odoo' in res:
            res = res.replace('odoo', 'viindoo')
        return res
