from odoo import api, models

# The scheduled action of visits to leads, which spends the credits of Odoo S.A.
REVEAL_CRON_XMLID = 'website_crm_iap_reveal.ir_cron_crm_reveal_lead'


class IrCron(models.Model):
    _inherit = 'ir.cron'

    @api.model
    def _deactivate_visits_to_leads(self):
        """Switch off the scheduled action of visits to leads."""
        cron = self.env.ref(REVEAL_CRON_XMLID, raise_if_not_found=False)
        if cron and cron.active:
            cron.active = False

    def _load_records(self, data_list, update=False):
        records = super()._load_records(data_list, update=update)
        # a record created again (an administrator deleted it) is created active
        if any(data.get('xml_id') == REVEAL_CRON_XMLID for data in data_list):
            self._deactivate_visits_to_leads()
        return records
