# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import tools
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.misc import file_path


@tagged("post_install", "-at_install")
class TestWebPushIconDebrand(TransactionCase):
    """The web-push notification icon must be Viindoo-branded, not the Odoo mascot.

    Core (``mail.thread._notify_by_web_push_prepare_payload``) falls back to the
    Odoo default icon (``/web/static/img/odoo-icon-192x192.png``) whenever a push
    notification has no author (e.g. a guest sender). ``viin_brand_mail`` inherits
    that method to replace this default with the Viindoo app icon
    (``/viin_brand_web/static/img/viindoo-icon-192x192.png``) - the size-correct
    192x192 asset, not this module's own ``static/img/viindoo_app_icon.png`` (95x95px).

    The substitution is UNCONDITIONAL: it must not depend on ``test_enable``, on a
    context key, or on any other runtime switch. A previous implementation gated it
    on ``not tools.config.get('test_enable')`` plus an opt-in
    ``viin_brand_mail_force_web_push_debrand`` context key. That shape was wrong in
    two ways: the de-brand would have silently switched OFF on any server started
    with ``--test-enable``, and the branch that actually ships to production was
    exercised by no test at all - the tests only ever drove the forced-on branch.

    The core test whose assertion this de-brand invalidates
    (``test_mail.tests.test_mail_push.TestWebPushNotification
    .test_notify_by_push_channel``, which asserts the literal Odoo icon for a guest
    sender) is NOT neutered: this module's ``post_load()`` wraps it so the de-brand is
    bypassed for the duration of that one test, which keeps all 13 of its assertions
    running against core's own behaviour. That makes the cases below the only
    protection for the de-brand itself, so they must stay exhaustive.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Debrand Web Push Partner"})

    def _make_message(self, author_id=False):
        return self.env["mail.message"].sudo().create({
            "model": "res.partner",
            "res_id": self.partner.id,
            "author_id": author_id,
            "message_type": "comment",
            "body": "<p>Push payload test</p>",
        })

    def test_anonymous_push_icon_is_debranded(self):
        """An authorless push notification uses the Odoo default icon in core -
        our override must replace it with the Viindoo app icon."""
        message = self._make_message(author_id=False)
        payload = self.partner._notify_by_web_push_prepare_payload(message)
        self.assertEqual(
            payload["options"]["icon"],
            "/viin_brand_web/static/img/viindoo-icon-192x192.png",
            "Anonymous web-push notifications must show the Viindoo app icon, "
            "not the Odoo default mascot",
        )

    def test_authored_push_icon_is_left_unchanged(self):
        """A push notification with an author already carries the author's own
        avatar icon - the de-brand substitution must leave it untouched."""
        message = self._make_message(author_id=self.partner.id)
        payload = self.partner._notify_by_web_push_prepare_payload(message)
        expected_icon = "/web/image/res.partner/%d/avatar_128" % self.partner.id
        self.assertEqual(
            payload["options"]["icon"],
            expected_icon,
            "A push notification with an author must keep the author's avatar icon",
        )

    def test_debrand_does_not_depend_on_test_enable(self):
        """Regression guard on the SHAPE of the production code path.

        The de-brand must fire even though ``test_enable`` is set - that flag is
        true process-wide under Odoo's test runner, so if the production method
        ever branches on it again (or on any opt-in context key), this test fails.
        This is what keeps the shipped behaviour and the tested behaviour identical
        instead of testing a branch customers never execute.
        """
        self.assertTrue(
            tools.config.get('test_enable'),
            "This test must run under Odoo's test runner (test_enable=True) "
            "to be meaningful",
        )
        message = self._make_message(author_id=False)
        payload = self.partner._notify_by_web_push_prepare_payload(message)
        self.assertEqual(
            payload["options"]["icon"],
            "/viin_brand_web/static/img/viindoo-icon-192x192.png",
            "The de-brand must apply regardless of test_enable - the production "
            "code path must have exactly one shape",
        )

    def test_debrand_icon_path_resolves_to_a_real_file_on_disk(self):
        """The icon path this override emits must resolve to a REAL FILE on disk.

        The two literal-string assertions above only prove the code emits a
        particular string; they would stay green even if the file behind that
        string had moved or been deleted, because a string comparison has no
        opinion about the filesystem. That is exactly what happened here: the
        code kept emitting ``/viin_brand_common/static/img/viindoo-icon-192x192.png``
        after that file was removed from ``viin_brand_common/static/img/`` - no
        exception, no log line, just a 404 image rendered in a real push
        notification. This test resolves the code's own returned path through
        Odoo's addons-path file lookup (the same mechanism the web server uses to
        serve ``/<module>/static/...`` URLs) so a future silent 404 fails loudly
        here instead of shipping quietly.
        """
        message = self._make_message(author_id=False)
        payload = self.partner._notify_by_web_push_prepare_payload(message)
        icon_path = payload["options"]["icon"]
        # icon_path has the shape "/<module>/static/img/<file>.png" - file_path()
        # expects an addons-path-relative path with no leading slash.
        relative_path = icon_path.lstrip("/")
        try:
            resolved_path = file_path(relative_path)
        except FileNotFoundError:
            resolved_path = None
        self.assertIsNotNone(
            resolved_path,
            "The web-push icon path %r returned by the de-brand override does not "
            "resolve to any file under the addons path. This is the silent-404 "
            "failure mode: the code can emit a well-formed-looking path to an "
            "asset that no longer exists, and a bare string-equality assertion "
            "cannot catch that." % icon_path,
        )
