from lxml import etree

from odoo.addons.viin_brand_sms_twilio import post_init_hook
from odoo.tests.common import TransactionCase, tagged


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
        self.assertTrue(any(href.startswith('https://viindoo.com/documentation/19.0/') for href in hrefs))

    def test_the_routing_test_of_core_twilio_runs_with_the_account_check_realigned(self):
        from odoo.addons.sms_twilio.tests.test_sms_twilio import TestSmsTwilio
        self.assertTrue(TestSmsTwilio.test_send_with_multi_company.realigned_for_sender_number)
