from odoo import api, models

# The carrier connectors of the Shipping Connectors block, which are Enterprise modules.
SHIPPING_CONNECTOR_SETTING_IDS = (
    'compute_shipping_costs_ups',
    'compute_shipping_costs_dhl',
    'compute_shipping_costs_fedex',
    'compute_shipping_costs_usps',
)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _get_hidden_setting_xpaths(self):
        """Hide the rows that only point to the Enterprise shipping connectors."""
        return super()._get_hidden_setting_xpaths() + [
            '//setting[@id="%s"]' % setting_id for setting_id in SHIPPING_CONNECTOR_SETTING_IDS
        ]
