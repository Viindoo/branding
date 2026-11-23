from urllib.parse import urlparse

from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBankDocumentationLink(TransactionCase):

    def test_vietnamese_bank_account_documentation_link_leaves_the_odoo_site(self):
        view = self.env['res.partner.bank'].get_view(view_type='form')
        links = etree.fromstring(view['arch']).xpath("//widget[@name='documentation_link']/@path")

        self.assertTrue(links)
        for link in links:
            with self.subTest(link=link):
                host = urlparse(link).hostname or ''
                self.assertFalse(host == 'odoo.com' or host.endswith('.odoo.com'))
        self.assertTrue(any(urlparse(link).hostname == 'viindoo.com' for link in links))
