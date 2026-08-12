# web.layout de-brand robustness + head-render guards (ODOO-AI-ETHOS #8).
#
# ITEM A - RED-carrier (test-first). Core web ships a self-test, web.WebSuite.test_check_suite
# (web/tests/test_js.py), which - because it runs outside a request context - OVERWRITES web.layout
# with a minimal STRIPPED PROXY arch that has NO <title> and a bare <link/> (no type attribute),
# then recombines web.layout with every inheriting view. Any view of ours that de-brands by
# targeting one of those omitted nodes:
#     <xpath expr="//title" position="attributes">
#     <xpath expr="//link[@type='image/x-icon']" position="attributes">
# cannot be located in that proxy, so the recombine raises
# ValidationError("Element '...' cannot be located in parent view") - which breaks core's suite on
# any DB with this module installed.
#
# WebLayoutFragileLocatorTest guards that invariant as a deterministic REGISTRY/SOURCE scan: NO
# view inside web.layout's inheritance tree - whichever module owns it - may carry either fragile
# locator. The scan is deliberately NOT scoped to viin_brand_web: core's suite breaks on the
# combined tree, so a SIBLING branding module re-introducing one of these locators breaks it just
# as hard, and a viin_brand_web-only filter could never see that. Offenders are reported with
# their owning module so the failure stays actionable. RED before the fix
# (views/webclient_template.xml's web_layout template carried both),
# GREEN after the de-brand is re-homed onto the render vars (<t t-set="title"/>, <t t-set="x_icon"/>)
# set inside web.layout's CALLERS, which survive the stripped arch.
#
# DO NOT "restore" this into a live write+recombine of web.layout. That mechanism is DEFECTIVE:
# ir.ui.view.write -> _check_xml -> _get_combined_arch ALSO cold-combines core's SIBLING primary
# views (e.g. web.frontend_layout) against the stripped proxy, so the write itself raises from a
# core-internal path before any assertion of ours is reached - RED both BEFORE and AFTER our fix,
# for a reason that has nothing to do with this module.
#
# ITEM A - invariant guards (regression, GREEN today by design). DebrandHeadRenderTest protects
# that the re-homing loses NO branding: the backend and login pages must keep the Viindoo <title>,
# and the favicon must stay the Viindoo asset. These pass on current code (the fragile web.layout
# extension already brands both surfaces); they are tripwires for the fix - in particular the LOGIN
# page renders via web.frontend_layout -> web.layout and does NOT pass through web.webclient_bootstrap,
# so a fix that re-homes the title only into the backend bootstrap would regress the login title
# back to core's 'Odoo'. (The login "Powered by Viindoo" promotion is already covered by
# tests/test_debrand_render.py and is deliberately NOT re-asserted here.)
#
# The two LOGIN guards are scoped to the no-website path THIS cluster owns: when `website` is
# co-installed (possibly transitively) it takes over /web/login rendering - its own page title +
# configurable favicon - so the login de-brand for the website case belongs to viin_brand_website,
# which is not yet upgraded to 19.0 (installable=False) and is DEFERRED by product-owner decision.
# The two login tests therefore skip when `website` is installed (see
# DebrandHeadRenderTest._skip_login_if_website_installed) so a co-installed `website` cannot raise a
# FALSE red; the backend title/favicon guard runs unconditionally and keeps that coverage.
import re

from odoo.tests.common import HttpCase, TransactionCase, tagged

# The Viindoo-branded favicon href that web.layout's shortcut-icon link must resolve to once the
# module is installed - NOT core's /web/static/img/favicon.ico. Grounded from
# views/webclient_template.xml (the module's own de-brand target).
VIINDOO_FAVICON_HREF = "/viin_brand/static/img/favicon.ico"
CORE_FAVICON_HREF = "/web/static/img/favicon.ico"
# Brand wordmark the branded <title> must carry, and the Odoo wordmark it must never fall back to.
# Note "Viindoo" does not contain the substring "Odoo", so the de-brand check is unambiguous.
VIINDOO_BRAND_NAME = "Viindoo"
ODOO_BRAND_NAME = "Odoo"

# The two locators core's stripped web.layout proxy omits (no <title>; the <link/> carries no type
# attribute). A view of ours inside web.layout's inheritance tree that targets either one cannot be
# combined against that proxy, which is exactly what breaks core's web.WebSuite.test_check_suite.
_FRAGILE_LOCATORS = (
    "//title",
    "//link[@type='image/x-icon']",
)

