from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Leave sending invoices by post out of the choices of the invoice sending preference."""
        fields = super().fields_get(allfields=allfields, attributes=attributes)
        sending_method = fields.get('invoice_sending_method')
        if sending_method and sending_method.get('selection'):
            sending_method['selection'] = [
                choice for choice in sending_method['selection'] if choice[0] != 'snailmail'
            ]
        return fields
