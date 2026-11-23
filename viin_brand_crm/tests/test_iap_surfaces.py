import re
from urllib.parse import urlsplit

from lxml import etree, html

from odoo.tests.common import TransactionCase, tagged

PRODUCT_NAME = re.compile(r'\bOdoo\b|odoo\.com', re.IGNORECASE)


@tagged('post_install', '-at_install')
class TestCrmBrandSurfaces(TransactionCase):

    def test_pipeline_empty_state_does_not_name_odoo(self):
        help_text = self.env.ref('crm.crm_case_form_view_salesteams_opportunity').with_context(lang='en_US').help
        self.assertNotRegex(help_text, PRODUCT_NAME)

    def test_the_website_placeholder_of_the_lead_form_names_viindoo(self):
        self.env.user.group_ids |= self.env.ref('base.group_no_one')
        arch = etree.fromstring(self.env['crm.lead'].get_view(view_type='form')['arch'])
        websites = arch.xpath('//field[@name="website"]')
        self.assertTrue(websites)
        for website in websites:
            self.assertNotRegex(website.get('placeholder'), PRODUCT_NAME)
            self.assertIn('viindoo.com', website.get('placeholder'))

    def test_digest_tips_name_viindoo_not_odoo(self):
        for xmlid in ('crm.digest_tip_crm_2', 'crm.digest_tip_crm_5'):
            with self.subTest(tip=xmlid):
                text = self.env.ref(xmlid).with_context(lang='en_US').tip_description
                self.assertNotRegex(text, PRODUCT_NAME)
                self.assertIn('Viindoo', text)

    def test_the_tips_of_the_paid_services_are_archived_and_name_no_odoo(self):
        # lead mining and the autocompletion of a company are credit-based services of Odoo S.A.
        for xmlid in ('crm.digest_tip_crm_1', 'crm.digest_tip_crm_4'):
            with self.subTest(tip=xmlid):
                tip = self.env.ref(xmlid).with_context(lang='en_US', active_test=False)
                self.assertFalse(tip.active)
                self.assertNotRegex(' '.join(html.fromstring(tip.tip_description).itertext()), PRODUCT_NAME)
                self.assertNotRegex(tip.name, PRODUCT_NAME)
                self.assertNotIn('odoocdn', tip.tip_description)

    def test_a_digest_never_offers_the_tip_of_lead_mining(self):
        user = self.env.ref('base.user_admin')
        user.group_ids |= self.env.ref('sales_team.group_sale_salesman_all_leads')
        tips = self.env['digest.tip']
        mining = self.env.ref('crm.digest_tip_crm_1')
        (tips.with_context(active_test=False).search([]) - mining).write({'user_ids': [(4, user.id)]})
        digest = self.env['digest.digest'].create({'name': 'Tips digest', 'user_ids': [(4, user.id)]})
        self.assertFalse(digest._compute_tips(user.company_id, user, tips_count=1, consumed=False))

    def test_the_tips_a_digest_sends_carry_no_odoo_mark_and_no_image_from_its_servers(self):
        user = self.env.ref('base.user_admin')
        user.group_ids |= self.env.ref('sales_team.group_sale_salesman_all_leads')
        tips = self.env['digest.tip']
        crm_tips = tips.browse(self.env['ir.model.data'].search([
            ('module', '=', 'crm'), ('model', '=', 'digest.tip'),
        ]).mapped('res_id'))
        (tips.search([]) - crm_tips).write({'user_ids': [(4, user.id)]})
        digest = self.env['digest.digest'].create({'name': 'Tips digest', 'user_ids': [(4, user.id)]})
        descriptions = digest._compute_tips(user.company_id, user, tips_count=len(crm_tips), consumed=False)
        database_host = urlsplit(digest.get_base_url()).netloc
        images = []
        for description in descriptions:
            with self.subTest(description=description[:60]):
                self.assertNotRegex(description, PRODUCT_NAME)
                for source in html.fromstring(description).xpath('//img/@src'):
                    images.append(source)
                    self.assertEqual(urlsplit(source).netloc, database_host)
        self.assertTrue(any(source.endswith('/viin_brand_crm/static/src/img/probability-rate.gif') for source in images))
        self.assertTrue(any(source.endswith('/crm/static/src/img/milk-mapview-toggle.gif') for source in images))
