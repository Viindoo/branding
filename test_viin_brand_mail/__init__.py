import functools
from unittest.mock import patch

from odoo.tools import config

STOCK_PUSH_ICON = '/web/static/img/odoo-icon-192x192.png'
VIINDOO_PUSH_ICON = '/viin_brand/static/img/viindoo-icon-192x192.png'
STOCK_BOT_MENTION = '@OdooBot'
VIINDOO_BOT_MENTION = '@ViindooBot'
STOCK_RECORDING_SENTENCE = 'Your meeting recording is available in Odoo.'


def _restore_stock_bot_after(setup_class_original):
    """Build a ``setUpClass`` that runs ``setup_class_original`` and then restores the OdooBot.

    Only for a class that defines its own ``setUpClass``: the function given is called as it is, the
    chain of the class is not continued. The write on ``base.partner_root`` happens in the
    transaction of the test class and is rolled back on teardown, so no committed data changes. The
    module imports nothing of ``viin_brand_mail``: loaded server wide,
    such an import would put that module in ``sys.modules`` before the server loads it, and its
    ``post_load`` would never run.

    :param setup_class_original: the ``setUpClass`` function to wrap
    :return: the wrapping ``classmethod``
    """
    def setUpClass(cls):
        setup_class_original(cls)
        partner_root = cls.env.ref('base.partner_root', raise_if_not_found=False)
        if partner_root:
            partner_root.sudo().write({  # sudo: restores a core record in the test transaction
                'name': 'OdooBot', 'email': 'odoobot@example.com'})
    return classmethod(setUpClass)


def _realign_core_calendar_sync_tests():
    """Realign the sync tests of ``google_calendar`` to the Viindoo bot.

    The tests expect the organizer of an event to be ``odoobot@example.com``, the email of the
    OdooBot that Viindoo renames. The fixture restores the stock bot inside the test transaction.
    """
    from odoo.addons.google_calendar.tests.test_sync_common import TestSyncGoogle

    TestSyncGoogle.setUpClass = _restore_stock_bot_after(TestSyncGoogle.setUpClass.__func__)


def _expect_viindoo_push_icon(assert_equal):
    """Wrap an ``assertEqual`` so that the stock Odoo push icon, as expected value, becomes Viindoo's.

    Only the expected (second) argument is turned: an actual icon that is still the stock one fails.

    :param assert_equal: the ``assertEqual`` to wrap
    :return: the wrapping function, with the signature of ``assertEqual``
    """
    def assertEqual(first, second, msg=None):
        return assert_equal(first, VIINDOO_PUSH_ICON if second == STOCK_PUSH_ICON else second, msg)
    return assertEqual


def _realign_core_web_push_icon_test():
    """Realign ``test_notify_by_push_channel`` of ``test_mail`` to the Viindoo push icon.

    The test compares the icon of a push notification sent by a guest with the stock Odoo icon,
    while Viindoo shows its own. Only that expected value is turned into the Viindoo icon, so every
    other assertion is unchanged.
    """
    from odoo.addons.test_mail.tests.test_mail_push import TestWebPushNotification

    test_original = TestWebPushNotification.test_notify_by_push_channel

    @functools.wraps(test_original)
    def test_notify_by_push_channel(self, *args, **kwargs):
        with patch.object(self, 'assertEqual', _expect_viindoo_push_icon(self.assertEqual)):
            return test_original(self, *args, **kwargs)

    TestWebPushNotification.test_notify_by_push_channel = test_notify_by_push_channel


def _expect_viindoo_bot_mention(assert_next_message):
    """Wrap an ``assertNextMessage`` so that the stock bot mention, as expected answer, becomes Viindoo's.

    Only the expected fragments (a tuple ``answer``) that are the stock mention are turned: the sender
    and every other fragment are checked as the core test writes them.

    :param assert_next_message: the ``assertNextMessage`` to wrap
    :return: the wrapping function, with the signature of ``assertNextMessage``
    """
    def assertNextMessage(message, answer=None, sender=None):
        if isinstance(answer, tuple):
            answer = tuple(VIINDOO_BOT_MENTION if fragment == STOCK_BOT_MENTION else fragment for fragment in answer)
        return assert_next_message(message, answer=answer, sender=sender)
    return assertNextMessage


def _realign_core_bot_onboarding_test():
    """Realign ``test_onboarding_flow`` of ``test_mail_full`` to the Viindoo bot.

    The first answer of the onboarding must mention the bot by its name, ``@OdooBot`` in core while
    Viindoo names it ``@ViindooBot``. Only that expected fragment is turned, so every other step of the
    flow is checked as it is.
    """
    from odoo.addons.test_mail_full.tests.test_mail_bot import TestOdoobot

    test_original = TestOdoobot.test_onboarding_flow

    @functools.wraps(test_original)
    def test_onboarding_flow(self, *args, **kwargs):
        with patch.object(self, 'assertNextMessage', _expect_viindoo_bot_mention(self.assertNextMessage)):
            return test_original(self, *args, **kwargs)

    TestOdoobot.test_onboarding_flow = test_onboarding_flow


def _expect_viindoo_recording_sentence(assert_mail_mail_w_record):
    """Wrap an ``assertMailMailWRecord`` so that the stock recording sentence, as expected content, names the product.

    Only the expected ``content`` that is the stock sentence is turned: the record, the recipients, the
    status and every other argument are checked as the core test writes them. The product name is read
    when the wrapper is called, from the module that owns it.

    :param assert_mail_mail_w_record: the ``assertMailMailWRecord`` to wrap
    :return: the wrapping function, with the signature of ``assertMailMailWRecord``
    """
    from odoo.addons.viin_brand.tools import PRODUCT_NAME

    def assertMailMailWRecord(*args, content=None, **kwargs):
        if content == STOCK_RECORDING_SENTENCE:
            content = content.replace('Odoo', PRODUCT_NAME)
        return assert_mail_mail_w_record(*args, content=content, **kwargs)
    return assertMailMailWRecord


def _realign_core_call_recording_test():
    """Realign ``test_recording_is_published_after_upload`` of ``cloud_storage`` to the Viindoo sentence.

    The test finds the mail that announces a recording by its sentence, worded with ``Odoo`` in core
    while Viindoo names itself. Only that expected content is turned into the Viindoo sentence, so
    every other assertion is unchanged.
    """
    from odoo.addons.cloud_storage.tests.test_rtc import TestCloudStorageRtc

    test_original = TestCloudStorageRtc.test_recording_is_published_after_upload

    @functools.wraps(test_original)
    def test_recording_is_published_after_upload(self, *args, **kwargs):
        with patch.object(
            self, 'assertMailMailWRecord', _expect_viindoo_recording_sentence(self.assertMailMailWRecord),
        ):
            return test_original(self, *args, **kwargs)

    TestCloudStorageRtc.test_recording_is_published_after_upload = test_recording_is_published_after_upload


def post_load():
    if config.get('test_enable', False):
        _realign_core_calendar_sync_tests()
        _realign_core_web_push_icon_test()
        _realign_core_bot_onboarding_test()
        _realign_core_call_recording_test()
