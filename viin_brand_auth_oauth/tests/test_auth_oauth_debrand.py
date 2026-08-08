# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAuthOauthDebrand(TransactionCase):
    """Core's baseline OAuth provider record must carry no Odoo branding.

    Business rule (BUG S41-OAUTH-1, HIGH; QA acceptance re-adjudication
    ``rb633-accept-20260808-k4x9-readjudication-2.md`` S41): a Viindoo-branded
    instance must show no Odoo wordmark and no live Odoo authentication
    endpoint for the core OAuth provider record - even though that record is
    disabled, an admin can still see it (Settings > Users & Companies > OAuth
    Providers - ``auth_oauth.action_oauth_provider`` lists disabled providers
    too, no domain filter on ``enabled`` per
    ``auth_oauth/views/auth_oauth_views.xml``) and core's
    ``/auth_oauth/oea`` controller route
    (``auth_oauth/controllers/main.py``) resolves this exact xmlid directly,
    unguarded by the ``enabled`` flag.

    Root cause (traced, not yet fixed at authoring time). Core `auth_oauth`
    ships a DATA record (``<data noupdate="1">``, not demo - listed under the
    ``data`` key of auth_oauth's manifest, so it installs in production) with
    xmlid ``auth_oauth.provider_openerp``, model ``auth.oauth.provider``:
    ``name = "Odoo.com Accounts"``,
    ``body = "Sign in with Odoo.com"``,
    ``auth_endpoint = "https://accounts.odoo.com/oauth2/auth"``,
    ``validation_endpoint = "https://accounts.odoo.com/oauth2/tokeninfo"``.
    ``viin_brand_auth_oauth/data/auth_oauth_data.xml`` already overrides this
    record via a ``<function name="write">`` to set ``enabled: False``, but
    never touches ``name`` / ``body`` / ``auth_endpoint`` /
    ``validation_endpoint`` - those four fields still literally read Odoo's
    own wordmark and point at Odoo's own accounts.odoo.com endpoints today.

    RED (current, pre-fix): ``test_provider_no_odoo_wordmark`` and
    ``test_provider_no_live_odoo_endpoint`` fail - the record's ``name``,
    ``body``, ``auth_endpoint`` and ``validation_endpoint`` all still contain
    the literal, case-insensitive substrings "odoo" / "odoo.com" (confirmed
    live via read-only ``search_read`` on db ``rb633_f3``,
    ``auth.oauth.provider`` id 1: ``name="Odoo.com Accounts"``,
    ``body="Sign in with Odoo.com"``,
    ``auth_endpoint="https://accounts.odoo.com/oauth2/auth"``,
    ``validation_endpoint="https://accounts.odoo.com/oauth2/tokeninfo"``).
    ``test_provider_stays_disabled`` already passes today - the existing
    ``enabled: False`` override is kept as a regression guard so a future
    change cannot silently flip the record back on.

    GREEN (post-fix): once the ``<function name="write">`` override in
    ``viin_brand_auth_oauth/data/auth_oauth_data.xml`` is extended to also
    set ``name`` / ``body`` / ``auth_endpoint`` / ``validation_endpoint`` to
    values carrying no Odoo wordmark and no odoo.com endpoint (while keeping
    ``enabled: False``), all three tests below pass.
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
            "disabled - regression guard for the existing "
            "viin_brand_auth_oauth override so a future change cannot "
            "silently re-enable Odoo's own OAuth login button",
        )
