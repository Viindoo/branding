from lxml import etree

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestExpenseDebrand(TransactionCase):

    def test_the_approval_mail_footer_links_to_viindoo(self):
        for xmlid in (
            'hr_expense.hr_expense_template_submitted_expenses',
            'hr_expense.hr_expense_template_register_no_user',
        ):
            with self.subTest(template=xmlid):
                arch = etree.tostring(self.env.ref(xmlid)._get_combined_arch(), encoding='unicode')
                footer = ''.join(etree.fromstring(arch).xpath('//a[contains(@href, "viindoo.com")]//text()'))
                self.assertEqual(footer, 'Viindoo')
                self.assertNotIn('odoo.com', arch)

    def test_the_stripe_card_setting_help_names_viindoo(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        setting = etree.fromstring(arch).xpath('//setting[@id="expense_cards_stripe_issuing"]')[0]
        self.assertIn('Viindoo', setting.get('help'))
        self.assertNotIn('Odoo', setting.get('help'))

    def test_the_missing_expense_account_error_names_viindoo(self):
        self.env.company.expense_account_id = False
        employee = self.env['hr.employee'].create({'name': 'Expense Employee'})
        expense = self.env['hr.expense'].create({
            'name': 'Lunch',
            'employee_id': employee.id,
            'total_amount_currency': 10.0,
        })
        with self.assertRaises(UserError) as caught:
            expense._get_base_account()
        self.assertIn('Viindoo', str(caught.exception))
        self.assertNotIn('Odoo', str(caught.exception))

    def test_the_digest_tip_names_viindoo(self):
        tip = self.env.ref('hr_expense.digest_tip_hr_expense_0')
        self.assertNotIn('Odoo', tip.with_context(lang='en_US').tip_description)
