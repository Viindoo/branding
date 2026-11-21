# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import tagged
from odoo.tools import file_open
from odoo.tools.translate import get_po_paths, translation_file_reader

from odoo.addons.viin_brand.tests.common import LANG, NoupdateTranslationCase

DEMO_CAPTURE_HELP = ('payment_demo', 'field_payment_transaction__capture_manually')


@tagged('post_install', '-at_install')
class TestCaptureHelpTranslation(NoupdateTranslationCase):

    def test_demo_capture_help_of_a_language_added_later_does_not_name_odoo(self):
        """A language added later loads all catalogs, the demo one after this.

        The row stays in the demo module's stock wording when payment_demo is installed
        after this module while a language other than English is active, and when
        ``--load-language`` adds the language to an existing database: neither loads
        this module's catalog after the demo module's.
        """
        if self.env['ir.module.module']._get('payment_demo').state != 'installed':
            self.skipTest("payment_demo is not installed")
        xmlid = 'payment_demo.field_payment_transaction__capture_manually'
        field = self.env.ref(xmlid)
        source = self.env['payment.provider']._fields['capture_manually'].help
        self.env['res.lang']._activate_lang(LANG)
        self.env['ir.module.module']._load_module_terms(
            ['payment', 'viin_brand_payment', 'payment_demo'], [LANG],
        )
        help_vi = self.translated(field, 'help')
        self.assertNotIn('Odoo', help_vi)
        brand_vi = self.catalog_translation('viin_brand_payment', source, xmlid)
        self.assertEqual(help_vi, brand_vi)

    def test_catalog_keeps_the_entry_of_the_demo_capture_help(self):
        """The catalog names the help of the demo module's related field, which an export
        of this module does not produce: the entry has to stay through a regeneration.
        """
        source = self.env['payment.provider']._fields['capture_manually'].help
        paths = get_po_paths('viin_brand_payment', LANG)
        template = 'viin_brand_payment/i18n/viin_brand_payment.pot'
        self.assertTrue(paths)
        for path in [*paths, template]:
            with self.subTest(catalog=path), file_open(path, 'rb', env=self.env) as po_file:
                rows = [
                    row for row in translation_file_reader(po_file, 'po')
                    if (row['module'], row.get('imd_name')) == DEMO_CAPTURE_HELP
                ]
                self.assertEqual([(row['name'], row['src']) for row in rows],
                                 [('ir.model.fields,help', source)])
