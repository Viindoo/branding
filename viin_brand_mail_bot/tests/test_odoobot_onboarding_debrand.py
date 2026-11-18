from odoo.tests.common import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestOdoobotOnboardingDebrand(TransactionCase):
    """ViindooBot's automatic first message to a new internal user is branded Viindoo.

    The message is posted by ``res.users._init_odoobot()`` when the web client boots for a user
    whose onboarding has not started; it reads "Viindoo" and carries no "Odoo" text.
    """

    def test_odoobot_first_onboarding_message_is_not_branded_odoo(self):
        odoobot = self.env.ref("base.partner_root")
        new_user = new_test_user(
            self.env, login="s33_new_internal_user", groups="base.group_user",
        )
        self.assertIn(
            new_user.odoobot_state, (False, "not_initialized"),
            "precondition: a freshly created internal user must not already be "
            "past the odoobot onboarding flow",
        )

        channel = new_user.with_user(new_user)._init_odoobot()

        bot_messages = channel.message_ids.filtered(lambda m: m.author_id == odoobot)
        self.assertTrue(
            bot_messages,
            "ViindooBot must post an onboarding message to the new user's DM "
            "channel when _init_odoobot() runs",
        )
        body = bot_messages[0].body

        self.assertNotIn(
            "Odoo", body,
            "ViindooBot's first onboarding message must not contain the Odoo "
            "brand name",
        )
        self.assertIn(
            "Viindoo", body,
            "ViindooBot's first onboarding message must be branded Viindoo",
        )
