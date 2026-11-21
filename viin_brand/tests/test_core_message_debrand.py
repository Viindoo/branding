import re
from unittest.mock import patch

from odoo.exceptions import RedirectWarning, UserError
from odoo.tests.common import TransactionCase, tagged

ODOO_WORD = re.compile(r'\bOdoo\b')


@tagged('post_install', '-at_install')
class TestCoreMessageDebrand(TransactionCase):
    """The messages and texts of base that name the product name Viindoo, in their source language."""

    def assertViindoo(self, text):
        self.assertNotRegex(text, ODOO_WORD)
        self.assertIn('Viindoo', text)

    def test_multi_company_access_error_names_viindoo(self):
        companies = self.env['res.company'].create([{'name': 'Debrand A'}, {'name': 'Debrand B'}])
        partners = self.env['res.partner'].create([
            {'name': 'Debrand partner A', 'company_id': companies[0].id},
            {'name': 'Debrand partner B', 'company_id': companies[1].id},
        ])
        self.env['ir.rule'].create({
            'name': 'Debrand company rule',
            'model_id': self.env['ir.model']._get('res.partner').id,
            'domain_force': "[('company_id', 'in', company_ids)]",
        })
        user = self.env['res.users'].create({
            'name': 'Debrand user', 'login': 'debrand_user',
            'group_ids': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        error = self.env['ir.rule'].with_user(user)._make_access_error('read', partners)

        self.assertViindoo(str(error))

    def test_pdf_merge_errors_name_viindoo(self):
        Report = self.env['ir.actions.report']
        with self.assertRaises(UserError) as caught:
            Report._handle_merge_pdfs_error()
        self.assertViindoo(str(caught.exception))

        warning = RedirectWarning('Odoo is unable to merge the generated PDFs.', {}, 'Open')
        with patch.object(type(Report), '_pre_render_qweb_pdf', side_effect=warning):
            with self.assertRaises(RedirectWarning) as caught:
                Report._render_qweb_pdf('base.report_irmodulereference', [self.env.ref('base.module_base').id])
        self.assertViindoo(caught.exception.args[0])

    def test_pdf_merge_failure_names_viindoo(self):
        Report = self.env['ir.actions.report']
        failure = UserError('Odoo is unable to merge the generated PDFs.')
        with patch('odoo.addons.base.models.ir_actions_report.IrActionsReport._merge_pdfs', side_effect=failure):
            with self.assertRaises(UserError) as caught:
                Report._merge_pdfs([])
        self.assertViindoo(str(caught.exception))

    def test_module_operation_in_progress_names_viindoo(self):
        failure = UserError('Odoo is currently processing another module operation.')
        with patch(
            'odoo.addons.base.models.ir_module.IrModuleModule._button_immediate_function', side_effect=failure,
        ):
            with self.assertRaises(UserError) as caught:
                self.env['ir.module.module']._button_immediate_function(lambda modules: None)
        self.assertViindoo(str(caught.exception))

    def test_archiving_the_setup_language_names_viindoo(self):
        lang = self.env['res.lang']._activate_lang('fr_FR')
        user = self.env['res.users'].create({
            'name': 'Debrand inactive', 'login': 'debrand_inactive', 'lang': lang.code,
        })
        user.write({'active': False})
        user.partner_id.active = False

        with self.assertRaises(UserError) as caught:
            lang.active = False

        self.assertViindoo(str(caught.exception))

    def test_deleting_the_system_user_names_viindoo(self):
        with self.assertRaises(UserError) as caught:
            self.env.ref('base.user_root').sudo().unlink()

        self.assertViindoo(str(caught.exception))

    def test_empty_state_helps_name_viindoo(self):
        for xmlid in (
            'base.action_partner_form', 'base.action_partner_customer_form',
            'base.action_partner_supplier_form', 'base.action_res_company_form',
        ):
            with self.subTest(action=xmlid):
                self.assertViindoo(self.env.ref(xmlid).with_context(lang='en_US').help)

    def test_merge_wizard_text_names_viindoo(self):
        arch = re.sub(r'\s+', ' ', self.env['base.partner.merge.automatic.wizard'].get_view(view_type='form')['arch'])

        self.assertIn('Viindoo will propose', arch)
        self.assertNotRegex(arch, ODOO_WORD)

    def test_translation_export_wizard_keeps_the_core_sentence_about_the_odoo_project(self):
        arch = re.sub(r'\s+', ' ', self.env['base.language.export'].get_view(view_type='form')['arch'])

        self.assertIn('translating Odoo in your language', arch)
        self.assertFalse(self.env.ref('viin_brand.wizard_lang_export', raise_if_not_found=False))
