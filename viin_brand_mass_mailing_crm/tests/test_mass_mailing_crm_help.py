# Part of Viindoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMassMailingCrmHelp(TransactionCase):

    def test_leads_helper_says_viindoo_cannot_track_replies(self):
        mailing = self.env["mailing.mailing"].create({"subject": "Newsletter"})

        action = mailing.action_redirect_to_leads_and_opportunities()

        self.assertIn("Viindoo cannot track replies", action["help"])
        self.assertNotIn("the system", action["help"])
