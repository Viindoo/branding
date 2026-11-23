from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestGs1BrandHelp(TransactionCase):

    def test_content_type_help_names_viindoo_not_odoo(self):
        fields = self.env['barcode.rule'].fields_get(['gs1_content_type'], attributes=['help', 'selection'])
        help_text = fields['gs1_content_type']['help']
        self.assertNotRegex(help_text, r'\bOdoo\b')
        for _value, label in fields['gs1_content_type']['selection']:
            with self.subTest(content_type=label):
                self.assertIn(label, help_text)
