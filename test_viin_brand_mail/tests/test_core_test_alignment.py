from odoo.tests.common import TransactionCase, tagged

from odoo.addons.test_viin_brand_mail import (
    STOCK_BOT_MENTION,
    STOCK_PUSH_ICON,
    STOCK_RECORDING_SENTENCE,
    VIINDOO_BOT_MENTION,
    VIINDOO_PUSH_ICON,
    _expect_viindoo_bot_mention,
    _expect_viindoo_push_icon,
    _expect_viindoo_recording_sentence,
    _restore_stock_bot_after,
)


@tagged('post_install', '-at_install')
class TestCoreTestAlignment(TransactionCase):
    """The core tests of ``test_mail``, ``test_mail_full``, ``google_calendar`` and ``cloud_storage`` expect Viindoo.

    The realigned core suites are not run from here: a suite run inside a test would stop the patchers
    of this test. The core suites themselves run with this module installed.
    """

    def test_a_push_icon_expectation_of_odoo_is_realigned_to_viindoo(self):
        expect = _expect_viindoo_push_icon(self.assertEqual)

        expect(VIINDOO_PUSH_ICON, STOCK_PUSH_ICON)

    def test_a_push_with_the_stock_icon_still_fails_the_realigned_expectation(self):
        expect = _expect_viindoo_push_icon(self.assertEqual)

        with self.assertRaises(AssertionError):
            expect(STOCK_PUSH_ICON, STOCK_PUSH_ICON)

    def test_any_other_expectation_is_left_unchanged(self):
        expect = _expect_viindoo_push_icon(self.assertEqual)

        expect('/web/image/res.partner/1/avatar_128', '/web/image/res.partner/1/avatar_128')
        with self.assertRaises(AssertionError):
            expect('/web/image/res.partner/1/avatar_128', '/web/image/res.partner/2/avatar_128')

    def test_the_core_bot_fixture_is_restored_in_the_test_transaction(self):
        partner_root = self.env.ref('base.partner_root')
        self.assertNotEqual(partner_root.email, 'odoobot@example.com', 'Viindoo brands the bot')
        calls = []

        def setup_class_core(cls):
            calls.append(cls)

        with self.env.cr.savepoint():
            _restore_stock_bot_after(setup_class_core).__func__(type(self))
            partner_root.invalidate_recordset()

            self.assertEqual(calls, [type(self)], 'the core setUpClass still runs first')
            self.assertEqual((partner_root.name, partner_root.email), ('OdooBot', 'odoobot@example.com'))

    def test_a_bot_mention_expectation_of_odoo_is_realigned_to_viindoo(self):
        calls = []

        def assert_next_message(message, answer=None, sender=None):
            calls.append((message, answer, sender))
            return 'last message'

        expect = _expect_viindoo_bot_mention(assert_next_message)

        result = expect('message', answer=(STOCK_BOT_MENTION, 'attachment'), sender='bot')

        self.assertEqual(result, 'last message')
        self.assertEqual(calls, [('message', (VIINDOO_BOT_MENTION, 'attachment'), 'bot')])

    def test_the_bot_mention_realignment_is_checked_against_the_message_the_core_test_reads(self):
        message = self.env['mail.message'].create({'body': '<p>Hi, %s</p>' % STOCK_BOT_MENTION})

        def assert_next_message(message, answer=None, sender=None):
            for fragment in answer:
                self.assertIn(fragment, message.body)

        expect = _expect_viindoo_bot_mention(assert_next_message)

        with self.assertRaises(AssertionError):
            expect(message, answer=(STOCK_BOT_MENTION,))
        message.body = '<p>Hi, %s</p>' % VIINDOO_BOT_MENTION
        expect(message, answer=(STOCK_BOT_MENTION,))

    def test_any_other_expected_answer_of_the_bot_is_left_unchanged(self):
        calls = []

        def assert_next_message(message, answer=None, sender=None):
            calls.append(answer)

        expect = _expect_viindoo_bot_mention(assert_next_message)

        for answer in (('attachment',), ['OdooBot'], 'OdooBot', False, None):
            expect('message', answer=answer)

        self.assertEqual(calls, [('attachment',), ['OdooBot'], 'OdooBot', False, None])

    def test_a_recording_sentence_expectation_of_odoo_is_realigned_to_the_product_name(self):
        from odoo.addons.viin_brand.tools import PRODUCT_NAME
        calls = []

        def assert_mail_mail_w_record(*args, **kwargs):
            calls.append((args, kwargs))

        expect = _expect_viindoo_recording_sentence(assert_mail_mail_w_record)

        expect('record', 'recipients', 'outgoing', content=STOCK_RECORDING_SENTENCE)

        (args, kwargs), = calls
        self.assertEqual(args, ('record', 'recipients', 'outgoing'))
        self.assertIn(PRODUCT_NAME, kwargs['content'])
        self.assertNotIn('Odoo', kwargs['content'])

    def test_any_other_expected_content_of_a_mail_is_left_unchanged(self):
        calls = []

        def assert_mail_mail_w_record(*args, **kwargs):
            calls.append(kwargs)

        expect = _expect_viindoo_recording_sentence(assert_mail_mail_w_record)

        for content in ('Your meeting recording is available', None):
            expect('record', content=content)
        expect('record')

        self.assertEqual(calls, [
            {'content': 'Your meeting recording is available'}, {'content': None}, {'content': None},
        ])
