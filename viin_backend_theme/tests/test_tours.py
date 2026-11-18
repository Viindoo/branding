from requests import Response

from odoo.tests import HttpCase, tagged
from odoo.addons.base.tests.common import HttpCaseWithUserDemo


class _WebTourCapabilityGuard:
    def setUp(self):
        super().setUp()
        if "tour_enabled" not in self.env["res.users"]._fields:
            self.skipTest("web_tour is not installed")


@tagged("post_install", "-at_install")
class TestViinThemeTours(_WebTourCapabilityGuard, HttpCase):
    """Appearance (dark persist+reload, density persistence) and the flat home menu."""

    def test_dark_toggle_persists_to_pref_and_reloads(self):
        """Choosing Dark persists to the user preference and reloads to serve the dark bundle.

        Dark is a recompiled server bundle (web.assets_web_dark), which cannot swap without a
        reload. The tour asserts the reload and the server-stamped ``data-bs-theme=dark`` after it;
        this test adds the server-side outcome: the choice landed in ``res.users.viin_color_scheme``.
        """
        admin = self.env.ref("base.user_admin")
        admin.viin_color_scheme = "light"

        self.start_tour("/odoo", "viin_dark_toggle_tour", login="admin")

        admin.invalidate_recordset(["viin_color_scheme"])
        self.assertEqual(
            admin.viin_color_scheme,
            "dark",
            "toggling Dark in the appearance systray must persist to res.users.viin_color_scheme.",
        )

        # A fresh /odoo load (new browser session) is still stamped dark from the stored preference.
        self.start_tour("/odoo", "viin_dark_persist_tour", login="admin")

    def test_density_compact_persists_across_reload(self):
        """Choosing Compact stamps data-viin-density=compact and it survives an in-page reload.

        Density lives in a cookie only (``viin_density``, no server field), and a second tour would
        start a fresh browser without that cookie, so persistence is proven inside one tour.
        """
        self.start_tour("/odoo", "viin_density_tour", login="admin")

    def test_home_menu_fuzzy_search_then_keyboard_launches_app(self):
        """The flat home menu filters by fuzzy search and launches the highlighted app via the keyboard."""
        self.start_tour("/odoo", "viin_home_menu_tour", login="admin")

    def test_home_menu_typeahead_focuses_search_on_first_keystroke(self):
        """Typing a printable character on the boot-landing home menu must reach the search box
        without the user clicking it first - the first keystroke must never be swallowed."""
        self.start_tour("/odoo", "viin_home_typeahead_tour", login="admin")


@tagged("post_install", "-at_install")
class TestViinAppearanceMarkerCount(_WebTourCapabilityGuard, HttpCase):
    """The active row in the Appearance systray renders exactly one selected-marker."""

    def test_active_option_shows_exactly_one_marker_in_light_scheme(self):
        admin = self.env.ref("base.user_admin")
        admin.viin_color_scheme = "light"
        self.start_tour("/odoo", "viin_appearance_marker_count_light_tour", login="admin")

    def test_active_option_shows_exactly_one_marker_in_dark_scheme(self):
        admin = self.env.ref("base.user_admin")
        admin.viin_color_scheme = "light"
        self.start_tour("/odoo", "viin_appearance_marker_count_dark_tour", login="admin")


@tagged("post_install", "-at_install")
class TestViinThemeA11yTour(_WebTourCapabilityGuard, HttpCase):
    """Keyboard accessibility of the theme shell (the skip link stays reachable and working)."""

    def test_skip_link_is_keyboard_reachable_from_prefocused_search(self):
        """A skip-to-content link stays present, keyboard-reachable and functional (WCAG 2.4.1).

        The home menu pre-focuses its search input on mount, so the skip link is not the first Tab
        stop. It still exists in the DOM, Shift+Tab from the search input reaches it, and activating
        it moves focus into the main content region.
        """
        self.start_tour("/odoo", "viin_a11y_skip_link_keyboard_reachable_tour", login="admin")

    def test_home_tiles_are_announced_as_links(self):
        """A home-menu app tile keeps its own `link` role - nothing overrides it.

        An explicit ARIA role replaces an element's implicit one; a `role="listitem"` on an anchor
        tile would announce a list item where the user can follow a link and drop the tile out of
        links navigation.
        """
        self.start_tour("/odoo", "viin_a11y_home_tile_semantics_tour", login="admin")


