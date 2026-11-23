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

    def _render_approval_mail(self, company):
        return str(self.env['ir.qweb']._render('hr_expense.hr_expense_template_submitted_expenses', {
            'manager_name': 'Brand Test Manager',
            'url': '/odoo/expenses-to-process',
            'company': company,
            'user': self.env.user,
            'total_amount': 10.0,
            'today_string': 'Monday',
            'first_expense_name': 'Lunch',
            'expenses_count': 1,
            'employee_breakdown': [{'name': 'Employee', 'amount': '10.00'}],
        }))

    def test_the_approval_mail_button_takes_the_company_colour(self):
        company = self.env.company
        company.email_secondary_color = '#123456'
        body = self._render_approval_mail(company)
        self.assertIn('background-color: #123456', body)
        self.assertNotRegex(body, r'(?i)#875A7B')

    def test_the_approval_mail_button_falls_back_to_the_brand_colour(self):
        company = self.env.company
        company.email_secondary_color = False
        self.assertIn('background-color: #7F4282', self._render_approval_mail(company))

    def test_the_approval_mail_names_viindoo_not_odoo(self):
        body = self._render_approval_mail(self.env.company)
        sentence = ' '.join(etree.HTML(body).xpath(
            "//p[contains(., 'Brand Test Manager')]/following-sibling::p[1]//text()"))
        self.assertIn('Viindoo', sentence)
        self.assertNotIn('Odoo', body)

    def test_the_missing_expense_account_error_names_viindoo(self):
        self.env.company.expense_account_id = False
        employee = self.env['hr.employee'].create({'name': 'Expense Employee'})
        expense = self.env['hr.expense'].create({
            'name': 'Lunch',
            'employee_id': employee.id,
            'total_amount_currency': 10.0,
            'payment_mode': 'company_account',
            'product_id': False,
            'account_id': False,
        })
        with self.assertRaises(UserError) as caught:
            expense._get_base_account()
        self.assertIn('Viindoo', str(caught.exception))
        self.assertNotIn('Odoo', str(caught.exception))

    def test_the_digest_tip_names_viindoo(self):
        tip = self.env.ref('hr_expense.digest_tip_hr_expense_0')
        self.assertNotIn('Odoo', tip.with_context(lang='en_US').tip_description)
