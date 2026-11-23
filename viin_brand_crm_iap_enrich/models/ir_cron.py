from odoo import api, models

# The scheduled action of the lead enrichment service, which spends the credits of Odoo S.A.
ENRICHMENT_CRON_XMLID = 'crm_iap_enrich.ir_cron_lead_enrichment'


class IrCron(models.Model):
    _inherit = 'ir.cron'

    @api.model
    def _deactivate_lead_enrichment_cron(self):
        """Switch off the scheduled action of the lead enrichment service."""
        cron = self.env.ref(ENRICHMENT_CRON_XMLID, raise_if_not_found=False)
        if cron and cron.active:
            cron.active = False

    def _load_records(self, data_list, update=False):
        records = super()._load_records(data_list, update=update)
        # a record created again (an administrator deleted it) is created active
        if any(data.get('xml_id') == ENRICHMENT_CRON_XMLID for data in data_list):
            self._deactivate_lead_enrichment_cron()
        return records
