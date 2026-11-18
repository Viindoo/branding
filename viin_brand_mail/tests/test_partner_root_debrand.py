import base64

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.convert import convert_file


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

    def test_module_update_keeps_the_customer_name_and_image(self):
        partner_root = self.env.ref("base.partner_root")
        customer_image = base64.b64encode(
            b"<svg xmlns='http://www.w3.org/2000/svg' width='8' height='8'/>"
        )
        partner_root.write({"name": "Customer Bot", "image_1920": customer_image})
        self._load_partner_data("update")
        self.assertEqual(
            partner_root.name,
            "Customer Bot",
            "a customer's rename of the bot must survive -u viin_brand_mail",
        )
        self.assertEqual(
            partner_root.image_1920,
            customer_image,
            "a customer's bot picture must survive -u viin_brand_mail",
        )
