# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestNotificationGroupTranslation(NoupdateTranslationCase):

    def test_inbox_group_name_of_a_language_loaded_before_the_module_names_viindoo(self):
        self.load_stock_then_branding_catalog(['mail'], 'viin_brand_mail')
        group = self.env.ref('mail.group_mail_notification_type_inbox')
        self.assertHoldsStockWording(self.translated(group, 'name'))
        self.load_catalog('viin_brand_mail')
        self.assertNamesNoOdoo(self.translated(group, 'name'))
