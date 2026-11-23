import re
from urllib.parse import urlsplit

from lxml import etree

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open

from odoo.addons.viin_brand_account.models.res_partner_bank import TRUSTED_ACCOUNTS_DOCUMENTATION_URL

PRODUCT_NAME = re.compile(r'\bOdoo\b|odoo\.com', re.IGNORECASE)


@tagged('post_install', '-at_install')
class TestBrandSurfaces(TransactionCase):

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

    def test_field_helps_do_not_name_odoo(self):
        checks = {
            'account.journal': ['inbound_payment_method_line_ids', 'outbound_payment_method_line_ids',
                                'alias_id', 'alias_name', 'invoice_reference_model'],
            'account.move': ['quick_edit_total_amount'],
            'account.payment': ['payment_method_line_id'],
            'account.payment.register': ['payment_method_line_id'],
            'account.financial.year.op': ['opening_date'],
        }
        for model, names in checks.items():
            info = self.env[model].fields_get(names, attributes=['help'])
            for name in names:
                with self.subTest(field='%s.%s' % (model, name)):
                    self.assertNotRegex(info[name]['help'], PRODUCT_NAME)

    def test_journal_reference_help_names_the_default_option_by_its_label(self):
        info = self.env['account.journal'].fields_get(['invoice_reference_model'], attributes=['help', 'selection'])
        labels = dict(info['invoice_reference_model']['selection'])
        self.assertIn(labels['odoo'].split(' (')[0], info['invoice_reference_model']['help'])


@tagged('post_install', '-at_install')
class TestEinvoiceMailLogo(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.lang']._activate_lang('fr_FR')
        cls.journal = cls.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        partner = cls.env['res.partner'].create({'name': 'Customer'})
        cls.move = cls.env['account.move'].create({
            'move_type': 'out_invoice', 'partner_id': partner.id, 'journal_id': cls.journal.id,
        })

    def _render(self, xmlid, record, lang):
        template = self.env.ref(xmlid).with_context(lang=lang)
        return template._render_field('body_html', record.ids)[record.id]

    def test_einvoice_notification_mails_carry_the_viindoo_logo_in_every_language(self):
        cases = (
            ('account.mail_template_einvoice_notification', self.journal),
            ('account.mail_template_invoice_subscriber', self.move),
        )
        for xmlid, record in cases:
            for lang in ('en_US', 'fr_FR'):
                with self.subTest(template=xmlid, lang=lang):
                    body = self._render(xmlid, record, lang)
                    sources = etree.HTML(body).xpath('//img/@src')
                    self.assertTrue(any('Viindoo-logo-inverted' in source for source in sources))
                    self.assertFalse(any('logo_inverse_white' in source for source in sources))
                    self.assertFalse(etree.HTML(body).xpath('//img[@alt="Odoo"]'))


@tagged('post_install', '-at_install')
class TestPhishingWarningLink(TransactionCase):

    def test_the_learn_more_link_of_a_phishing_warning_opens_a_viindoo_page(self):
        partner = self.env['res.partner'].create({'name': 'Vendor', 'country_id': self.env.ref('base.us').id})
        bank = self.env['res.partner.bank'].create({
            'account_number': 'BE68539007547034',
            'partner_id': partner.id,
            'allow_out_payment': False,
        })
        warnings = bank.phishing_warnings
        self.assertTrue(warnings, 'an IBAN of Belgium on a vendor of the United States is a phishing risk')
        for key, warning in warnings.items():
            with self.subTest(warning=key):
                self.assertEqual(warning['action']['type'], 'ir.actions.act_url')
                host = urlsplit(warning['action']['url']).hostname
                self.assertEqual(host, 'viindoo.com')

    def test_the_phishing_link_is_the_page_of_the_documentation_map_of_viin_brand(self):
        with file_open('viin_brand/static/src/views/widgets/documentation_link/viindoo_mapping_url.js') as source:
            documentation_map = source.read()
        entry = re.escape('"/applications/finance/accounting/payables/pay/trusted_accounts.html":')
        self.assertRegex(documentation_map, entry + r'\s*"%s"' % re.escape(TRUSTED_ACCOUNTS_DOCUMENTATION_URL))
