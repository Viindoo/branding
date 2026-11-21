from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestGs1BrandHelp(TransactionCase):

    def test_content_type_help_names_viindoo_not_odoo(self):
        fields = self.env['barcode.rule'].fields_get(['gs1_content_type'], attributes=['help'])
        help_text = fields['gs1_content_type']['help']
        self.assertNotRegex(help_text, r'\bOdoo\b')
        self.assertIn('converted into a datetime', help_text)
        self.assertIn('Numeric Identifier', help_text)
