from odoo.tests.common import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestOdoobotOnboardingDebrand(TransactionCase):
    """ViindooBot's automatic first DM to a new internal user must not read "Odoo".

    Business rule (BUG S33-1; MASTER_DESIGN_DOC scenario S33 - "no console error ...
    no 'Odoo' text/logo visible anywhere in the Discuss UI"): the very first message
    ViindooBot posts to a brand-new internal user's private chat - the "onboarding
    emoji" step triggered on webclient bootstrap - must be fully de-branded. No
    "Odoo" text may appear anywhere in that message; it must read "Viindoo" instead.

    Root cause (traced, not yet fixed at authoring time). Core's
    ``mail_bot.models.res_users.ResUsers._init_odoobot()``
    (odoo/addons/mail_bot/models/res_users.py:33-50) is a self-contained method with
    no separate hook/override point: it builds the whole ``Markup`` message inline
    from three ``_(...)`` pieces, and the middle piece is hardcoded at line 39:
    ``_("Odoo's chat helps employees collaborate efficiently. I'm here to help you
    discover its features.")``. That ``Markup`` is posted directly via
    ``channel.sudo().message_post(...)`` (lines 42-48).

    ``viin_brand_mail_bot/models/mail_bot.py`` already de-brands every OTHER bot
    message via ``mail.bot._get_answer()`` overrides (the onboarding_command /
    onboarding_canned / onboarding_ping paths use ``self.env._(...)`` with
    ``_get_style_dict()`` to inject "@ViindooBot", viindoo.com links, "Enjoy
    discovering Viindoo!"). That established de-brand convention never reaches the
    first-message case: ``_init_odoobot`` lives on ``res.users`` (not ``mail.bot``)
    and posts directly via ``message_post`` - it never calls ``_get_answer``.
    ``viin_brand_mail_bot/models/res_user.py`` currently only overrides the
    ``odoobot_state`` field's string label; it does not override ``_init_odoobot``.

    RED (current, pre-fix): fails because the posted body still contains the
    literal, capitalized substring "Odoo" and does not contain "Viindoo".
    GREEN (post-fix): once ``viin_brand_mail_bot/models/res_user.py`` gets a full
    ``_init_odoobot()`` override that replicates core's method (same channel
    lookup, same Markup structure, same message_post call, same odoobot_state
    assignment) with only that middle sentence re-branded to "Viindoo's chat helps
    employees collaborate efficiently...", the posted body will contain "Viindoo"
    and no "Odoo".

    Trigger path: this test calls ``_init_odoobot()`` directly on a fresh internal
    user (mirroring core's own precedent,
    ``test_mail_full.tests.test_mail_bot.TestOdoobot.test_fetch_listener``:
    ``self.user_employee.with_user(self.user_employee)._init_odoobot()``), which is
    the same method core's ``_on_webclient_bootstrap()`` calls for every new
    internal user whose ``odoobot_state`` is not yet initialized.
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
            "brand name (core mail_bot/models/res_users.py:39 hardcodes \"Odoo's "
            "chat helps employees collaborate efficiently...\" with no override "
            "hook a de-brand module can intercept)",
        )
        self.assertIn(
            "Viindoo", body,
            "ViindooBot's first onboarding message must be branded Viindoo, "
            "matching the de-brand style already applied to every other bot "
            "message in viin_brand_mail_bot/models/mail_bot.py",
        )
