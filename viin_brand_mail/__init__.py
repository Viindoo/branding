from odoo import tools

from . import models
from . import wizard

if tools.config.get('test_enable', False):
    from unittest.mock import patch

    from odoo.addons.mail.tests.common import MailCommon
    from odoo.addons.mail.tests.discuss.test_ui import TestUi as CoreDiscussTestUi

    from .models.mail_thread import MailThread as ViinBrandMailThread
    try:
        from odoo.addons.test_mail.tests.test_mail_push import TestWebPushNotification
    except ImportError:
        TestWebPushNotification = None
    try:
        from odoo.addons.google_calendar.tests.test_sync_common import TestSyncGoogle
    except ImportError:
        TestSyncGoogle = None


def _core_web_push_payload(self, message, msg_vals=False, force_record_name=False):
    """`_notify_by_web_push_prepare_payload` with this module's de-brand bypassed.

    Dispatches straight past our override to whatever implementation sits below it,
    so the caller observes stock Odoo behaviour (including the stock
    `odoo-icon-192x192.png` fallback) while any other module's override is still
    honoured.
    """
    return super(ViinBrandMailThread, self)._notify_by_web_push_prepare_payload(
        message, msg_vals, force_record_name=force_record_name,
    )


def _without_web_push_debrand(test_method_original):
    """Run a core test with this module's web-push de-brand temporarily disabled.

    `models/mail_thread.py` replaces the anonymous web-push icon with the Viindoo app
    icon, which invalidates exactly ONE of the 13 assertions in
    `test_mail.tests.test_mail_push.TestWebPushNotification.test_notify_by_push_channel`
    (`test_mail_push.py:135`, the guest-sender icon).

    That expectation is an inline local built at `test_mail_push.py:130-134` inside a
    loop and a `subTest` - there is no builder, helper or class attribute to patch, so
    the expectation itself is unreachable. Rather than neuter the whole method (which
    would silently drop the other 12 assertions - channel-type routing, notification
    counts, title composition, body/res_id/model, device endpoint and mute-until
    behaviour) or copy its body (which would drift from core), we restore the
    PRECONDITION instead: with our override bypassed, core's test exercises core's own
    code and all 13 assertions run unchanged.

    Our de-brand stays protected by `tests/test_web_push_icon_debrand.py`.
    """
    def test_notify_by_push_channel(self, *args, **kwargs):
        with patch.object(
            ViinBrandMailThread,
            '_notify_by_web_push_prepare_payload',
            _core_web_push_payload,
        ):
            return test_method_original(self, *args, **kwargs)
    return test_notify_by_push_channel


def _restore_core_bot_branding_fixture(setup_class_original):
    """Build a `setUpClass` that re-applies core's OdooBot naming on `base.partner_root`.

    `data/res_partner_data.xml` de-brands `base.partner_root` to ViindooBot. A number
    of core suites assert the stock Odoo naming on that very record - e.g.
    `test_discuss_full.tests.test_performance` (`test_performance.py:400,406`),
    `test_mail.tests.test_performance`, `im_livechat.tests.test_get_discuss_channel`,
    `im_livechat.tests.test_chatbot_internals` and
    `test_mail_full.tests.test_mail_bot`. Since this module is `auto_install`, those
    suites see the de-branded record and would fail on the literal `OdooBot` /
    `odoobot@example.com`.

    All of those suites derive from `mail.tests.common.MailCommon`, so restoring the
    fixture once here covers every one of them. The write happens inside the test
    class transaction and is rolled back on teardown, so it never reaches committed
    data - unlike the previous implementation, which performed this same write from
    `post_init_hook`, i.e. on the production install path.

    `mail.tests.discuss.test_ui.TestUi` (its `test_05_can_create_channel_tour`
    tour renders the Discuss sidebar and reads the bot's live `name`) is
    wrapped SEPARATELY with this same builder rather than being covered by the
    MailCommon fixture above: it derives from `base.tests.common.
    HttpCaseWithUserDemo`, a plain `HttpCase` mixin used by ~30 unrelated core
    suites across `website`, `sale`, `im_livechat`, `digest`, etc. that have no
    stake in the bot's naming - wrapping `HttpCaseWithUserDemo` itself would
    restore core's naming for all of them too, far beyond what this fixture
    needs to cover. Targeting `TestUi` alone keeps the blast radius to the one
    class that actually needs it.
    """
    def setUpClass(cls):
        setup_class_original(cls)
        partner_root = cls.env.ref('base.partner_root', raise_if_not_found=False)
        if partner_root:
            # sudo: test fixture restoring a core-owned record inside the test
            # transaction; rolled back with the class teardown.
            partner_root.sudo().write({'name': 'OdooBot', 'email': 'odoobot@example.com'})
    return classmethod(setUpClass)


def post_load():
    if not tools.config.get('test_enable', False):
        return
    MailCommon.setUpClass = _restore_core_bot_branding_fixture(MailCommon.setUpClass.__func__)
    # mail.tests.discuss.test_ui.TestUi derives from HttpCaseWithUserDemo (NOT MailCommon), so the
    # MailCommon fixture above misses it too - same reason as TestSyncGoogle below. Its
    # test_05_can_create_channel_tour tour renders the Discuss sidebar and asserts the literal
    # "OdooBot" text; wrapped narrowly on TestUi itself (not on HttpCaseWithUserDemo, which ~30
    # unrelated core suites also derive from - see the docstring above) to keep the fixture's blast
    # radius to exactly the one suite that needs it.
    CoreDiscussTestUi.setUpClass = _restore_core_bot_branding_fixture(CoreDiscussTestUi.setUpClass.__func__)
    # google_calendar's sync suites derive from HttpCase (NOT MailCommon), so the MailCommon fixture
    # above misses them. They hardcode the stock bot address odoobot@example.com in ~14 expected
    # google-API organizer/attendee payloads (test_sync_odoo2google.py); the event organizer is
    # env.user = base.partner_root, which this module de-brands to viindoobot@example.viindoo.com,
    # so every payload mismatches. Restore core's bot identity for their base class too - same
    # rollback-safe, test-only fixture; the committed de-brand (asserted by test_partner_root_debrand)
    # is untouched.
    if TestSyncGoogle:
        TestSyncGoogle.setUpClass = _restore_core_bot_branding_fixture(TestSyncGoogle.setUpClass.__func__)
    if TestWebPushNotification:
        TestWebPushNotification.test_notify_by_push_channel = _without_web_push_debrand(
            TestWebPushNotification.test_notify_by_push_channel
        )


def post_init_hook(env):
    # OBS-1 debrand: normalize any company still holding mail's untouched core default
    # ('#875A7B', legacy Odoo aubergine) for the outgoing-notification button color to
    # Viindoo's brand secondary colour (owner decision D1: '#7f4282'), so pre-existing
    # companies (upgrade path) get debranded too - not just companies created after this
    # module is installed. A company whose value already differs from the stock default
    # (an explicit customer choice) is left untouched.
    env['res.company'].sudo().search([('email_secondary_color', '=', '#875A7B')]).write({
        'email_secondary_color': '#7f4282',
    })
