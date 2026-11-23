from unittest.mock import patch

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.base.models.ir_ui_view import Base
from odoo.addons.viin_brand_crm_iap_enrich.models.ir_cron import ENRICHMENT_CRON_XMLID

LEAD_LIST = """
<list>
    <header>
        <button name="iap_enrich" type="object" string="Enrich"/>
    </header>
    <field name="name"/>
</list>"""
LEAD_FORM = """
<form>
    <header>
        <button name="iap_enrich" type="object" string="Enrich"/>
        <button name="action_convert" type="object" string="Convert"/>
    </header>
    <field name="name"/>
</form>"""


@tagged('post_install', '-at_install')
class TestLeadEnrichmentHidden(TransactionCase):

    def _lead_action(self, name):
        lead_model = self.env.ref('crm.model_crm_lead')
        return {
            'name': name,
            'model_id': lead_model.id,
            'binding_model_id': lead_model.id,
            'state': 'code',
            'code': 'pass',
        }

    def _load_cron(self, xmlid):
        """Load a scheduled action as the data of its module does: without an ``active`` value."""
        values = {
            'name': xmlid, 'model_id': self.env.ref('crm.model_crm_lead').id,
            'state': 'code', 'code': 'pass',
        }
        self.env['ir.cron']._load_records([{'xml_id': xmlid, 'values': values, 'noupdate': False}])
        return self.env.ref(xmlid)

    def test_the_enrichment_scheduled_action_is_switched_off(self):
        cron = self.env.ref(ENRICHMENT_CRON_XMLID).with_context(active_test=False)
        self.assertFalse(cron.active)

    def test_the_enrichment_scheduled_action_created_again_is_switched_off(self):
        self.env.ref(ENRICHMENT_CRON_XMLID).unlink()
        self.assertFalse(self._load_cron(ENRICHMENT_CRON_XMLID).active)

    def test_other_scheduled_actions_created_after_the_branding_stay_active(self):
        self.assertTrue(self._load_cron('viin_brand_crm_iap_enrich.test_other_cron').active)

    def test_the_enrichment_action_is_kept_out_of_the_action_menu_of_leads(self):
        action = self.env.ref('crm_iap_enrich.action_enrich_mail')
        other = self.env['ir.actions.server'].create(self._lead_action('Other'))
        bindings = self.env['ir.actions.actions'].get_bindings('crm.lead')
        bound = [binding['id'] for binding in bindings.get('action', [])]
        self.assertEqual(action.binding_model_id, self.env.ref('crm.model_crm_lead'))
        self.assertNotIn(action.id, bound)
        self.assertIn(other.id, bound, 'the other actions of the leads stay')

    def _synthetic_view(self, arch):
        with patch.object(Base, 'get_view', return_value={'arch': arch}):
            return etree.fromstring(self.env['crm.lead'].get_view(view_type='form')['arch'])

    def test_the_enrichment_button_is_not_in_the_lead_form(self):
        arch = etree.fromstring(self.env['crm.lead'].get_view(view_type='form')['arch'])
        self.assertTrue(arch.xpath('//button[@name="action_convert_to_opportunity"]'), 'the other buttons stay')
        self.assertFalse(arch.xpath('//button[@name="iap_enrich"]'))

    def test_the_other_buttons_of_the_header_stay_when_the_enrichment_button_goes(self):
        doc = self._synthetic_view(LEAD_FORM)
        self.assertFalse(doc.xpath('//button[@name="iap_enrich"]'))
        self.assertTrue(doc.xpath('//header/button[@name="action_convert"]'))

    def test_the_header_left_empty_by_the_enrichment_button_is_removed(self):
        doc = self._synthetic_view(LEAD_LIST)
        self.assertFalse(doc.xpath('//button[@name="iap_enrich"]'))
        self.assertFalse(doc.xpath('//header'))
        self.assertTrue(doc.xpath('//field[@name="name"]'))
