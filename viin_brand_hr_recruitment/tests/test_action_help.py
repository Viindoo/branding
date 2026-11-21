from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestActionHelp(TransactionCase):

    def test_applications_empty_states_name_viindoo_not_odoo(self):
        for xmlid in ('hr_recruitment.action_hr_job_applications', 'hr_recruitment.crm_case_categ0_act_job'):
            with self.subTest(action=xmlid):
                help_text = self.env.ref(xmlid).help
                self.assertIn('Viindoo helps you track applicants', help_text)
                self.assertNotIn('Odoo', help_text)
