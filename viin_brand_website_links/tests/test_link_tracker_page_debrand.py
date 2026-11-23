from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestLinkTrackerPageDebrand(TransactionCase):

    def test_the_tracker_creation_page_names_and_links_no_odoo(self):
        arch = self.env.ref('website_links.create_shorten_url')._get_combined_arch()
        self.assertEqual(arch.xpath('//a[contains(@href, "odoo.com")]'), [])
        self.assertEqual(arch.xpath('//input[@id="url"][contains(@placeholder, "odoo")]'), [])
        texts = ' '.join(arch.xpath('//div[contains(@class, "o_website_links_create_tracked_url")]//text()'))
        self.assertNotIn('Odoo', texts)
