from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestContactsBrandHelp(TransactionCase):

    def test_contacts_empty_state_names_viindoo_not_odoo(self):
        help_text = self.env.ref('contacts.action_contacts').help

        self.assertTrue(help_text)
        self.assertNotRegex(help_text, r'\bOdoo\b')
        self.assertRegex(help_text, r'\bViindoo\b')
