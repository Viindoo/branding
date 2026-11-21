from odoo import api, models

# The scheduled actions of the paid lead services, which are installed in a database but never run.
IAP_CRON_XMLIDS = [
    'crm_iap_enrich.ir_cron_lead_enrichment',
    'website_crm_iap_reveal.ir_cron_crm_reveal_lead',
]


class IrCron(models.Model):
    _inherit = 'ir.cron'

    @api.model
    def _deactivate_crm_iap_services(self):
        """Switch off what the paid lead services run on their own, in the databases that have them.

        The scheduled actions are switched off, and so are the reveal rules: an active rule keeps
        recording the visits it would turn into leads, and only the switched-off action would clean them.
        Lead enrichment is set to manual, the mode in which the enrichment module
        keeps its scheduled action off when it is installed after this module.
        """
        Param = self.env['ir.config_parameter']
        Param.set_param('crm.iap.lead.enrich.setting', 'manual')
        for xmlid in IAP_CRON_XMLIDS:
            cron = self.env.ref(xmlid, raise_if_not_found=False)
            if cron and cron.active:
                cron.active = False
        if 'crm.reveal.rule' in self.env:
            self.env['crm.reveal.rule'].search([('active', '=', True)]).write({'active': False})

    def _load_records(self, data_list, update=False):
        records = super()._load_records(data_list, update=update)
        # A lead service installed after this module creates its action active.
        if any(data.get('xml_id') in IAP_CRON_XMLIDS for data in data_list):
            self._deactivate_crm_iap_services()
        return records
