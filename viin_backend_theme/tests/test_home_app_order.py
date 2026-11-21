# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, new_test_user, tagged
from odoo.exceptions import AccessError


@tagged("post_install", "-at_install")
class TestViinHomeAppOrderPref(TransactionCase):
    """res.users.viin_home_app_order holds a user's home-menu app order as comma-separated app
    root-menu xmlids. A user reads and writes only their OWN order, never another user's."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = new_test_user(cls.env, login="viin_order_a", groups="base.group_user")
        cls.user_b = new_test_user(cls.env, login="viin_order_b", groups="base.group_user")

    def test_field_shape_and_default(self):
        """The order is a Char defaulting to empty (False)."""
        field = self.env["res.users"]._fields.get("viin_home_app_order")
        self.assertIsNotNone(
            field,
            "res.users.viin_home_app_order was not added by viin_backend_theme.",
        )
        self.assertEqual(
            field.type, "char", "viin_home_app_order must be a Char field."
        )
        self.assertFalse(
            self.user_a.viin_home_app_order,
            "viin_home_app_order must default to empty (use the default app sequence).",
        )

    def test_user_sets_own_order_without_admin(self):
        """A non-admin internal user writes their OWN order - no admin rights."""
        self.user_a.with_user(self.user_a).write(
            {"viin_home_app_order": "mail.menu_root_discuss,base.menu_administration"}
        )
        self.assertEqual(
            self.user_a.viin_home_app_order,
            "mail.menu_root_discuss,base.menu_administration",
        )

    def test_user_can_read_own_order(self):
        """A non-admin user can READ their own order - the home menu's onWillStart read."""
        self.user_a.with_user(self.user_a).write({"viin_home_app_order": "base.menu_administration"})
        records = self.user_a.with_user(self.user_a).read(["viin_home_app_order"])
        self.assertEqual(records[0]["viin_home_app_order"], "base.menu_administration")

    def test_user_cannot_write_another_users_order(self):
        """Writing ANOTHER user's order must raise AccessError - own scope only, not a broad grant."""
        with self.assertRaises(AccessError):
            self.user_b.with_user(self.user_a).write(
                {"viin_home_app_order": "base.menu_administration"}
            )
