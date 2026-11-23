from lxml import etree

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestResumeLinePlaceholder(TransactionCase):

    def test_resume_line_title_placeholder_names_viindoo_not_odoo(self):
        arch = etree.fromstring(self.env['hr.resume.line'].get_view(
            view_id=self.env.ref('hr_skills.resume_line_view_form').id, view_type='form')['arch'])
        placeholder = arch.xpath("//field[@name='name']/@placeholder")[0]
        self.assertIn('Viindoo', placeholder)
        self.assertNotIn('Odoo', placeholder)
