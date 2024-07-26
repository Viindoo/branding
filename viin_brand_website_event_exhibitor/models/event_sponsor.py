from odoo import models, api


class Sponsor(models.Model):
    _inherit = "event.sponsor"

    @api.onchange('exhibitor_type')
    def _onchange_exhibitor_type(self):
        super()._onchange_exhibitor_type()
        for r in self:
            if 'odoo-' in r.room_name:
                r.room_name = r.room_name.replace('odoo-', 'viindoo-')
