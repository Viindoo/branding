from unittest.mock import patch

from lxml import etree

from odoo.addons.base.models.ir_ui_view import Base
from odoo.addons.viin_brand.tests.common import HiddenMenuCase
from odoo.addons.viin_brand_website_crm_iap_reveal import uninstall_hook
from odoo.addons.viin_brand_website_crm_iap_reveal.models.crm_reveal_rule import CrmRevealRule
from odoo.addons.viin_brand_website_crm_iap_reveal.models.ir_cron import REVEAL_CRON_XMLID
from odoo.tests.common import tagged


LEAD_FORM = """
<form>
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
LEAD_PIVOT = """
<pivot>
    <field name="stage_id" type="row"/>
    <field name="reveal_iap_credits" invisible="1"/>
</pivot>"""
VISITS_TO_LEADS_MENUS = (
    'website_crm_iap_reveal.crm_reveal_rule_menu_action',
    'website_crm_iap_reveal.crm_reveal_view_menu_action',
)


@tagged('post_install', '-at_install')
class TestVisitsToLeadsHidden(HiddenMenuCase):

    def _load_cron(self, xmlid):
        """Load a scheduled action as the data of its module does: without an ``active`` value."""
        values = {
            'name': xmlid, 'model_id': self.env.ref('crm.model_crm_lead').id,
            'state': 'code', 'code': 'pass',
        }
        self.env['ir.cron']._load_records([{'xml_id': xmlid, 'values': values, 'noupdate': False}])
        return self.env.ref(xmlid)

    def test_the_visits_to_leads_menus_are_archived_until_the_uninstall(self):
        menus = [self.env.ref(xmlid) for xmlid in VISITS_TO_LEADS_MENUS]
        for menu in menus:
            self.assertFalse(menu.active, menu.complete_name)
            self.assertNotIn(menu.id, self.web_client_menu_ids())

        uninstall_hook(self.env)

        for menu in menus:
            self.assertTrue(menu.active, menu.complete_name)
        # the rules menu sits under the menu of the mining service, which may stay hidden
        reports_menu = self.env.ref('website_crm_iap_reveal.crm_reveal_view_menu_action')
        self.assertIn(reports_menu.id, self.web_client_menu_ids())

    def test_the_visits_to_leads_scheduled_action_is_switched_off(self):
        cron = self.env.ref(REVEAL_CRON_XMLID).with_context(active_test=False)
        self.assertFalse(cron.active)

    def test_the_scheduled_action_created_again_is_switched_off(self):
        self.env.ref(REVEAL_CRON_XMLID).unlink()
        self.assertFalse(self._load_cron(REVEAL_CRON_XMLID).active)

    def test_other_scheduled_actions_created_after_the_branding_stay_active(self):
        self.assertTrue(self._load_cron('viin_brand_website_crm_iap_reveal.test_other_cron').active)

    def _visit(self, rule_country):
        """Record a visit from ``rule_country`` of a page the rule would match, return what is recorded."""
        views = self.env['crm.reveal.view']
        before = views.search_count([])
        result = views._create_reveal_view(1, 'http://localhost/page', '203.0.113.7', rule_country.code, None, [])
        return result, views.search_count([]) - before

    def test_a_visit_records_nothing_and_the_rule_of_a_customer_stays_active(self):
        country = self.env.ref('base.be')
        rule = self.env['crm.reveal.rule'].create({'name': 'Visitors of a country', 'country_ids': [(4, country.id)]})

        self.env['ir.cron']._deactivate_visits_to_leads()
        result, recorded = self._visit(country)

        self.assertTrue(rule.active, 'the rule keeps the state its user gave it')
        self.assertFalse(result)
        self.assertEqual(recorded, 0)

    def test_the_rule_matches_again_once_the_module_is_not_there(self):
        country = self.env.ref('base.be')
        rule = self.env['crm.reveal.rule'].create({'name': 'Visitors of a country', 'country_ids': [(4, country.id)]})

        # what the service would do without this module
        matched = super(CrmRevealRule, rule)._match_url(1, 'http://localhost/page', country.code, None, [])

        self.assertEqual([found['id'] for found in matched], rule.ids)

    def _synthetic_view(self, arch):
        with patch.object(Base, 'get_view', return_value={'arch': arch}):
            return etree.fromstring(self.env['crm.lead'].get_view(view_type='form')['arch'])

    def test_the_reveal_fields_are_not_in_the_lead_form(self):
        self.env.user.group_ids |= self.env.ref('base.group_no_one')
        arch = etree.fromstring(self.env['crm.lead'].get_view(view_type='form')['arch'])
        self.assertTrue(arch.xpath('//field[@name="partner_id"]'), 'the other fields stay')
        self.assertFalse(arch.xpath('//field[starts-with(@name, "reveal_")]'))
        self.assertFalse(arch.xpath('//group[@string="Lead Generation Information"]'))

    def test_the_group_of_the_reveal_fields_is_removed_with_them(self):
        doc = self._synthetic_view(LEAD_FORM)
        self.assertFalse(doc.xpath('//field[starts-with(@name, "reveal_")]'))
        self.assertFalse(doc.xpath('//group[@string="Lead Generation Information"]'))
        self.assertTrue(doc.xpath('//field[@name="name"]'))

    def test_the_reveal_field_of_a_report_view_is_removed(self):
        doc = self._synthetic_view(LEAD_PIVOT)
        self.assertFalse(doc.xpath('//field[@name="reveal_iap_credits"]'))
        self.assertTrue(doc.xpath('//field[@name="stage_id"]'))
