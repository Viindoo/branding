import re

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

PRODUCT_NAME = re.compile(r'\bOdoo\b|odoo\.com', re.IGNORECASE)


@tagged('post_install', '-at_install')
class TestBrandSurfaces(TransactionCase):

    def test_einvoice_notification_mails_carry_the_viindoo_logo(self):
        for xmlid in ('account.mail_template_einvoice_notification', 'account.mail_template_invoice_subscriber'):
            with self.subTest(template=xmlid):
                body = self.env.ref(xmlid).with_context(lang='en_US').body_html
                self.assertNotIn('logo_inverse_white_206px', body)
                self.assertNotRegex(body, r'alt="Odoo"')
                self.assertIn('Viindoo-logo-inverted', body)

    def test_both_invoice_qr_code_logos_are_the_viindoo_logo(self):
        for xmlid in ('account.report_invoice_document', 'account.report_invoice_qr_code_preview'):
            logos = self.env.ref(xmlid)._get_combined_arch().xpath("//img[@id='qrcode_odoo_logo']")
            self.assertTrue(logos, xmlid)
            for logo in logos:
                with self.subTest(template=xmlid):
                    self.assertNotIn('Odoo_logo_O', logo.get('src'))
                    self.assertIn('Viindoo-logo', logo.get('src'))

    def test_company_data_onboarding_website_placeholder_names_viindoo(self):
        view = self.env['res.company'].get_view(
            view_id=self.env.ref('account.res_company_form_view_onboarding').id, view_type='form')
        website = etree.fromstring(view['arch']).xpath("//field[@name='website']")
        self.assertEqual(len(website), 1)
        self.assertNotRegex(website[0].get('placeholder'), PRODUCT_NAME)
        self.assertIn('viindoo.com', website[0].get('placeholder'))

    def test_empty_state_helps_do_not_name_odoo(self):
        for xmlid in (
            'account.action_credit_statement_tree',
            'account.action_bank_statement_tree',
            'account.res_partner_action_supplier_bills',
            'account.res_partner_action_customer',
            'account.res_partner_action_supplier',
        ):
            with self.subTest(action=xmlid):
                self.assertNotRegex(self.env.ref(xmlid).with_context(lang='en_US').help, PRODUCT_NAME)

    def test_field_helps_name_viindoo_not_a_neutral_word(self):
        checks = {
            'account.journal': ['inbound_payment_method_line_ids', 'outbound_payment_method_line_ids',
                                'alias_name', 'invoice_reference_model'],
            'account.move': ['quick_edit_total_amount'],
        }
        for model, names in checks.items():
            info = self.env[model].fields_get(names, attributes=['help'])
            for name in names:
                with self.subTest(field='%s.%s' % (model, name)):
                    self.assertNotRegex(info[name]['help'], PRODUCT_NAME)
                    self.assertNotRegex(info[name]['help'], r'\b[Ss]ystem\b')

    def test_report_expression_engine_label_stays_as_core_has_it(self):
        selection = self.env['account.report.expression'].fields_get(['engine'], attributes=['selection'])
        labels = dict(selection['engine']['selection'])
        self.assertEqual(labels['domain'], 'Odoo Domain')

    def test_journal_reference_help_names_the_default_option_by_its_label(self):
        info = self.env['account.journal'].fields_get(['invoice_reference_model'], attributes=['help', 'selection'])
        labels = dict(info['invoice_reference_model']['selection'])
        self.assertIn('The default one is the %s' % labels['odoo'].split(' (')[0], info['invoice_reference_model']['help'])

    def test_the_tip_about_sending_invoices_by_post_is_archived(self):
        self.assertFalse(self.env.ref('account.digest_tip_account_0').active)

    def test_the_module_depends_on_the_module_that_adds_the_active_flag_of_digest_tips(self):
        module = self.env['ir.module.module'].search([('name', '=', 'viin_brand_account')])
        self.assertIn('viin_brand_digest', module.dependencies_id.mapped('name'))
