from odoo.tests.common import HttpCase, TransactionCase, tagged

from odoo.addons.mail.tests import common as mail_common
from odoo.addons.viin_brand_mail import _restore_core_bot_branding_fixture

STOCK_BOT = ('OdooBot', 'odoobot@example.com')
STOCK_MAIL_ICON = '/mail/static/description/icon.png'
# The Viindoo icon of a module is the image of the same name under the apps folder of viin_brand,
# only while viin_brand_mail ships no static/description/icon.png: that one would be returned first.
VIINDOO_MAIL_ICON = '/viin_brand/static/img/apps/mail.png'


@tagged('post_install', '-at_install')
class TestCoreBotFixtureHelper(TransactionCase):
    """The setUpClass wrapper restores the stock bot in the transaction of the test class."""

    def _suite_class(self, *bases, **attributes):
        """Build a stand-in for a core suite, on the transaction of this test."""
        return type('Suite', bases, dict(attributes, env=self.env))

    def _recording_setup(self, calls):
        return classmethod(lambda cls: calls.append(cls))

    def test_the_core_bot_fixture_is_restored_in_the_test_transaction(self):
        partner_root = self.env.ref('base.partner_root')
        self.assertNotEqual(partner_root.email, STOCK_BOT[1], 'Viindoo brands the bot')
        calls = []
        owner = self._suite_class(setUpClass=self._recording_setup(calls))

        with self.env.cr.savepoint():
            _restore_core_bot_branding_fixture(owner).__func__(owner)
            partner_root.invalidate_recordset()

            self.assertEqual(calls, [owner], 'the core setUpClass still runs first')
            self.assertEqual((partner_root.name, partner_root.email), STOCK_BOT)

    def test_a_suite_with_another_base_between_the_owner_and_the_end_of_the_chain_keeps_that_base(self):
        # MailCase and HttpCase together: HttpCase.setUpClass sits after MailCase in the chain
        partner_root = self.env.ref('base.partner_root')
        calls = []
        owner = self._suite_class()
        sibling = self._suite_class(setUpClass=self._recording_setup(calls))
        suite = self._suite_class(owner, sibling)

        with self.env.cr.savepoint():
            _restore_core_bot_branding_fixture(owner).__func__(suite)
            partner_root.invalidate_recordset()

            self.assertEqual(calls, [suite], 'the next setUpClass of the suite chain runs')
            self.assertEqual((partner_root.name, partner_root.email), STOCK_BOT)


@tagged('post_install', '-at_install')
class TestMailCaseSeesTheStockBot(mail_common.MailCase):
    """A suite built on ``MailCase`` finds the stock bot, whatever order the modules were loaded in.

    The realignment is installed by the ``post_load`` of ``viin_brand_mail``. A module imported
    server wide before the server loads ``viin_brand_mail`` would keep that hook from running, and
    this suite, which is built like the core ones, would then see ViindooBot.
    """

    def test_the_bot_of_a_mail_case_suite_is_the_stock_one(self):
        partner_root = self.env.ref('base.partner_root')

        self.assertEqual((partner_root.name, partner_root.email), STOCK_BOT)


@tagged('post_install', '-at_install')
class TestMailCommonExpectsTheViindooModuleIcon(mail_common.MailCommon):
    """A suite built on ``MailCommon`` expects the Viindoo icon of a module in a Store payload."""

    def test_the_expected_module_icon_of_a_thread_is_the_viindoo_one(self):
        data, = self._filter_threads_fields({'model': 'mail.message', 'module_icon': STOCK_MAIL_ICON})

        self.assertEqual(data['module_icon'], VIINDOO_MAIL_ICON)


@tagged('post_install', '-at_install')
class TestMailCommonWithHttpCaseSeesTheStockBot(mail_common.MailCommon, HttpCase):
    """A suite built like ``ChatbotCase`` (``MailCommon`` and ``HttpCase``) still gets both setups."""

    def test_both_setups_of_the_suite_run_and_the_bot_is_the_stock_one(self):
        self.assertEqual((self.partner_root.name, self.partner_root.email), STOCK_BOT)
