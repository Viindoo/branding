# web.layout de-brand: rendered <title> and favicon guards (ODOO-AI-ETHOS #8).
#
# viin_brand_web de-brands web.layout's <title> and shortcut-icon <link> by setting the `title` /
# `x_icon` QWeb variables in web.layout's CALLERS - web.webclient_bootstrap (backend) and
# web.login_layout (login) - never by editing web.layout's own <title>/<link> nodes directly.
# DebrandHeadRenderTest below asserts the OBSERVABLE result: the backend and login pages render the
# Viindoo <title> and the Viindoo favicon, never core's fallback.
#
# The login surface needs its own guard because it renders through a DIFFERENT caller
# (web.frontend_layout -> web.layout) that does not pass through web.webclient_bootstrap - a title
# set only on the backend bootstrap would leave the login page on core's 'Odoo' fallback. (The
# login "Powered by Viindoo" promotion is covered separately by tests/test_debrand_render.py and is
# not re-asserted here.)
#
# The two LOGIN guards are scoped to the no-website path this cluster owns: when `website` is
# co-installed (possibly transitively) it takes over /web/login rendering with its own page title
# and configurable favicon, superseding this cluster's render vars. That case belongs to
# viin_brand_website, which is not yet upgraded to 19.0 (installable=False) and is DEFERRED by
# product-owner decision. The two login tests skip when `website` is installed (see
# DebrandHeadRenderTest._skip_login_if_website_installed) so a co-installed `website` cannot raise a
# FALSE red; the backend title/favicon guard runs unconditionally and keeps that coverage.
import re

from odoo.tests.common import HttpCase, tagged

# The Viindoo-branded favicon href that web.layout's shortcut-icon link must resolve to once the
# module is installed - NOT core's /web/static/img/favicon.ico. Grounded from
# views/webclient_template.xml (the module's own de-brand target).
VIINDOO_FAVICON_HREF = "/viin_brand/static/img/favicon.ico"
CORE_FAVICON_HREF = "/web/static/img/favicon.ico"
# Brand wordmark the branded <title> must carry, and the Odoo wordmark it must never fall back to.
# Note "Viindoo" does not contain the substring "Odoo", so the de-brand check is unambiguous.
VIINDOO_BRAND_NAME = "Viindoo"
ODOO_BRAND_NAME = "Odoo"

# Extract the text of the first <title> element from a server-rendered HTML page.
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
# Match a single <link ...> element (self-closing or not) so its attributes can be inspected.
_LINK_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
# The shortcut-icon rel marker and an href value inside one <link> element.
_SHORTCUT_ICON_RE = re.compile(r'rel\s*=\s*["\']shortcut icon["\']', re.IGNORECASE)
_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


