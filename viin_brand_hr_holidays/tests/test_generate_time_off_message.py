from datetime import date
from unittest.mock import patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestGenerateTimeOffMessage(TransactionCase):

    def test_overlapping_hourly_time_off_is_refused_in_the_name_of_viindoo(self):
        employee = self.env['hr.employee'].create({'name': 'Hourly Employee'})
        leave_type = self.env['hr.work.entry.type'].create({
            'name': 'Hourly Leave',
            'code': 'HOURLY_LEAVE',
            'leave_validation_type': 'no_validation',
            'request_unit': 'hour',
            'requires_allocation': False,
        })
        self.env['hr.leave'].create({
            'name': 'Dentist',
            'employee_id': employee.id,
            'work_entry_type_id': leave_type.id,
            'request_date_from': date(2026, 3, 2),
            'request_date_to': date(2026, 3, 2),
            'request_hour_from': 9,
            'request_hour_to': 10,
        })
        wizard = self.env['hr.leave.generate.multi.wizard'].create({
            'employee_ids': [(6, 0, employee.ids)],
            'work_entry_type_id': leave_type.id,
            'date_from': date(2026, 3, 2),
            'date_to': date(2026, 3, 2),
            'hour_from': 9,
            'hour_to': 10,
        })
        with self.assertRaises(UserError) as caught:
            wizard.action_generate_time_off()
        self.assertIn('Viindoo', str(caught.exception))
        self.assertNotIn('Odoo', str(caught.exception))

    def test_a_validation_error_of_the_wizard_keeps_its_class_and_names_viindoo(self):
        leave_type = self.env['hr.work.entry.type'].create({
            'name': 'Any Leave',
            'code': 'ANY_LEAVE',
            'requires_allocation': False,
        })
        wizard = self.env['hr.leave.generate.multi.wizard'].create({
            'work_entry_type_id': leave_type.id,
            'date_from': date(2026, 3, 2),
            'date_to': date(2026, 3, 2),
        })
        core_method = (
            'odoo.addons.hr_holidays.wizard.hr_leave_generate_multi_wizard.'
            'HrLeaveGenerateMultiWizard.action_generate_time_off'
        )
        with patch(core_method, side_effect=ValidationError('Odoo cannot generate this time off')):
            with self.assertRaises(ValidationError) as caught:
                wizard.action_generate_time_off()
        self.assertIn('Viindoo', str(caught.exception))
        self.assertNotIn('Odoo', str(caught.exception))
