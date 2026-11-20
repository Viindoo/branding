from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestScenarioDebrand(TransactionCase):

    def _assert_job_description_names_no_product(self):
        description = self.env.ref('hr.job_ceo').description
        self.assertNotIn('Odoo', description)
        self.assertNotIn('Viindoo', description)
        self.assertIn('Demonstration of different services for each client', description)

    def test_scenario_job_description_names_no_product(self):
        self.env['hr.employee']._load_scenario()
        self._assert_job_description_names_no_product()

    def test_demo_data_job_description_names_no_product(self):
        self.env['hr.employee']._load_demo_data()
        self._assert_job_description_names_no_product()
