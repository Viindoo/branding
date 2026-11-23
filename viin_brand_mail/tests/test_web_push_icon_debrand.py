# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import tools
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.misc import file_path


@tagged("post_install", "-at_install")
class TestWebPushIconDebrand(TransactionCase):
    """The web-push notification icon is Viindoo-branded, not the Odoo mascot.

    Core falls back to the Odoo default icon whenever a push notification has no author (e.g. a
    guest sender). ``viin_brand_mail`` replaces it with the 192x192 Viindoo app icon of
    ``viin_brand``. The substitution is unconditional: it does not depend on ``test_enable`` or on
    any other runtime switch, so the tested code path is the one that ships.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Debrand Web Push Partner"})

    def _make_message(self, author_id=False):
        # sudo: arrange - the message is created for a guest author the test user cannot create for
        return self.env["mail.message"].sudo().create({
            "model": "res.partner",
            "res_id": self.partner.id,
            "author_id": author_id,
            "message_type": "comment",
            "body": "<p>Push payload test</p>",
        })

    def test_anonymous_push_icon_is_debranded(self):
        """An authorless push notification shows the Viindoo app icon."""
        message = self._make_message(author_id=False)
        payload = self.partner._notify_by_web_push_prepare_payload(message)
        self.assertEqual(
            payload["options"]["icon"],
            "/viin_brand/static/img/viindoo-icon-192x192.png",
            "Anonymous web-push notifications must show the Viindoo app icon, "
            "not the Odoo default mascot",
        )

    def test_authored_push_icon_is_left_unchanged(self):
        """A push notification with an author keeps the author's avatar icon."""
        message = self._make_message(author_id=self.partner.id)
        payload = self.partner._notify_by_web_push_prepare_payload(message)
        expected_icon = "/web/image/res.partner/%d/avatar_128" % self.partner.id
        self.assertEqual(
            payload["options"]["icon"],
            expected_icon,
            "A push notification with an author must keep the author's avatar icon",
        )

    def test_debrand_does_not_depend_on_test_enable(self):
        """The de-brand applies even though ``test_enable`` is set, as under any test runner."""
        self.assertTrue(
            tools.config.get('test_enable'),
            "This test must run under Odoo's test runner (test_enable=True) "
            "to be meaningful",
        )
        message = self._make_message(author_id=False)
        payload = self.partner._notify_by_web_push_prepare_payload(message)
        self.assertEqual(
            payload["options"]["icon"],
            "/viin_brand/static/img/viindoo-icon-192x192.png",
            "The de-brand must apply regardless of test_enable - the production "
            "code path must have exactly one shape",
        )

    def test_debrand_icon_path_resolves_to_a_real_file_on_disk(self):
        """The icon path the override emits resolves to a real file under the addons path."""
        message = self._make_message(author_id=False)
        payload = self.partner._notify_by_web_push_prepare_payload(message)
        icon_path = payload["options"]["icon"]
        # file_path() expects an addons-path-relative path with no leading slash
        relative_path = icon_path.lstrip("/")
        try:
            resolved_path = file_path(relative_path)
        except FileNotFoundError:
            resolved_path = None
        self.assertIsNotNone(
            resolved_path,
            "The web-push icon path %r returned by the de-brand override does not "
            "resolve to any file under the addons path." % icon_path,
        )
