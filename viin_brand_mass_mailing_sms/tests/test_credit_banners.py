from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCreditBanners(TransactionCase):
    """The banners that send an SMS campaign owner to buy credits or to register an account of Odoo."""

    def _banners(self, view_type):
        arch = self.env['mailing.mailing'].get_view(view_type=view_type)['arch']
        return etree.fromstring(arch).xpath('//div[.//*[@name="action_buy_sms_credits"]]')

    def test_the_form_has_no_banner_that_sends_to_the_credits_page(self):
        banners = self._banners('form')
        self.assertEqual(len(banners), 2)
        for banner in banners:
            self.assertEqual(banner.get('invisible'), '1')

    def test_the_kanban_card_has_no_banner_that_sends_to_the_credits_page(self):
        banners = self._banners('kanban')
        self.assertEqual(len(banners), 2)
        for banner in banners:
            self.assertEqual(banner.get('invisible'), '1')
