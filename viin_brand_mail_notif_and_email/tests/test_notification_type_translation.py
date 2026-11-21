# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged

from odoo.addons.viin_brand.tests.common import LANG, NoupdateTranslationCase


@tagged('post_install', '-at_install')
class TestNotificationTypeTranslation(NoupdateTranslationCase):

    def test_help_of_a_language_added_later_translates_the_three_choices(self):
        """Every module declaring the field names its row; the catalog of the English wins."""
        xmlid = 'viin_brand_mail_notif_and_email.field_res_users__notification_type'
        field = self.env.ref(xmlid)
        english = field.with_context(lang='en_US').help
        self.assertEqual(english, self.env['res.users']._fields['notification_type'].help)
        self.env['res.lang']._activate_lang(LANG)
        self.env['ir.module.module']._load_module_terms(['mail'], [LANG], overwrite=True)
        self.assertHoldsStockWording(self.translated(field, 'help'))

        self.load_catalog('viin_brand_mail')
        self.load_catalog('viin_brand_mail_notif_and_email')

        self.assertEqual(
            self.translated(field, 'help'),
            self.catalog_translation('viin_brand_mail_notif_and_email', english, xmlid),
        )
