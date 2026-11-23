import re

from lxml import etree

from odoo.tests.common import TransactionCase, tagged

PRODUCT_NAME = re.compile(r'\bOdoo\b|odoo\.com', re.IGNORECASE)


@tagged('post_install', '-at_install')
class TestPaymentBrandSurfaces(TransactionCase):

    def test_provider_form_offers_no_onboarding_through_odoo(self):
        form = self.env.ref('payment.payment_provider_form')
        self.env['ir.ui.view'].create({
            'name': 'payment.provider.form.onboarding.test',
            'model': 'payment.provider',
            'inherit_id': form.id,
            'arch': """
                <data>
                    <group name="provider_credentials" position="before">
                        <div name="onboarding_test_group">
                            <button string="Connect" type="object" name="action_start_onboarding"/>
                            <button string="Other" type="object" name="action_toggle_is_published"/>
                        </div>
                    </group>
                </data>""",
        })
        arch = etree.fromstring(
            self.env['payment.provider'].get_view(view_id=form.id, view_type='form')['arch'])
        self.assertFalse(arch.xpath('//button[@name="action_start_onboarding"]'))
        self.assertTrue(arch.xpath('//button[@name="action_toggle_is_published"]'), 'other buttons stay')

    def test_enterprise_flag_is_not_offered_to_filters_and_groupings(self):
        self.assertNotIn('module_to_buy', self.env['payment.provider'].fields_get())
        self.assertNotIn('module_to_buy', self.env['payment.provider'].fields_get(attributes=['string', 'type']))
        info = self.env['payment.provider'].fields_get(['module_to_buy'], attributes=['string'])
        self.assertIn('module_to_buy', info, 'a view still reads the field')
        views = self.env['payment.provider'].get_views([(False, 'kanban')])
        fields = views['models']['payment.provider']['fields']
        self.assertIn('module_to_buy', fields, 'the kanban card still reads the field')
        self.assertFalse(fields['module_to_buy']['groupable'])

    def test_payment_method_configuration_note_does_not_name_odoo(self):
        arch = etree.fromstring(self.env['payment.method'].get_view(
            view_id=self.env.ref('payment.payment_method_form').id, view_type='form')['arch'])
        notes = arch.xpath("//page[@name='configuration']/div[hasclass('alert-warning')]")
        self.assertEqual(len(notes), 1)
        text = ' '.join(notes[0].itertext())
        self.assertNotRegex(text, PRODUCT_NAME)
        self.assertIn('Viindoo', text)

    def test_field_helps_do_not_name_odoo(self):
        for model, name in (
            ('payment.provider', 'capture_manually'),
            ('payment.provider', 'support_refund'),
            ('payment.method', 'support_refund'),
        ):
            with self.subTest(field='%s.%s' % (model, name)):
                help_text = self.env[model].fields_get([name], attributes=['help'])[name]['help']
                self.assertNotRegex(help_text, PRODUCT_NAME)

    def test_payment_method_configuration_note_uses_the_icon_font_of_the_series(self):
        arch = etree.fromstring(self.env['payment.method'].get_view(
            view_id=self.env.ref('payment.payment_method_form').id, view_type='form')['arch'])
        icons = arch.xpath("//page[@name='configuration']/div[hasclass('alert-warning')]/i")
        self.assertEqual(len(icons), 1)
        self.assertEqual(icons[0].get('data-icon'), 'warning')
        self.assertFalse(set((icons[0].get('class') or '').split()) & {'fa', 'fa-exclamation-triangle'})
