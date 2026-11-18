# Part of Viindoo. See LICENSE file for full copyright and licensing details.
#
# The apps button of the frontend header (`o_frontend_to_backend_apps_btn` of `website.layout`)
# links straight to /odoo. The sibling `o_frontend_to_backend_apps_menu` div stays as core renders
# it: core's `test_29_website_backend_menus_redirect` tour clicks an entry inside it. The click
# feedback is covered by the Hoot suite and by the wiring tour below, as `HttpCase` cannot click.
import re

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class FrontendToBackendAppsButtonNavigatesTest(HttpCase):
    """The frontend header's apps button must jump straight into the backend for an internal user."""

    def _apps_btn_tag(self, html):
        """Return the rendered opening <a> tag for the apps button, or None if absent."""
        match = re.search(
            r'<a\b[^>]*class="[^"]*\bo_frontend_to_backend_apps_btn\b[^"]*"[^>]*>',
            html,
            re.IGNORECASE,
        )
        return match.group(0) if match else None

    def _apps_menu_div_inner_html(self, html):
        """Return the o_frontend_to_backend_apps_menu div's inner HTML, or None if it is absent.

        The div has no nested div in core's markup, so a non-greedy match to the next ``</div>``
        is safe.
        """
        match = re.search(
            r'<div\b(?=[^>]*\bclass="[^"]*\bdropdown-menu\b)'
            r'(?=[^>]*\bclass="[^"]*\bo_frontend_to_backend_apps_menu\b)[^>]*>(.*?)</div>',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        return match.group(1) if match else None

    def test_apps_button_navigates_directly_to_backend_instead_of_toggling_a_dropdown(self):
        """The apps icon takes an internal user straight into the backend.

        Core wires the anchor to `data-bs-toggle="dropdown"` with an inert `href="#"`.
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
            "the apps-button anchor must not carry data-bs-toggle; got %r" % tag,
        )

        href_match = re.search(r'href\s*=\s*["\']([^"\']*)["\']', tag, re.IGNORECASE)
        href = href_match.group(1) if href_match else None
        self.assertEqual(
            href,
            "/odoo",
            "the apps-button anchor's href must be exactly /odoo so it navigates straight into "
            "the backend; got %r from tag %r" % (href, tag),
        )

    def test_apps_dropdown_never_opens_and_is_left_as_core_renders_it(self):
        """The dropdown never opens, and its menu div renders core's own content.

        The anchor carries no `data-bs-toggle`, so Bootstrap never initializes a dropdown on it
        and nothing adds `.show` to the sibling menu div. The div keeps core's menu items: an
        xpath that empties it breaks core's `test_29_website_backend_menus_redirect` tour.
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
            "the apps-button anchor must not carry data-bs-toggle; got %r" % tag,
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
            "load_menus_root() is not empty on this instance; got inner HTML %r"
            % inner_html,
        )


@tagged("post_install", "-at_install")
class FrontendToBackendAppsButtonWiringTourTest(HttpCase):
    """The apps button's click-feedback JS is reachable on a real website page.

    The button is a sibling of #wrapwrap, so a Hoot fixture cannot show that the real page runs
    the wiring; the tour drives the actual homepage in a browser.
    """

    def setUp(self):
        super().setUp()
        if "tour_enabled" not in self.env["res.users"]._fields:
            self.skipTest("web_tour is not installed")

    def test_apps_button_click_wiring_is_live_on_the_real_rendered_page(self):
        self.start_tour(
            "/", "viin_brand_website_frontend_to_backend_apps_btn_wiring", login="admin"
        )
