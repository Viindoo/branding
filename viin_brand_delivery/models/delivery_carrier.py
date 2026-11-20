from odoo import models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def install_more_provider(self):
        """Open the list of provider modules without the Enterprise offer in its empty state."""
        action = super().install_more_provider()
        action.pop('help', None)
        return action
