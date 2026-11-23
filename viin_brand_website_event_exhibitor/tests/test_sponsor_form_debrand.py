from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSponsorFormDebrand(TransactionCase):

    def test_the_sponsor_website_placeholder_is_not_a_page_of_odoo(self):
        arch = self.env['event.sponsor'].get_view(view_type='form')['arch']
        placeholders = etree.fromstring(arch).xpath('//field[@name="url"]/@placeholder')
        self.assertEqual(len(placeholders), 1)
        self.assertNotIn('odoo', placeholders[0].lower())
