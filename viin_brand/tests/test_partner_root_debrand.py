from odoo.tests.common import TransactionCase, tagged
from odoo.tools.convert import convert_file


@tagged("post_install", "-at_install")
class TestPartnerRootDebrand(TransactionCase):
    """The built-in bot partner carries the Viindoo address even when `mail` is not installed."""

    def setUp(self):
        super().setUp()
        # The data file must keep a customer's edit by its own markup, whatever the
        # noupdate flag of the core external id of the partner is on a given database.
        self.env["ir.model.data"].search(
            [("module", "=", "base"), ("name", "=", "partner_root")]
        ).noupdate = False
        self.env.flush_all()

    def _load_partner_data(self, mode):
        convert_file(self.env, "viin_brand", "data/res_partner_data.xml", None, mode)
        self.env.invalidate_all()

    def test_partner_root_email_is_viindoo_branded(self):
        self.assertEqual(
            self.env.ref("base.partner_root").email,
            "viindoobot@example.viindoo.com",
            "base.partner_root must not keep the Odoo example.com bot address",
        )

    def test_install_sets_the_viindoo_email(self):
        partner_root = self.env.ref("base.partner_root")
        partner_root.email = "odoobot@example.com"
        self._load_partner_data("init")
        self.assertEqual(partner_root.email, "viindoobot@example.viindoo.com")

    def test_module_update_keeps_the_customer_email(self):
        partner_root = self.env.ref("base.partner_root")
        partner_root.email = "bot@customer.example"
        self._load_partner_data("update")
        self.assertEqual(
            partner_root.email,
            "bot@customer.example",
            "a customer's edit of the bot address must survive -u viin_brand",
        )
