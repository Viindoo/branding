from types import SimpleNamespace

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand_sms_twilio import _companies_through_odoo_after, post_init_hook


@tagged('post_install', '-at_install')
class TestTwilioDefaults(TransactionCase):

    def test_a_new_company_sends_sms_through_twilio(self):
        company = self.env['res.company'].create({'name': 'Twilio Default Company'})
        self.assertEqual(company.sms_provider, 'twilio')

    def test_a_company_that_sent_through_odoo_is_moved_to_twilio(self):
        company = self.env['res.company'].create({'name': 'Moved Company', 'sms_provider': 'iap'})
        post_init_hook(self.env)
        self.assertEqual(company.sms_provider, 'twilio')

    def test_settings_do_not_offer_to_send_through_odoo(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        doc = etree.fromstring(arch)
        provider = doc.xpath('//field[@name="sms_provider"]')
        self.assertEqual(len(provider), 1)
        self.assertEqual(provider[0].get('invisible'), '1')
        button = doc.xpath('//button[@name="action_open_sms_twilio_account_manage"]')
        self.assertEqual(len(button), 1)
        self.assertFalse(button[0].getparent().get('invisible'), "The Twilio button must always be offered")

    def test_the_twilio_help_link_opens_a_viindoo_page(self):
        arch = self.env['sms.twilio.account.manage'].get_view(view_type='form')['arch']
        hrefs = etree.fromstring(arch).xpath('//a/@href')
        self.assertTrue(hrefs)
        for href in hrefs:
            self.assertNotIn('odoo.com', href)
        self.assertTrue(any(href.startswith('https://viindoo.com/documentation/20.0/') for href in hrefs))

    def test_the_core_sms_suites_run_with_their_companies_on_the_gateway_of_odoo(self):
        from odoo.addons.sms.tests.common import SMSCase, SMSCommon
        for suite_class in (SMSCase, SMSCommon):
            with self.subTest(suite=suite_class.__name__):
                self.assertTrue(suite_class.setUpClass.realigned_for_odoo_gateway)

    def test_the_realigned_setup_of_the_core_sms_suites_moves_every_company_to_the_gateway_of_odoo(self):
        calls = []
        other = self.env['res.company'].create({'name': 'Second Company'})
        self.assertEqual((self.env.company.sms_provider, other.sms_provider), ('twilio', 'twilio'))
        setup_class = _companies_through_odoo_after(calls.append)

        with self.env.cr.savepoint():
            setup_class.__func__(SimpleNamespace(env=self.env))
            (self.env.company | other).invalidate_recordset(['sms_provider'])

            self.assertEqual(len(calls), 1, 'the setUpClass of core still runs first')
            self.assertEqual((self.env.company.sms_provider, other.sms_provider), ('iap', 'iap'))
