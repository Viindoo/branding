from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAttendanceSettings(TransactionCase):

    def setUp(self):
        super().setUp()
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        self.doc = etree.fromstring(arch)

    def test_the_backend_check_in_setting_names_viindoo(self):
        setting = self.doc.xpath("//setting[field[@name='attendance_from_systray']]")[0]
        self.assertIn('Viindoo', setting.get('help'))
        self.assertNotIn('Odoo', setting.get('help'))
