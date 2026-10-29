from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestIapSettings(TransactionCase):

    def test_crm_iap_settings_are_hidden(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        doc = etree.fromstring(arch)

        for field_name in ('module_crm_iap_enrich', 'module_crm_iap_mine', 'module_website_crm_iap_reveal'):
            nodes = doc.xpath('//field[@name="%s"]/ancestor::setting[1]' % field_name)
            self.assertEqual(len(nodes), 1, field_name)
            self.assertEqual(nodes[0].get('invisible'), '1', field_name)
