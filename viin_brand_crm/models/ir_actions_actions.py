from odoo import api, models


class IrActionsActions(models.Model):
    _inherit = 'ir.actions.actions'

    @api.model
    def _get_hidden_binding_xmlids(self):
        """Keep the lead enrichment action out of the Action menu of the leads."""
        return super()._get_hidden_binding_xmlids() + ['crm_iap_enrich.action_enrich_mail']
