# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# Locks the behavioral contract of the frontend header's apps button: for an authenticated
# internal user, `o_frontend_to_backend_apps_btn` (core `website.layout`, extended by this
# module's own `layout` inherit at views/website_templates.xml) must navigate straight into the
# backend, never open the Bootstrap dropdown core ships by default.
#
# Stock Odoo 19.0 core (website/views/website_templates.xml, template `website.layout`,
# verified against the local checkout) renders, unconditionally, the
# `o_frontend_to_backend_apps_btn` anchor and its sibling `o_frontend_to_backend_apps_menu` div,
# inside a `groups="base.group_user"` block:
#     <a href="#" title="Go to your Odoo Apps" class="o_frontend_to_backend_apps_btn ..."
#        data-bs-toggle="dropdown"/>
#     <div class="dropdown-menu o_frontend_to_backend_apps_menu" role="menu">
#         <a role="menuitem" class="dropdown-item" t-out="menu['name']" t-as="menu"
#            t-foreach="env['ir.ui.menu'].with_context(force_action=True).load_menus_root()['children']"
#            t-attf-href="/odoo/action-#{...}"/>
#     </div>
# i.e. the anchor defers navigation to a dropdown click handler (`href="#"`, `data-bs-toggle`),
# and the sibling menu calls `load_menus_root()` on every render regardless of whether it is ever
# opened.
#
# This module's fix only customizes the anchor: making it a direct `/odoo` link (asserted
# below) and stripping `data-bs-toggle` so Bootstrap never wires a dropdown to it. The sibling
# `o_frontend_to_backend_apps_menu` div, its `load_menus_root()`-driven `<a>` entries, and the
# per-render ORM call that produces them are left fully UNTOUCHED - core's own default markup and
# behavior, verbatim.
#
# An earlier revision of this module instead emptied that div via an xpath. That broke core's
# own `website.tests.test_ui.TestUi.test_29_website_backend_menus_redirect` (tour
# `website_backend_menus_redirect`), which does
# `this.anchor.querySelector(".o_frontend_to_backend_apps_menu").classList.add("show")` and then
# clicks an `<a>` inside it - an emptied or absent div breaks that core test the moment this
# module installs (auto_install: True on website, always present). The xpath was removed for
# that reason; restoring core's div/content/ORM call verbatim keeps this module compatible with
# core's own test suite. A reader tempted to re-add such an xpath (to save the per-render
# `load_menus_root()` query) would reintroduce exactly that breakage - see
# `test_apps_dropdown_never_opens_and_is_left_as_core_renders_it` below, which guards against it.
# The "user never sees the dropdown" guarantee this module still owns is structural, not
# content-based: the anchor carries no `data-bs-toggle`, so Bootstrap never initializes a
# dropdown on it and nothing ever adds `.show` to the div - it can safely keep rendering core's
# own content because nothing ever displays it.
#
# The `title` attribute this module's own `layout` template xpath sets on the apps-button anchor
# ("Go to your Viindoo Apps") is deliberately NOT asserted here: its wording is translated,
# user-facing text, and this suite never pins tests to translated/display wording (that class of
# regression is caught by the i18n pipeline's own diff-review, not by this test). The only
# content-free proxy available - "the anchor still carries a non-empty `title`" - can never fail
# even if the customization were dropped entirely, because core's own default title also renders
# non-empty; a toothless assertion that can never fail is not authored here.
#
# The button's click-triggered spinner feedback and its back/forward-cache pageshow reset are
# owned by a real JS module (static/src/js/frontend_to_backend_apps_btn.js), not by anything this
# file can observe: `HttpCase` renders the page but never executes a click or dispatches a
# `pageshow` event. The pure logic and the DOM wiring are protected by the Hoot suite at
# static/tests/js/frontend_to_backend_apps_btn.test.js; whether that wiring actually reaches the
# button AS THE REAL PAGE RENDERS IT - the button is a #wrapwrap SIBLING, never a descendant, so it
# is unreachable through the public.interactions scanner Hoot's own fixture helper used to
# fabricate around it - is proven only by driving a real page, which is what
# FrontendToBackendAppsButtonWiringTourTest below does.
import re

from odoo.tests.common import HttpCase, tagged

# Matches the opening <a> tag carrying the apps-button class, attributes in any order.
_APPS_BTN_TAG_RE = re.compile(
    r'<a\b[^>]*class="[^"]*\bo_frontend_to_backend_apps_btn\b[^"]*"[^>]*>', re.IGNORECASE
)
# Matches the o_frontend_to_backend_apps_menu div's full opening tag through its closing tag,
# capturing the inner HTML. The div has no nested divs in core's own markup (only a single <a>
# child), so a non-greedy match to the next </div> is safe here.
_APPS_MENU_DIV_RE = re.compile(
    r'<div\b(?=[^>]*\bclass="[^"]*\bdropdown-menu\b)'
    r'(?=[^>]*\bclass="[^"]*\bo_frontend_to_backend_apps_menu\b)[^>]*>(.*?)</div>',
    re.IGNORECASE | re.DOTALL,
)
_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)


