# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCoreBotRestorationCoverage(TransactionCase):
    """The core-bot restoration fixture must actually cover every suite it claims to.

    ``data/res_partner_data.xml`` de-brands ``base.partner_root`` to
    ``ViindooBot`` - a deliberate, shipped product behaviour
    (``test_partner_root_debrand.py``). Because that record is core-owned and
    a number of core suites assert the stock ``OdooBot`` naming on it,
    ``__init__.py``'s ``post_load()`` monkeypatches ``setUpClass`` (or, for
    ``TestWebPushNotification``, one specific test method) on a short,
    explicit list of core test base classes so those suites see core's own
    naming instead of this module's de-brand.

    That list previously missed ``mail.tests.discuss.test_ui.TestUi`` - a
    plain ``HttpCase`` subclass (``HttpCaseWithUserDemo``, NOT ``MailCommon``)
    whose ``test_05_can_create_channel_tour`` renders the Discuss sidebar and
    reads the bot's live ``name``. The gap was silent: nothing asserted that
    the fixture's claimed coverage matched its actual coverage, so the drift
    surfaced only as a core tour timing out on a selector that could never
    match (``.o-mail-DiscussSidebarChannel-itemName:contains(OdooBot)``),
    weeks after the coverage actually lapsed.

    Each assertion below is a coverage-drift trip wire, not a proxy for the
    restored behaviour itself: it asserts the named target's OWN class/method
    dictionary carries our monkeypatch, directly on the class rather than
    merely inherited, so a future edit that narrows or drops a target from
    ``post_load()`` fails HERE immediately instead of surfacing later as an
    unrelated core tour timeout. The restored behaviour itself is exercised
    end-to-end by core's own suites (e.g. ``test_discuss_full.tests.
    test_performance``, and - after this fix - ``mail.tests.discuss.test_ui.
    TestUi.test_05_can_create_channel_tour``); the committed de-brand stays
    protected by ``test_partner_root_debrand.py``, untouched by any of this.
    """

    def test_mail_common_setupclass_is_wrapped(self):
        from odoo.addons.mail.tests.common import MailCommon
        self.assertIn(
            "setUpClass", MailCommon.__dict__,
            "post_load() must monkeypatch MailCommon.setUpClass directly on "
            "the class (not merely inherit it unchanged) so every "
            "MailCommon-derived core suite sees the restored OdooBot naming",
        )

    def test_discuss_test_ui_setupclass_is_wrapped(self):
        """Regression guard for the actual bug this test file was added for.

        ``mail.tests.discuss.test_ui.TestUi`` derives from
        ``HttpCaseWithUserDemo``, NOT ``MailCommon`` - the MailCommon-only
        fixture never reaches it, so its tours (e.g.
        ``test_05_can_create_channel_tour``) see the de-branded ``ViindooBot``
        name instead of core's own ``OdooBot``.
        """
        from odoo.addons.base.tests.common import HttpCaseWithUserDemo
        from odoo.addons.mail.tests.discuss.test_ui import TestUi
        self.assertIn(
            "setUpClass", TestUi.__dict__,
            "post_load() must monkeypatch mail.tests.discuss.test_ui.TestUi."
            "setUpClass directly on the class so its tours see the restored "
            "OdooBot naming instead of the de-branded ViindooBot name",
        )
        self.assertIsNot(
            TestUi.setUpClass.__func__,
            HttpCaseWithUserDemo.setUpClass.__func__,
            "TestUi.setUpClass must be a DIFFERENT function object than the "
            "plain inherited HttpCaseWithUserDemo.setUpClass - identity here "
            "is the direct proof the monkeypatch was actually applied to "
            "this class, not merely inherited unchanged",
        )

    def test_web_push_notification_test_method_is_wrapped(self):
        try:
            from odoo.addons.test_mail.tests.test_mail_push import TestWebPushNotification
        except ImportError:
            self.skipTest("test_mail is not installed in this database")
        self.assertIn(
            "test_notify_by_push_channel", TestWebPushNotification.__dict__,
            "post_load() must monkeypatch "
            "TestWebPushNotification.test_notify_by_push_channel directly on "
            "the class so this module's web-push de-brand is bypassed for "
            "that one test and its 13 assertions run against core's own "
            "behaviour",
        )

    def test_sync_google_setupclass_is_wrapped(self):
        try:
            from odoo.addons.google_calendar.tests.test_sync_common import TestSyncGoogle
        except ImportError:
            self.skipTest("google_calendar is not installed in this database")
        self.assertIn(
            "setUpClass", TestSyncGoogle.__dict__,
            "post_load() must monkeypatch TestSyncGoogle.setUpClass directly "
            "on the class so google_calendar's sync suites see the restored "
            "OdooBot organizer identity instead of the de-branded one",
        )
