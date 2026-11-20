from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestMailFooter(TransactionCase):

    def test_the_badge_mail_is_powered_by_viindoo(self):
        body = self.env.ref('gamification.email_template_badge_received').with_context(lang='en_US').body_html
        self.assertNotIn('odoo.com', body)
        self.assertRegex(body, r'href="https://viindoo\.com[^"]*"[^>]*>Viindoo</a>')