@tagged("post_install", "-at_install")
class FrontendToBackendAppsButtonNavigatesTest(HttpCase):
    """The frontend header's apps button must jump straight into the backend for an internal user."""

    def _apps_btn_tag(self, html):
        """Return the rendered opening <a> tag for the apps button, or None if absent."""
        match = _APPS_BTN_TAG_RE.search(html)
        return match.group(0) if match else None

    def _apps_menu_div_inner_html(self, html):
        """Return the o_frontend_to_backend_apps_menu div's inner HTML, or None if the div
        itself is absent from the rendered page.
        """
        match = _APPS_MENU_DIV_RE.search(html)
        return match.group(1) if match else None

    def test_apps_button_navigates_directly_to_backend_instead_of_toggling_a_dropdown(self):
        """The apps-button anchor must link straight to /odoo, not defer to a dropdown toggle.

        Business rule: clicking the header's apps icon must take an authenticated internal user
        straight into the backend. Stock core wires the anchor to `data-bs-toggle="dropdown"`
        with an inert `href="#"`, deferring navigation to a dropdown click handler instead of
        linking anywhere - that is exactly what this asserts against.
        """
        self.authenticate("admin", "admin")
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200, "the website homepage must render")

        tag = self._apps_btn_tag(response.text)
        self.assertIsNotNone(
            tag,
            "the homepage must render an anchor carrying the o_frontend_to_backend_apps_btn "
            "class for an authenticated internal user",
        )

        self.assertNotIn(
            "data-bs-toggle",
            tag,
            "the apps-button anchor must not carry data-bs-toggle - that wiring only makes "
            "sense when the anchor opens a dropdown instead of navigating directly; got %r" % tag,
        )

        href_match = _HREF_RE.search(tag)
        href = href_match.group(1) if href_match else None
        self.assertEqual(
            href,
            "/odoo",
            "the apps-button anchor's href must be exactly /odoo so it navigates straight into "
            "the backend; got %r from tag %r" % (href, tag),
        )

    def test_apps_dropdown_never_opens_and_is_left_as_core_renders_it(self):
        """The dropdown must never open for the user, and its menu div renders core's own content.

        Two properties, both protected here:

        (1) The user never sees the dropdown open. The real guarantee is structural, not
        content-based: the apps-button anchor carries no `data-bs-toggle`, so Bootstrap never
        initializes a dropdown on it and nothing ever adds `.show` to the sibling menu div.
        `HttpCase` cannot execute JS, so the resulting computed CSS visibility cannot be
        asserted here directly - only the structural cause that makes it true; the same
        assertion also anchors
        `test_apps_button_navigates_directly_to_backend_instead_of_toggling_a_dropdown`, and is
        repeated here because it is this test's own guarantee too, not borrowed from there.

        (2) The o_frontend_to_backend_apps_menu div must render WITH core's own menu-item
        markup again - not force-emptied. Because (1) already makes the div unreachable to the
        user, nothing requires suppressing its content anymore; a future reader re-adding an
        xpath that empties it (to "optimise away" the per-render `load_menus_root()` query)
        would silently break core's own
        `website.tests.test_ui.TestUi.test_29_website_backend_menus_redirect` tour the moment
        this module installs, which is exactly the regression this test exists to catch.
        """
        self.authenticate("admin", "admin")
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200, "the website homepage must render")

        tag = self._apps_btn_tag(response.text)
        self.assertIsNotNone(
            tag,
            "the homepage must render an anchor carrying the o_frontend_to_backend_apps_btn "
            "class for an authenticated internal user",
        )
        self.assertNotIn(
            "data-bs-toggle",
            tag,
            "the apps-button anchor must not carry data-bs-toggle - without it, Bootstrap "
            "never initializes a dropdown on this anchor and nothing ever adds .show to the "
            "sibling menu div, which is the actual reason the user never sees it open; "
            "got %r" % tag,
        )

        inner_html = self._apps_menu_div_inner_html(response.text)
        self.assertIsNotNone(
            inner_html,
            "the homepage must still render a div carrying both the dropdown-menu and "
            "o_frontend_to_backend_apps_menu classes for an authenticated internal user",
        )
        self.assertTrue(
            "dropdown-item" in inner_html or "menuitem" in inner_html,
            "the o_frontend_to_backend_apps_menu div must render WITH core's own menu-item "
            "markup (a dropdown-item or role=menuitem entry) for an authenticated admin whose "
            "load_menus_root() is not empty on this instance - an empty inner HTML here means "
            "the withdrawn div-emptying xpath has been reintroduced; got inner HTML %r"
            % inner_html,
        )


@tagged("post_install", "-at_install")
class FrontendToBackendAppsButtonWiringTourTest(HttpCase):
    """The apps button's click-feedback JS must actually be reachable on a real website page.

    A Hoot fixture is not the real page: the button is a #wrapwrap SIBLING (never a descendant),
    so any test that fabricates a #wrapwrap around a bare fixture proves nothing about whether the
    real page ever runs this wiring - it did not, for nine passing unit tests, until this tour was
    added. `start_tour` drives the actual homepage in a real browser, with no fabricated ancestor.
    """

    def setUp(self):
        super().setUp()
        if "tour_enabled" not in self.env["res.users"]._fields:
            self.skipTest("web_tour is not installed")

    def test_apps_button_click_wiring_is_live_on_the_real_rendered_page(self):
        self.start_tour(
            "/", "viin_brand_website_frontend_to_backend_apps_btn_wiring", login="admin"
        )
