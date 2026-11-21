from odoo.tests.common import TransactionCase, tagged
from odoo.tools import convert_file


@tagged("post_install", "-at_install")
class TestAuthOauthDebrand(TransactionCase):
    """The provider record of the Odoo.com accounts is removed.

    Core ships it enabled and names it after the Odoo.com accounts; it would otherwise stay listed
    in Settings > Users & Companies > OAuth Providers and offered as a login button.
    """

    def test_odoo_accounts_provider_is_removed(self):
        self.assertFalse(
            self.env.ref("auth_oauth.provider_openerp", raise_if_not_found=False),
            "the 'Odoo.com Accounts' provider record must not exist",
        )

    def test_no_provider_is_named_after_odoo(self):
        providers = self.env["auth.oauth.provider"].with_context(active_test=False).search([])
        for provider in providers:
            self.assertNotIn("odoo", (provider.name or "").lower())
            self.assertNotIn("odoo.com", (provider.auth_endpoint or "").lower())
            self.assertNotIn("odoo.com", (provider.validation_endpoint or "").lower())

    def _load_data(self):
        convert_file(self.env, "viin_brand_auth_oauth", "data/auth_oauth_data.xml", None, mode="update")

    def test_loading_the_data_again_logs_no_warning(self):
        with self.assertNoLogs("odoo.tools.convert", "WARNING"):
            self._load_data()

    def test_a_provider_core_recreates_is_removed_and_its_users_lose_the_reference(self):
        provider = self.env["auth.oauth.provider"].create({
            "name": "Core provider",
            "body": "Log in with the provider",
            "client_id": "client",
            "auth_endpoint": "https://provider.example.com/auth",
            "validation_endpoint": "https://provider.example.com/validate",
        })
        self.env["ir.model.data"].create({
            "module": "auth_oauth", "name": "provider_openerp", "model": "auth.oauth.provider", "res_id": provider.id,
        })
        user = self.env["res.users"].create({
            "name": "Oauth user", "login": "oauth_user_login", "oauth_provider_id": provider.id, "oauth_uid": "uid1",
        })
        provider_id = provider.id

        with self.assertNoLogs("odoo.tools.convert", "WARNING"):
            self._load_data()

        self.assertFalse(self.env["auth.oauth.provider"].browse(provider_id).exists())
        self.assertFalse(user.oauth_provider_id)
