from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestActionHelp(TransactionCase):

    def test_fleet_empty_states_name_viindoo_not_odoo_or_the_system(self):
        for xmlid in (
            'fleet.fleet_vehicle_odometer_reporting_action',
            'fleet.fleet_vehicle_log_contract_action',
        ):
            with self.subTest(action=xmlid):
                help_text = self.env.ref(xmlid).help
                self.assertIn('Viindoo', help_text)
                self.assertNotIn('Odoo', help_text)
                self.assertNotIn('The system', help_text)
