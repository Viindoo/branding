from odoo.tests.common import TransactionCase, tagged

TEMPLATE_XMLID = 'lunch.lunch_order_mail_supplier'


@tagged('post_install', '-at_install')
class TestMailFooter(TransactionCase):

    def _body(self):
        return self.env.ref(TEMPLATE_XMLID).with_context(lang='en_US').body_html

    def _assert_powered_by_viindoo(self):
        body = self._body()
        self.assertNotIn('odoo.com', body)
        self.assertRegex(body, r'href="https://viindoo\.com[^"]*"[^>]*>Viindoo</a>')

    def test_the_supplier_order_mail_is_powered_by_viindoo(self):
        self._assert_powered_by_viindoo()

    def test_an_update_of_lunch_that_restores_the_core_body_is_rewritten_again(self):
        template = self.env.ref(TEMPLATE_XMLID)
        template.body_html = str(template.body_html).replace('https://viindoo.com', 'https://www.odoo.com').replace(
            '>Viindoo</a>', '>Odoo</a>',
        )
        self.assertIn('odoo.com', self._body())
        self.env['mail.template']._debrand_lunch_supplier_footer()
        self._assert_powered_by_viindoo()
