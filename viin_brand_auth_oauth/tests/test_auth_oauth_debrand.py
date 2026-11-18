# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAuthOauthDebrand(TransactionCase):
    """Core's baseline OAuth provider record carries no Odoo branding.

    The record ``auth_oauth.provider_openerp`` is listed in Settings > Users & Companies >
    OAuth Providers even while disabled, and core's ``/auth_oauth/oea`` route resolves it
    regardless of its ``enabled`` flag. Its name, button text and endpoints therefore name no
    Odoo wordmark and no odoo.com host, and the record stays disabled.
    """

    def test_provider_no_odoo_wordmark(self):
        provider = self.env.ref("auth_oauth.provider_openerp")

        self.assertNotIn(
            "odoo", (provider.name or "").lower(),
            "auth.oauth.provider 'Odoo.com Accounts' record must not carry "
            "the Odoo wordmark in its name - it is admin-visible on Settings "
            "> Users & Companies > OAuth Providers even while disabled "
            "(list view has no domain filter on 'enabled')",
        )
        self.assertNotIn(
            "odoo", (provider.body or "").lower(),
            "auth.oauth.provider 'Odoo.com Accounts' record must not carry "
            "the Odoo wordmark in its login-button body text ('Sign in with "
            "Odoo.com')",
        )

    def test_provider_no_live_odoo_endpoint(self):
        provider = self.env.ref("auth_oauth.provider_openerp")

        self.assertNotIn(
            "odoo.com", (provider.auth_endpoint or "").lower(),
            "auth.oauth.provider 'Odoo.com Accounts' record must not keep a "
            "live accounts.odoo.com auth_endpoint - core's /auth_oauth/oea "
            "controller route resolves this exact xmlid unguarded by the "
            "'enabled' flag, so a live endpoint here is reachable through "
            "more than just the login-page button list",
        )
        self.assertNotIn(
            "odoo.com", (provider.validation_endpoint or "").lower(),
            "auth.oauth.provider 'Odoo.com Accounts' record must not keep a "
            "live accounts.odoo.com validation_endpoint, for the same "
            "unguarded-controller-route reason as auth_endpoint",
        )

    def test_provider_stays_disabled(self):
        provider = self.env.ref("auth_oauth.provider_openerp")

        self.assertFalse(
            provider.enabled,
            "auth.oauth.provider 'Odoo.com Accounts' record must stay "
            "disabled so Odoo's own OAuth login button is never offered",
        )
