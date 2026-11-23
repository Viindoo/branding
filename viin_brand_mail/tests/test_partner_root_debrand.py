import re

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.binary import BinaryBytes
from odoo.tools.convert import convert_file

BRAND_TERM = re.compile(r"odoo", re.IGNORECASE)


@tagged("post_install", "-at_install")
class TestPartnerRootDebrand(TransactionCase):
    """The built-in bot partner, the author of every system-generated message, is ViindooBot.

    The case derives from ``TransactionCase`` and not from ``mail.tests.common.MailCommon``,
    because the realignment of ``MailCommon`` restores the OdooBot naming and would hide the
    shipped value.
    """

    def setUp(self):
        super().setUp()
        # The data file must keep a customer's edit by its own markup, whatever the
        # noupdate flag of the core external id of the partner is on a given database.
        self.env["ir.model.data"].search(
            [("module", "=", "base"), ("name", "=", "partner_root")]
        ).noupdate = False
        self.env.flush_all()

    def _load_partner_data(self, mode):
        convert_file(self.env, "viin_brand_mail", "data/res_partner_data.xml", None, mode)
        self.env.invalidate_all()

    def test_partner_root_is_viindoo_branded(self):
        partner_root = self.env.ref("base.partner_root")
        self.assertEqual(partner_root.name, "ViindooBot")
        self.assertTrue(partner_root.image_1920, "ViindooBot must carry the Viindoo bot picture")

    def test_install_sets_the_viindoo_name_and_image(self):
        partner_root = self.env.ref("base.partner_root")
        partner_root.write({"name": "System", "image_1920": False})
        self._load_partner_data("init")
        self.assertEqual(partner_root.name, "ViindooBot")
        self.assertTrue(partner_root.image_1920)

    def _tracking_messages(self):
        return self.env["mail.message"].search([
            ("model", "=", "res.partner"),
            ("res_id", "=", self.env.ref("base.partner_root").id),
            ("message_type", "=", "tracking"),
        ])

    def _seed_the_state_core_leaves(self):
        """The bot as core's own install leaves it: renamed and flushed, its history line written."""
        partner_root = self.env.ref("base.partner_root")
        partner_root.write({"name": "OdooBot", "email": "odoobot@example.com"})
        self.env.flush_all()
        self.env.cr.precommit.run()
        self.assertTrue(
            self._tracking_messages().filtered(lambda message: BRAND_TERM.search(message.body or "")),
            "the seed must leave the history line core writes, or the test proves nothing",
        )

    def test_installed_database_has_no_history_line_naming_odoo_on_the_bot(self):
        self.assertFalse(
            self._tracking_messages().filtered(lambda message: BRAND_TERM.search(message.body or "")),
            "the history of the bot of an installed database must not name Odoo",
        )

    def test_install_leaves_no_history_line_for_the_branding_of_the_bot(self):
        """Neither the rename of this module nor the address change of viin_brand is a change a user made."""
        self._seed_the_state_core_leaves()
        known = self._tracking_messages()
        convert_file(self.env, "viin_brand", "data/res_partner_data.xml", None, "init")
        self._load_partner_data("init")
        self.env.flush_all()
        self.env.cr.precommit.run()
        partner_root = self.env.ref("base.partner_root")
        self.assertEqual(partner_root.name, "ViindooBot")
        self.assertEqual(partner_root.email, "viindoobot@example.viindoo.com")
        self.assertFalse(
            self._tracking_messages() - known,
            "the branding of the bot must not show in its history",
        )
        self.assertFalse(
            self._tracking_messages().filtered(lambda message: BRAND_TERM.search(message.body or "")),
            "the history of the bot must not name Odoo, whoever wrote the line",
        )

    def test_install_keeps_a_history_line_a_user_made(self):
        admin = self.env.ref("base.user_admin")
        partner_root = self.env.ref("base.partner_root").with_user(admin).with_context(active_test=False)
        partner_root.write({"name": "Odoo Fan Bot"})
        self.env.flush_all()
        self.env.cr.precommit.run()
        user_lines = self._tracking_messages().filtered(lambda message: message.create_uid == admin)
        self.assertTrue(user_lines, "a rename made by a user is tracked")
        self._load_partner_data("init")
        self.env.flush_all()
        self.env.cr.precommit.run()
        self.assertEqual(
            self._tracking_messages() & user_lines,
            user_lines,
            "the history a user made is not cleaned by the install of the branding",
        )

    def test_rename_made_after_the_install_is_tracked(self):
        self._load_partner_data("init")
        self.env.flush_all()
        self.env.cr.precommit.run()
        known = self._tracking_messages()
        admin = self.env.ref("base.user_admin")
        self.env.ref("base.partner_root").with_user(admin).with_context(active_test=False).write(
            {"name": "Customer Bot"}
        )
        self.env.flush_all()
        self.env.cr.precommit.run()
        self.assertTrue(self._tracking_messages() - known, "a rename a customer makes shows in the history")

    def test_module_update_keeps_the_customer_name_and_image(self):
        partner_root = self.env.ref("base.partner_root")
        customer_image = b"<svg xmlns='http://www.w3.org/2000/svg' width='8' height='8'/>"
        partner_root.write({"name": "Customer Bot", "image_1920": BinaryBytes(customer_image)})
        self._load_partner_data("update")
        self.assertEqual(
            partner_root.name,
            "Customer Bot",
            "a customer's rename of the bot must survive -u viin_brand_mail",
        )
        self.assertEqual(
            partner_root.image_1920.content,
            customer_image,
            "a customer's bot picture must survive -u viin_brand_mail",
        )