# Extract the text of the first <title> element from a server-rendered HTML page.
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
# Match a single <link ...> element (self-closing or not) so its attributes can be inspected.
_LINK_RE = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
# The shortcut-icon rel marker and an href value inside one <link> element.
_SHORTCUT_ICON_RE = re.compile(r'rel\s*=\s*["\']shortcut icon["\']', re.IGNORECASE)
_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


@tagged("post_install", "-at_install")
class WebLayoutFragileLocatorTest(TransactionCase):
    """RED-carrier: NO installed view may extend web.layout through locators core's proxy omits."""

    def _views_in_web_layout_tree(self):
        """Return every ir.ui.view sitting anywhere BELOW web.layout in the inheritance tree.

        Walks DOWN from web.layout (one search per depth level) rather than up from a candidate
        set, so the scan covers every installed module - core, this cluster and any third party -
        without enumerating the whole ir.ui.view table.

        `active_test=False` on purpose: an inactive view is not combined today, but it is a latent
        offender the moment someone re-activates it, and catching it now costs nothing."""
        View = self.env["ir.ui.view"].with_context(active_test=False)
        web_layout = self.env.ref("web.layout")
        tree = View.browse()
        frontier = web_layout
        while frontier:
            # Subtracting what is already known also makes the walk cycle-proof.
            frontier = View.search([("inherit_id", "in", frontier.ids)]) - tree - web_layout
            tree |= frontier
        return tree

    def _owner_labels(self, views):
        """Map view id -> 'module.xml_id', so an offender always names the module that owns it."""
        labels = {}
        data = self.env["ir.model.data"].search([
            ("model", "=", "ir.ui.view"),
            ("res_id", "in", views.ids),
        ])
        for entry in data:
            labels[entry.res_id] = "%s.%s" % (entry.module, entry.name)
        for view in views:
            # A view with no ir.model.data row is a UI/studio customisation - it breaks core's
            # suite just the same, so report it with whatever identity it has.
            labels.setdefault(view.id, "<no xml id> (view id=%s, name=%r)" % (view.id, view.name))
        return labels

    def test_no_installed_view_adds_a_fragile_web_layout_locator(self):
        """No view in web.layout's tree may target //title or the typed favicon link.

        Core's web.WebSuite.test_check_suite swaps web.layout for a stripped proxy (no <title>, bare
        <link/> with no type attribute) and recombines the whole inheritance tree. A view targeting
        either omitted node makes that core suite raise ValidationError on any DB where that view is
        installed. The de-brand must instead set the `title` / `x_icon` render vars in web.layout's
        CALLERS (web.webclient_bootstrap, web.login_layout), which survive the stripped arch - and the
        rendered result stays guarded by DebrandHeadRenderTest below.

        Scanned cluster-wide (no module filter) because the breakage is a property of the COMBINED
        tree: a sibling branding module re-introducing either locator breaks core's suite exactly as
        hard as this module would, and a self-scoped scan is blind to it. Views that carry these
        locators against a template OUTSIDE web.layout's tree are correctly NOT flagged - e.g.
        viin_brand_mail's discuss_public_channel_template extension, whose target is a standalone
        primary template with its own DOCTYPE (asserted below so the widening cannot silently
        over-reach)."""
        views = self._views_in_web_layout_tree()
        self.assertTrue(
            views,
            "web.layout has no inheriting view at all - the tree walk found nothing to scan, so "
            "this guard would pass vacuously.",
        )

        # Over-reach guard: a template that is NOT in web.layout's tree must stay out of scope,
        # even though it legitimately uses both locators. Skipped when mail is not installed -
        # this module does not depend on it.
        discuss_public = self.env.ref(
            "mail.discuss_public_channel_template", raise_if_not_found=False
        )
        if discuss_public:
            self.assertNotIn(
                discuss_public.id, views.ids,
                "mail.discuss_public_channel_template is a standalone primary template (it ships "
                "its own DOCTYPE), not part of web.layout's tree. It must never enter this scan, "
                "otherwise viin_brand_mail's legitimate //title / favicon extension of it would be "
                "reported as an offender.",
            )

        labels = self._owner_labels(views)
        offenders = []
        for view in views:
            arch = view.arch_db or ""
            for locator in _FRAGILE_LOCATORS:
                if locator in arch:
                    offenders.append("%s -> %s" % (labels[view.id], locator))
        self.assertFalse(
            offenders,
            "These installed views extend web.layout through a locator core's stripped test proxy "
            "omits, which breaks web.WebSuite.test_check_suite: %s. Re-home the de-brand onto the "
            "title/x_icon render vars set in web.layout's callers instead of rewriting //title and "
            "//link[@type='image/x-icon']." % ", ".join(offenders),
        )


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