@tagged("post_install", "-at_install")
class TestViinAppsMenuHome(_WebTourCapabilityGuard, HttpCase):
    """The navbar apps icon is the sole app switcher: it opens the flat home menu, with no rail and
    no bottom-nav."""

    def test_apps_menu_button_opens_flat_home_menu_and_no_old_chrome(self):
        """The apps-menu button stays visible and enabled (the trigger every core app-switch tour
        clicks first) and opens the one theme home menu whose tiles carry the
        ``.o_app[data-menu-xmlid]`` selector; neither the desktop rail nor the mobile bottom-nav
        renders.

        Clicking the apps icon while the home menu is the only controller on the stack is a no-op
        (nothing to go back to), which is the state every core app-switch tour starts from.
        """
        self.start_tour("/odoo", "viin_apps_menu_home_tour", login="admin")

    def test_apps_icon_toggles_back_to_the_previous_view(self):
        """The apps icon toggles: a second click returns to the view the user came from, without
        leaving the page.

        The apps button renders the home menu as a non-navigating overlay above the untouched
        controller, so the previous view is still mounted underneath.
        """
        self.start_tour("/odoo", "viin_apps_menu_toggle_tour", login="admin")

    def test_home_menu_overlay_does_not_block_the_view_underneath(self):
        """The home menu is an overlay, not a blocker: the view underneath stays reachable.

        Like core's apps dropdown, it has no backdrop and an interaction outside the panel dismisses
        it instead of being swallowed, which core tours depend on. The tour opens the panel over
        Settings, clicks the Settings control panel underneath it, and asserts the panel went away
        while the view stayed.
        """
        self.start_tour("/odoo", "viin_apps_menu_overlay_dismiss_tour", login="admin")


@tagged("post_install", "-at_install")
class TestViinHomeReorder(_WebTourCapabilityGuard, HttpCase):
    """A drag reorders two home-menu tiles and the new order persists across a reload."""

    def test_home_tiles_reorder_by_drag_and_persist_across_reload(self):
        """Press-dragging one app tile onto another reorders the grid, and the new order survives a
        full page reload (the reloaded grid rebuilds from the server-stored order).

        The tour asserts the client-side reorder and the persistence across reload; this test adds
        the server-side outcome: the drop wrote the order into ``res.users.viin_home_app_order``.
        """
        admin = self.env.ref("base.user_admin")
        admin.viin_home_app_order = False

        self.start_tour("/odoo", "viin_home_reorder_persist_tour", login="admin")

        admin.invalidate_recordset(["viin_home_app_order"])
        self.assertTrue(
            admin.viin_home_app_order,
            "dragging a home-menu tile must persist the new order to "
            "res.users.viin_home_app_order (it is still empty).",
        )
        self.assertIn(
            ".",
            admin.viin_home_app_order,
            "the stored home app order %r does not look like a comma-separated list of app "
            "root-menu xmlids." % admin.viin_home_app_order,
        )


@tagged("post_install", "-at_install")
class TestViinClickbotHomeMenu(_WebTourCapabilityGuard, HttpCaseWithUserDemo):
    """Core's clickbot walks apps via the theme home menu, not the dropdown."""

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        # Stub the odoofin dashboard request the Accounting app fires during the crawl, so a real
        # external call cannot hang the walk's RPC-settle.
        if "proxy/v2/get_dashboard_institutions" in r.url:
            response = Response()
            response.status_code = 200
            response.json = list
            return response
        return super()._request_handler(s, r, **kw)

    def test_clickbot_walks_all_apps_via_theme_home_menu(self):
        """The core clickbot (light mode) opens EVERY app through the flat home menu and finishes
        with the success signal.

        The theme replaces the navbar dropdown with a home-menu button, so the clickbot clicks
        ``.o_navbar_apps_menu button``, enumerates and clicks the
        ``.o_viin_home_menu .o_app[data-menu-xmlid]`` tiles, settles on pending RPCs and the OWL
        scheduler, and asserts no ``.o_error_dialog`` per app.
        """
        self.user_demo.tour_enabled = False
        # With website installed and the demo user not a designer, landing on the website dashboard
        # redirects to ``/`` and crashes the crawl.
        group_website_designer = self.env.ref(
            "website.group_website_designer", raise_if_not_found=False
        )
        if group_website_designer:
            self.env.ref("base.group_user").write(
                {"implied_ids": [(4, group_website_designer.id)]}
            )
        self.browser_js(
            "/odoo",
            "odoo.loader.modules.get('@web/webclient/clickbot/clickbot_loader')"
            ".startClickEverywhere(undefined, true);",
            "odoo.isReady === true",
            login="demo",
            timeout=240,
            success_signal="clickbot test succeeded",
        )


@tagged("post_install", "-at_install")
class TestViinDiscussOnboarding(_WebTourCapabilityGuard, HttpCase):
    """The Discuss onboarding reaches Discuss from the flat home-menu landing."""

    def test_discuss_onboarding_reaches_discuss_from_themed_landing(self):
        """Core's ``discuss_channel_tour`` runs to completion under the themed ``/odoo`` landing.

        ``/odoo`` lands on the flat home menu, not Discuss, so the tour's first step
        (``.o-mail-DiscussSearch-inputContainer``) needs a prepended step that clicks the home-menu
        Discuss tile (``.o_viin_home_menu .o_app[data-menu-xmlid='mail.menu_root_discuss']``).
        """
        self.start_tour("/odoo", "discuss_channel_tour", login="admin")
