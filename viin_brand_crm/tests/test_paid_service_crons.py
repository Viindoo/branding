from odoo.addons.viin_brand_crm.models.ir_cron import IAP_CRON_XMLIDS
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPaidLeadServiceCrons(TransactionCase):

    def _load_cron(self, xmlid):
        """Load a scheduled action as the data of its module does at the install."""
        values = {
            'name': xmlid, 'model_id': self.env.ref('crm.model_crm_lead').id,
            'state': 'code', 'code': 'pass', 'active': True,
        }
        self.env['ir.cron']._load_records(
            [{'xml_id': xmlid, 'values': values, 'noupdate': False}],
        )
        return self.env.ref(xmlid)

    def test_crons_of_lead_services_loaded_after_the_branding_are_switched_off(self):
        for xmlid in IAP_CRON_XMLIDS:
            with self.subTest(cron=xmlid):
                self.assertFalse(self._load_cron(xmlid).active)

    def test_other_crons_loaded_after_the_branding_stay_active(self):
        cron = self._load_cron('viin_brand_crm.test_other_cron')

        self.assertTrue(cron.active)

    def test_the_branding_sets_lead_enrichment_to_manual(self):
        # The lead enrichment module switches its scheduled action on at its install
        # only when the enrichment is automatic.
        Param = self.env['ir.config_parameter']
        Param.set_param('crm.iap.lead.enrich.setting', 'auto')

        self.env['ir.cron']._deactivate_crm_iap_services()

        self.assertEqual(Param.get_param('crm.iap.lead.enrich.setting'), 'manual')

    def test_the_crons_of_the_installed_lead_services_are_switched_off(self):
        crons = {
            xmlid: self.env.ref(xmlid, raise_if_not_found=False) for xmlid in IAP_CRON_XMLIDS
        }
        if not any(crons.values()):
            self.skipTest("none of the paid lead services is installed")
        for xmlid, cron in crons.items():
            if cron:
                with self.subTest(cron=xmlid):
                    self.assertFalse(cron.active)
