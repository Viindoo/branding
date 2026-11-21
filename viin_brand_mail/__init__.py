from odoo import tools

from . import models
from . import wizard

if tools.config.get('test_enable', False):
    from unittest.mock import patch

    from odoo.addons.mail.tests.common import MailCommon
    from odoo.addons.mail.tests.discuss.test_ui import TestUi as CoreDiscussTestUi

    from odoo.addons.viin_brand import get_viin_brand_module_icon

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
    """Run ``_notify_by_web_push_prepare_payload`` below this module's override.

    The caller observes the stock behaviour, including the stock ``odoo-icon-192x192.png``
    fallback, while the overrides of other modules are still honoured.
    """
    return super(ViinBrandMailThread, self)._notify_by_web_push_prepare_payload(
        message, msg_vals, force_record_name=force_record_name,
    )


def _without_web_push_debrand(test_method_original):
    """Run a core test with the web-push de-brand of this module disabled.

    The de-brand invalidates exactly one assertion of
    ``TestWebPushNotification.test_notify_by_push_channel`` (the icon for a guest sender), and
    that expectation is an inline local of the test. Restoring the precondition keeps its other
    assertions running unchanged. The de-brand itself is protected by
    ``tests/test_web_push_icon_debrand.py``.
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
    """Build a ``setUpClass`` that restores the OdooBot name and email on ``base.partner_root``.

    Core suites such as those of ``test_discuss_full``, ``test_mail``, ``im_livechat``,
    ``test_mail_full`` and ``google_calendar`` hardcode the stock bot naming. The write happens in
    the transaction of the test class and is rolled back on teardown, so no committed data changes.

    :param setup_class_original: the ``setUpClass`` function to wrap
    :return: the wrapping ``classmethod``
    """
    def setUpClass(cls):
        setup_class_original(cls)
        partner_root = cls.env.ref('base.partner_root', raise_if_not_found=False)
        if partner_root:
            # sudo: restores a record of another module inside the test transaction
            partner_root.sudo().write({'name': 'OdooBot', 'email': 'odoobot@example.com'})
    return classmethod(setUpClass)


def _patch_mailcommon_module_icon_expectation():
    """Realign the core mail Store tests to the Viindoo module icon.

    Several core suites hardcode the stock icon of a module in the expected ``module_icon`` of
    their Store payloads, all built through ``MailCommon._filter_threads_fields``. The expected
    icon is resolved with the same function the Store uses, so the tests assert the Viindoo icon.
    """
    _filter_threads_fields_orig = MailCommon._filter_threads_fields

    def _filter_threads_fields(self, /, *threads_data):
        data_list = _filter_threads_fields_orig(self, *threads_data)
        for data in data_list:
            model = data.get('model')
            if 'module_icon' in data and model and model in self.env:
                data['module_icon'] = get_viin_brand_module_icon(self.env[model]._original_module)
        return data_list

    MailCommon._filter_threads_fields = _filter_threads_fields


def post_load():
    if not tools.config.get('test_enable', False):
        return
    _patch_mailcommon_module_icon_expectation()
    MailCommon.setUpClass = _restore_core_bot_branding_fixture(MailCommon.setUpClass.__func__)
    # TestUi derives from HttpCaseWithUserDemo, which ~30 unrelated suites share, so it is
    # wrapped itself and not its base class.
    CoreDiscussTestUi.setUpClass = _restore_core_bot_branding_fixture(CoreDiscussTestUi.setUpClass.__func__)
    # The sync tests of google_calendar derive from HttpCase and run right after google_calendar
    # loads, so the realignment has to exist before that. Within a load phase modules load by graph
    # depth, then by name: this holds while viin_brand_mail sits at a smaller depth than
    # google_calendar, which tests/test_realign_load_order.py asserts.
    if TestSyncGoogle:
        TestSyncGoogle.setUpClass = _restore_core_bot_branding_fixture(TestSyncGoogle.setUpClass.__func__)
    if TestWebPushNotification:
        TestWebPushNotification.test_notify_by_push_channel = _without_web_push_debrand(
            TestWebPushNotification.test_notify_by_push_channel
        )


def post_init_hook(env):
    # Companies that still hold the stock outgoing-notification button colour of mail get the
    # Viindoo secondary colour; a colour the customer chose is left untouched.
    env['res.company'].sudo().search([('email_secondary_color', '=', '#875A7B')]).write({
        'email_secondary_color': '#7f4282',
    })
