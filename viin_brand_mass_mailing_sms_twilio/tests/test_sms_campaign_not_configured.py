from odoo import fields
from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.sms_twilio.tests.common import MockSmsTwilio
from odoo.exceptions import RedirectWarning, UserError
from odoo.tests.common import tagged


@tagged('post_install', '-at_install')
class TestSmsCampaignNotConfigured(MockSmsTwilio):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_admin.sudo().write({
            'sms_provider': 'twilio',
            'sms_twilio_account_sid': False,
            'sms_twilio_auth_token': False,
        })
        cls.partner_model = cls.env['ir.model']._get('res.partner')

    def _make_mailing(self, mailing_type='sms', user=None):
        return self.env['mailing.mailing'].with_user(user or self.user_admin).create({
            'subject': 'Campaign',
            'email_from': 'sender@example.com',
            'mailing_type': mailing_type,
            'mailing_model_id': self.partner_model.id,
            'body_plaintext': 'Hello',
            'body_html': '<p>Hello</p>',
        })

    def test_send_of_an_sms_campaign_stops_and_offers_the_settings(self):
        mailing = self._make_mailing()
        with self.assertRaises(RedirectWarning) as caught:
            mailing.action_put_in_queue()
        self.assertEqual(caught.exception.args[1]['res_model'], 'res.config.settings')
        self.assertEqual(mailing.state, 'draft')

    def test_schedule_of_an_sms_campaign_stops_before_the_date_dialog(self):
        with self.assertRaises(RedirectWarning):
            self._make_mailing().action_schedule()

    def test_send_now_of_an_sms_campaign_stops(self):
        with self.assertRaises(RedirectWarning):
            self._make_mailing().action_send_mail()

    def test_test_send_of_an_sms_campaign_stops(self):
        mailing = self._make_mailing()
        wizard = self.env['mailing.sms.test'].with_user(self.user_admin).create({
            'mailing_id': mailing.id,
            'numbers': self.twilio_valid_phone_number,
        })
        with self.assertRaises(RedirectWarning):
            wizard.action_send_sms()

    def test_a_user_who_cannot_configure_reads_the_sentence_without_a_button(self):
        marketer = mail_new_test_user(
            self.env, login='sms_marketer', groups='base.group_user,mass_mailing.group_mass_mailing_user',
        )
        mailing = self._make_mailing(user=marketer)
        with self.assertRaises(UserError) as caught:
            mailing.action_put_in_queue()
        self.assertNotIsInstance(caught.exception, RedirectWarning)

    def test_an_email_campaign_is_not_stopped(self):
        mailing = self._make_mailing(mailing_type='mail')
        mailing.action_put_in_queue()
        self.assertEqual(mailing.state, 'in_queue')

    def test_a_company_with_a_twilio_account_queues_its_sms_campaign(self):
        self._setup_sms_twilio(self.company_admin)
        mailing = self._make_mailing()
        mailing.action_put_in_queue()
        self.assertEqual(mailing.state, 'in_queue')

    def test_a_cron_queues_an_sms_campaign_without_a_warning(self):
        mailing = self._make_mailing()
        mailing.with_context(cron_id=1).action_put_in_queue()
        self.assertEqual(mailing.state, 'in_queue')

    def test_an_automation_running_as_superuser_queues_an_sms_campaign_without_a_warning(self):
        mailing = self._make_mailing()
        mailing.sudo().action_put_in_queue()
        self.assertEqual(mailing.state, 'in_queue')

    def test_the_winner_of_an_sms_ab_test_is_queued_by_the_cron_even_without_a_twilio_account(self):
        campaign = self.env['utm.campaign'].create({
            'name': 'A/B campaign',
            'ab_testing_winner_selection': 'clicks_ratio',
            'ab_testing_schedule_datetime': fields.Datetime.subtract(fields.Datetime.now(), hours=1),
        })
        mailing = self._make_mailing()
        mailing.write({'campaign_id': campaign.id, 'ab_testing_enabled': True, 'state': 'done'})
        self.env['utm.campaign']._cron_process_mass_mailing_ab_testing()
        self.assertEqual(campaign.ab_testing_winner_mailing_id.state, 'in_queue')
