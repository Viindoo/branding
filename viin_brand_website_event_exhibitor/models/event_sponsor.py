from odoo import models, api


class Sponsor(models.Model):
    _inherit = "event.sponsor"

    @api.onchange('exhibitor_type')
    def _onchange_exhibitor_type(self):
        for sponsor in self:
            if sponsor.exhibitor_type == 'online' and not sponsor.room_name:
                if sponsor.name:
                    room_name = "viindoo-exhibitor-%s" % sponsor.name
                else:
                    room_name = self.env['chat.room']._default_name(objname='exhibitor')
                sponsor.room_name = self._jitsi_sanitize_name(room_name)
        super()._onchange_exhibitor_type()
