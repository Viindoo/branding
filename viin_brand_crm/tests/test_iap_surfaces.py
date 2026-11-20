import re
from unittest.mock import patch

from lxml import etree

from odoo.addons.base.models.ir_ui_view import Base
from odoo.tests.common import TransactionCase, tagged

PRODUCT_NAME = re.compile(r'\bOdoo\b|odoo\.com', re.IGNORECASE)
LEAD_FORM = """
<form>
    <header>
        <button name="iap_enrich" type="object" string="Enrich"/>
        <button name="action_convert" type="object" string="Convert"/>
    </header>
    <sheet>
        <group>
            <field name="name"/>
            <group string="Lead Generation Information">
                <field name="reveal_ip"/>
                <field name="reveal_iap_credits"/>
                <field name="reveal_rule_id"/>
            </group>
        </group>
    </sheet>
</form>"""
LEAD_KANBAN = """
<kanban>
    <header>
        <button name="action_generate_leads" type="object" string="Generate Leads"/>
    </header>
    <field name="name"/>
    <field name="reveal_iap_credits" invisible="1"/>
</kanban>"""


@tagged('post_install', '-at_install')
class TestLeadViewsKeepThePaidServicesOut(TransactionCase):

    def _view(self, arch):
        with patch.object(Base, 'get_view', return_value={'arch': arch}):
            return etree.fromstring(self.env['crm.lead'].get_view(view_type='form')['arch'])

    def test_enrich_and_reveal_nodes_are_removed_from_the_lead_form(self):
        doc = self._view(LEAD_FORM)
        self.assertFalse(doc.xpath('//button[@name="iap_enrich"]'))
        self.assertFalse(doc.xpath('//field[starts-with(@name, "reveal_")]'))
        self.assertFalse(doc.xpath('//group[@string="Lead Generation Information"]'))
        self.assertTrue(doc.xpath('//button[@name="action_convert"]'), 'the other buttons stay')
        self.assertTrue(doc.xpath('//field[@name="name"]'))

    def test_generate_leads_button_and_the_header_it_leaves_empty_are_removed_from_the_kanban(self):
        doc = self._view(LEAD_KANBAN)
        self.assertFalse(doc.xpath('//button[@name="action_generate_leads"]'))
        self.assertFalse(doc.xpath('//header'))
        self.assertFalse(doc.xpath('//field[@name="reveal_iap_credits"]'))
        self.assertTrue(doc.xpath('//field[@name="name"]'))


@tagged('post_install', '-at_install')
class TestPaidLeadServicesStayHidden(TransactionCase):

    def _service_record(self, xmlid, model, values):
        """Return the record of a paid service under ``xmlid``.

        The service's own record when its module is installed, else one made from
        ``values`` and registered under ``xmlid``.
        """
        record = self.env.ref(xmlid, raise_if_not_found=False)
        if record:
            return record
        record = self.env[model].create(values)
        module, name = xmlid.split('.')
        self.env['ir.model.data'].create({
            'module': module, 'name': name, 'model': model, 'res_id': record.id,
        })
        return record

    def _lead_action(self, name):
        lead_model = self.env.ref('crm.model_crm_lead')
        return {
            'name': name,
            'model_id': lead_model.id,
            'binding_model_id': lead_model.id,
            'state': 'code',
            'code': 'pass',
        }

    def test_enrich_action_is_kept_out_of_the_action_menu_of_leads(self):
        action = self._service_record(
            'crm_iap_enrich.action_enrich_mail',
            'ir.actions.server',
            self._lead_action('Enrich'),
        )
        other = self.env['ir.actions.server'].create(self._lead_action('Other'))
        self.env.registry.clear_cache()
        bindings = self.env['ir.actions.actions'].get_bindings('crm.lead')
        bound = [binding['id'] for binding in bindings.get('action', [])]
        self.assertEqual(action.binding_model_id, self.env.ref('crm.model_crm_lead'))
        self.assertNotIn(action.id, bound)
        self.assertIn(other.id, bound, 'the other actions of the leads stay')

    def test_scheduled_actions_of_the_paid_services_are_switched_off(self):
        xmlids = (
            'crm_iap_enrich.ir_cron_lead_enrichment',
            'website_crm_iap_reveal.ir_cron_crm_reveal_lead',
        )
        for xmlid in xmlids:
            cron = self._service_record(xmlid, 'ir.cron', {
                'name': xmlid,
                'model_id': self.env.ref('crm.model_crm_lead').id,
                'state': 'code',
                'code': 'pass',
            })
            cron.active = True
        self.env['ir.cron']._deactivate_crm_iap_services()
        for xmlid in xmlids:
            self.assertFalse(self.env.ref(xmlid).active, xmlid)

    def test_a_missing_service_module_is_ignored(self):
        self.env['ir.cron']._deactivate_crm_iap_services()
        self.assertIsInstance(self.env['ir.ui.menu']._get_hidden_menu_xmlids(), list)


@tagged('post_install', '-at_install')
class TestCrmBrandSurfaces(TransactionCase):

    def test_pipeline_empty_state_and_ringover_help_do_not_name_odoo(self):
        help_text = self.env.ref('crm.crm_case_form_view_salesteams_opportunity').with_context(lang='en_US').help
        self.assertNotRegex(help_text, PRODUCT_NAME)
        arch = etree.fromstring(self.env['res.config.settings'].get_view(view_type='form')['arch'])
        row = arch.xpath('//setting[@id="ringover-voip"]')
        self.assertEqual(len(row), 1)
        self.assertNotRegex(row[0].get('help'), PRODUCT_NAME)

    def test_digest_tips_name_viindoo_not_a_neutral_word(self):
        text = self.env.ref('crm.digest_tip_crm_5').with_context(lang='en_US').tip_description
        self.assertNotRegex(text, r'\b[Tt]he system\b|\bin system\b')
        self.assertIn('Viindoo', text)

    def test_tips_about_features_that_are_not_available_are_archived(self):
        for xmlid in ('crm.digest_tip_crm_1', 'crm.digest_tip_crm_4'):
            with self.subTest(tip=xmlid):
                self.assertFalse(self.env.ref(xmlid).active)

    def test_demo_welcome_mail_names_viindoo(self):
        template = self.env['mail.template'].create({
            'name': 'Welcome Demo',
            'model_id': self.env.ref('crm.model_crm_lead').id,
            'body_html': (
                "<p>I'll help you get the most out of Odoo. Could we plan a quick demo soon?</p>"
                '<p>Powered by <a target="_blank" href="https://www.odoo.com?utm_source=db&amp;utm_medium=email" '
                'style="color: #875A7B;">Odoo</a></p>'),
        })
        self.env['ir.model.data'].create({
            'module': 'crm', 'name': 'mail_template_demo_crm_lead', 'model': 'mail.template', 'res_id': template.id,
        })
        self.env['mail.template']._debrand_crm_demo_template()
        self.assertNotRegex(template.body_html, PRODUCT_NAME)
        self.assertIn('get the most out of our solutions', template.body_html)
        self.assertIn('https://viindoo.com', template.body_html)
