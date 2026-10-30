from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestTrialErrorDebrand(TransactionCase):
    """The trial-credits error of a failed letter must not send users to iap.odoo.com."""

    def test_trial_error_message_is_debranded_and_keeps_credits_link(self):
        message = self.env['snailmail.letter']._get_error_message('TRIAL_ERROR')
        self.assertNotIn('odoo.com', message, "The message must not name an Odoo website")
        self.assertIn(
            'href=test_url',
            message,
            "The message must still link to the page where the free credits are claimed",
        )
