from urllib.parse import urlparse

from lxml import etree

from odoo.tests.common import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestOdoobotOnboardingDebrand(TransactionCase):
    """ViindooBot speaks as Viindoo through the whole onboarding tour, in the first message and in every answer.

    The tour is walked the way a user walks it: the messages are posted on the chat of the bot.
    """

    def _walk_tour(self, lang):
        """Walk the onboarding tour in a language, then ask for help.

        :return: the user and the bodies of the messages of the bot, by stage of the tour
        """
        odoobot = self.env.ref("base.partner_root")
        env = self.env(context=dict(self.env.context, lang=lang))
        user = new_test_user(env, login="odoobot_tour_%s" % lang, groups="base.group_user")
        user_env = env(user=user)
        channel = user_env["res.users"].browse(user.id)._init_odoobot()
        stages = {}

        def bot_bodies():
            # sudo: read-back of what the bot posted; the test asserts the text, not the reader's access
            messages = channel.sudo().message_ids.filtered(lambda message: message.author_id == odoobot)
            return messages.sorted("id").mapped("body")

        stages["first_message"] = bot_bodies()
        seen = len(stages["first_message"])

        def say(stage, body, **kwargs):
            nonlocal seen
            kwargs.setdefault("channel", channel)
            posting_channel = kwargs.pop("channel")
            posting_channel.message_post(
                body=body, message_type="comment", subtype_xmlid="mail.mt_comment", **kwargs,
            )
            bodies = bot_bodies()
            stages[stage] = bodies[seen:]
            seen = len(bodies)

        say("ping_prompt", "😊")
        say("ping_repeat", "hello there")
        say("attachment_prompt", "hi bot", partner_ids=[odoobot.id])
        attachment = user_env["ir.attachment"].create({
            "name": "dog.png", "raw": b"dog", "res_model": "discuss.channel", "res_id": channel.id,
        })
        say("canned_prompt", "a picture", attachment_ids=[attachment.id])
        canned_responses = user_env["mail.canned.response"].search([("create_uid", "=", user.id)])
        say(
            "command_prompt", "thanks",
            channel=channel.with_context(canned_response_ids=canned_responses.ids),
        )
        channel.execute_command_help()
        bodies = bot_bodies()
        stages["end_of_tour"] = bodies[seen:]
        seen = len(bodies)
        say("help_answer", "help")
        return user, stages

    def _assert_branded_viindoo(self, bodies):
        self.assertTrue(bodies)
        for body in bodies:
            self.assertNotIn("Odoo", body)
        self.assertTrue(any("Viindoo" in body for body in bodies))

    def test_every_message_of_the_tour_is_branded_viindoo(self):
        user, stages = self._walk_tour("en_US")

        for stage, bodies in stages.items():
            with self.subTest(stage=stage):
                self.assertTrue(bodies)
                for body in bodies:
                    self.assertNotIn("Odoo", body)
        self.assertEqual(user.odoobot_state, "idle")

    def test_the_prompts_to_mention_the_bot_name_it_viindoobot(self):
        user, stages = self._walk_tour("en_US")

        for stage in ("ping_prompt", "ping_repeat"):
            with self.subTest(stage=stage):
                self._assert_branded_viindoo(stages[stage])
                self.assertIn("@ViindooBot", stages[stage][0])

    def test_the_end_of_tour_answer_is_branded_viindoo(self):
        _user, stages = self._walk_tour("en_US")
        self._assert_branded_viindoo(stages["end_of_tour"])

    def test_the_help_answer_links_to_viindoo_pages(self):
        _user, stages = self._walk_tour("en_US")

        links = [
            urlparse(href)
            for body in stages["help_answer"]
            for href in etree.HTML(str(body)).xpath("//a/@href")
        ]
        self.assertTrue(links)
        self.assertEqual({link.netloc for link in links}, {"www.viindoo.com"})
        self.assertEqual({link.path for link in links}, {"/documentation", "/slides"})

    def test_a_translated_tour_is_branded_viindoo(self):
        self.env["res.lang"]._activate_lang("de_DE")
        _user, english_stages = self._walk_tour("en_US")
        _user, translated_stages = self._walk_tour("de_DE")

        for stage, bodies in translated_stages.items():
            with self.subTest(stage=stage):
                self.assertNotEqual(bodies, english_stages[stage], "the stage is not translated")
                for body in bodies:
                    self.assertNotIn("Odoo", body)
        for stage in ("first_message", "ping_prompt", "ping_repeat", "end_of_tour"):
            with self.subTest(stage=stage):
                self._assert_branded_viindoo(translated_stages[stage])
