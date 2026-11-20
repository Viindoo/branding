import re

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged

PRODUCT_NAME = re.compile(r'\bOdoo\b|odoo\.com', re.IGNORECASE)


@tagged('post_install', '-at_install')
class TestProductDocuments(TransactionCase):

    def test_invalid_document_url_error_gives_a_neutral_example(self):
        product = self.env['product.template'].create({'name': 'Documented product'})
        document = self.env['product.document'].new({
            'name': 'Spec',
            'type': 'url',
            'url': 'not a url',
            'res_model': product._name,
            'res_id': product.id,
        })
        with self.assertRaises(ValidationError) as caught:
            document._onchange_url()
        message = caught.exception.args[0]
        self.assertNotRegex(message, PRODUCT_NAME)
        self.assertIn('https://example.com', message)
        self.assertIn('not a url', message)

    def test_documents_empty_state_does_not_send_users_to_odoo(self):
        product = self.env['product.template'].create({'name': 'Documented product'})
        for record in (product, product.product_variant_id):
            with self.subTest(model=record._name):
                help_text = record.with_context(lang='en_US').action_open_documents()['help']
                self.assertNotRegex(help_text, PRODUCT_NAME)
                self.assertNotIn('<a ', help_text)