@tagged("post_install", "-at_install")
class DebrandHeadRenderTest(HttpCase):
    """Invariant guards: the re-homed de-brand must keep the Viindoo <title> and favicon on both surfaces."""

    def _html_title(self, html):
        """Return the stripped text of the first <title> element, or None when absent."""
        match = _TITLE_RE.search(html)
        return match.group(1).strip() if match else None

    def _favicon_href(self, html):
        """Return the href of the shortcut-icon <link>, or None when absent."""
        for link in _LINK_RE.findall(html):
            if _SHORTCUT_ICON_RE.search(link):
                href = _HREF_RE.search(link)
                return href.group(1) if href else None
        return None

    def _skip_login_if_website_installed(self):
        """Skip the /web/login de-brand guards when `website` is co-installed - NOT hidden breakage.

        When `website` is installed it takes over /web/login rendering: its login_layout
        (web.website.login_layout, priority 20) swaps web.frontend_layout for website.layout, which
        recomputes the page <title> from the site name (e.g. 'Login | My Website') and serves the
        website-configured favicon - overriding this cluster's `title` / `x_icon` render vars at
        render time. De-branding the login page for the website case is OWNED by viin_brand_website,
        which is not yet upgraded to 19.0 (installable=False) and is DEFERRED by product-owner
        decision - this cluster deliberately does not pull `website` into its scope. So these two
        tests are honest for the scope this cluster actually owns (the no-website path) and must not
        emit a false red merely because `website` happens to be co-installed transitively.

        Coverage is not lost under `website`: the no-website assertions below still verify
        title=='Viindoo' and the exact Viindoo favicon, and test_backend_page_title_is_viindoo (the
        /odoo surface, which `website` does not take over) still guards the title/x_icon render-var
        de-brand unconditionally.

        Idiom mirrors odoo/addons/account/tests/test_account_journal_dashboard.py:14-16 (skip when a
        named module IS installed, via ir.module.module search + .state == 'installed')."""
        if self.env["ir.module.module"].search([("name", "=", "website")]).state == "installed":
            self.skipTest(
                "website is installed: it supersedes the web.frontend_layout -> web.layout login "
                "path this cluster de-brands (its own page title + configurable favicon). The "
                "website login de-brand is owned by viin_brand_website, which is not yet upgraded to "
                "19.0 (installable=False) and is DEFERRED - see _skip_login_if_website_installed."
            )

    def test_backend_page_title_is_viindoo(self):
        """The backend web client page must render the Viindoo <title>, never core's 'Odoo'.

        Core web.layout renders <title t-esc="title or 'Odoo'"/> and web.webclient_bootstrap sets no
        title, so the branded title must come from viin_brand_web. Regression guard for the
        re-homing: the backend surface must keep 'Viindoo'."""
        self.authenticate("admin", "admin")
        response = self.url_open("/odoo")
        self.assertEqual(
            response.status_code, 200,
            "backend web client page (/odoo) must render for an authenticated admin",
        )
        title = self._html_title(response.text)
        self.assertIsNotNone(title, "backend page must render a <title> element")
        self.assertIn(
            VIINDOO_BRAND_NAME, title,
            "backend page <title> must be de-branded to Viindoo (got %r)" % title,
        )
        self.assertNotIn(
            ODOO_BRAND_NAME, title,
            "backend page <title> must not fall back to the Odoo wordmark (got %r)" % title,
        )

    def test_login_page_title_is_viindoo(self):
        """The login page must render the Viindoo <title>, never core's 'Odoo'.

        The login page renders via web.frontend_layout -> web.layout and does NOT pass through
        web.webclient_bootstrap. This is the re-homing tripwire: a fix that brands the title only in
        the backend bootstrap regresses the login <title> back to core's 'Odoo'. Guards it stays
        'Viindoo'.

        Scoped to the no-website path this cluster owns: skipped when `website` is co-installed
        (that login path is owned by the deferred viin_brand_website) - see
        _skip_login_if_website_installed."""
        self._skip_login_if_website_installed()
        response = self.url_open("/web/login")
        self.assertEqual(
            response.status_code, 200,
            "login page must render (no ParseError from the de-brand xpath targets)",
        )
        title = self._html_title(response.text)
        self.assertIsNotNone(title, "login page must render a <title> element")
        self.assertIn(
            VIINDOO_BRAND_NAME, title,
            "login page <title> must be de-branded to Viindoo (got %r)" % title,
        )
        self.assertNotIn(
            ODOO_BRAND_NAME, title,
            "login page <title> must not fall back to the Odoo wordmark (got %r)" % title,
        )

    def test_login_page_favicon_is_viindoo_asset(self):
        """The login page favicon must resolve to the Viindoo asset, never core's favicon.

        Core web.layout renders the shortcut-icon link href as `x_icon or '/web/static/img/favicon.ico'`;
        viin_brand_web must brand it to /viin_brand/static/img/favicon.ico. Regression guard for
        the re-homing (the login page bypasses web.webclient_bootstrap).

        Scoped to the no-website path this cluster owns: skipped when `website` is co-installed
        (that login favicon is served by the deferred viin_brand_website) - see
        _skip_login_if_website_installed."""
        self._skip_login_if_website_installed()
        response = self.url_open("/web/login")
        self.assertEqual(response.status_code, 200, "login page must render")
        favicon = self._favicon_href(response.text)
        self.assertIsNotNone(
            favicon, "login page must render a shortcut-icon <link> with an href"
        )
        self.assertEqual(
            favicon, VIINDOO_FAVICON_HREF,
            "login page favicon must be the Viindoo asset %s, not %s (got %r)"
            % (VIINDOO_FAVICON_HREF, CORE_FAVICON_HREF, favicon),
        )
