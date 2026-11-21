from odoo.modules import module as odoo_module
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.viin_brand import uninstall_hook


@tagged("post_install", "-at_install")
class TestUninstallHook(TransactionCase):
    """Uninstalling viin_brand on one database must not remove the branding of the other
    databases served by the same process."""

    def test_uninstall_restores_the_database_but_keeps_the_process_branding(self):
        action = self.env.ref("base.open_module_tree")
        self.assertIn("to_buy", action.domain or "", "the Apps action must hide the Enterprise stubs")

        uninstall_hook(self.env)

        self.assertNotIn("to_buy", action.domain or "", "the Apps action domain is restored")
        self.assertEqual(
            odoo_module.get_module_icon("crm"),
            "/viin_brand/static/img/apps/crm.png",
            "module icons stay Viindoo's for the databases that keep viin_brand",
        )
