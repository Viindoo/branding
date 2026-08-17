# Durable full-stack tour runners (ODOO-AI-ETHOS #8: protect BEHAVIOR, not code).
#
# These HttpCase tests drive the theme's appearance + mobile + a11y behaviors end-to-end in a real
# browser via the JS tours under static/tests/tours/. Each tour asserts observable UI state; these
# runners add the server-side observable outcomes the browser cannot see (the persisted preference)
# and the mobile viewport. cr.commit() is FORBIDDEN (HttpCase isolation is savepoint rollback -
# test_base_classes 19.0); start_tour drives a fresh /odoo load per call within one browser session,
# so cookies set by one tour are visible to the next.
from requests import Response

from odoo.tests import HttpCase, tagged
from odoo.addons.base.tests.common import HttpCaseWithUserDemo


@tagged("post_install", "-at_install")
class TestViinThemeTours(HttpCase):
    """Appearance (dark persist+reload, density persistence) and the flat home menu."""

    def test_dark_toggle_persists_to_pref_and_reloads(self):
        """T-1: choosing Dark PERSISTS to the user preference and RELOADS to serve the dark bundle.

        Dark is now a recompiled server bundle (web.assets_web_dark), which cannot swap without a
        reload, so the toggle persists the choice + effective cookie and reloads (no instant in-place
        flip). The tour asserts the reload happens (expectUnloadPage on the click) and that the server
        boot-stamps data-bs-theme=dark AFTER the reload; here we add the server-side observable: the
        choice landed in res.users.viin_color_scheme."""
        admin = self.env.ref("base.user_admin")
        # Clean baseline so the assertion below cannot pass on stale state from a reused DB.
        admin.viin_color_scheme = "light"

        # Tour: open systray -> click Dark (reloads) -> after reload <html data-bs-theme=dark>.
        self.start_tour("/odoo", "viin_dark_toggle_tour", login="admin")

        # Persistence to the per-user preference is an observable ORM outcome (not an internal).
        admin.invalidate_recordset(["viin_color_scheme"])
        self.assertEqual(
            admin.viin_color_scheme,
            "dark",
            "toggling Dark in the appearance systray must persist to res.users.viin_color_scheme.",
        )

        # A fresh /odoo load (new browser session) must still be boot-stamped dark server-side from
        # the stored preference - proving the choice survives beyond the reloading session.
        self.start_tour("/odoo", "viin_dark_persist_tour", login="admin")

    def test_density_compact_persists_across_reload(self):
        """Choosing Compact stamps data-viin-density=compact and it survives an in-page reload.

        Density is cookie-SSOT (viin_density, no server field), so persistence is proven WITHIN one
        tour: the tour reloads via location.reload() (same session keeps the cookie jar) and re-asserts
        the attribute. A second start_tour would spawn a fresh Chrome that never carries the
        viin_density cookie, so a two-tour design could not observe persistence."""
        self.start_tour("/odoo", "viin_density_tour", login="admin")

    def test_home_menu_fuzzy_search_then_keyboard_launches_app(self):
        """The flat home menu filters by fuzzy search and launches the highlighted app via the keyboard."""
        self.start_tour("/odoo", "viin_home_menu_tour", login="admin")


@tagged("post_install", "-at_install")
class TestViinThemeA11yTour(HttpCase):
    """T-4: keyboard accessibility of the theme shell (the skip link is the first focusable element)."""

    def test_skip_link_is_first_focusable(self):
        """A skip-to-content link is the first focusable element on the page - WCAG 2.4.1 bypass
        blocks. (The rail roving-tabindex arm was removed with the vertical rail in PR #658 item 1; the
        flat home menu is now the sole app switcher, so there is no rail to make one Tab stop.)"""
        self.start_tour("/odoo", "viin_a11y_skip_link_tour", login="admin")

    def test_home_tiles_are_announced_as_links(self):
        """A home-menu app tile keeps its own `link` role - nothing overrides it.

        An explicit ARIA role REPLACES an element's implicit one. The tiles carried
        `role="listitem"`, so a screen reader announced a list item where the user could actually
        follow a link, and the tiles dropped out of links navigation. Harmless-looking while the
        tiles were buttons; a real defect once they became anchors, because the role being
        suppressed became an accurate and useful one.

        RED before the 2026-08-17 fix: `a.o_app[href]:not([role])` matched nothing."""
        self.start_tour("/odoo", "viin_a11y_home_tile_semantics_tour", login="admin")


@tagged("post_install", "-at_install")
class TestViinAppsMenuHome(HttpCase):
    """PR #658 item 1: the navbar apps icon is the SOLE app switcher - no rail, no bottom-nav, and it
    opens the flat home menu. Preserves the B1 assertion the deleted viin_rail_appnav_tour owned."""

    def test_apps_menu_button_opens_flat_home_menu_and_no_old_chrome(self):
        """The apps-menu button stays visible + enabled (the trigger every core app-switch tour clicks
        first) and opens the ONE theme home menu whose tiles carry the tour-compatible
        .o_app[data-menu-xmlid] selector; and neither the removed desktop rail nor the removed mobile
        bottom-nav renders. The earlier d-none hide broke core tours (runbot 223591); this repurpose
        keeps them green.

        Also covers the toggle's BOOT edge case: clicking the apps icon while the home menu is the
        only controller on the stack must be a no-op (nothing to go back to), which is precisely the
        state every core app-switch tour starts from."""
        self.start_tour("/odoo", "viin_apps_menu_home_tour", login="admin")

    def test_apps_icon_toggles_back_to_the_previous_view(self):
        """Owner request 2026-08-03: the apps icon TOGGLES - a second click returns to the view the
        user came from ("bấm app icon lần nữa thì nó lại về lại view cũ"). Owner decision D3,
        2026-08-17: it does so WITHOUT leaving the page.

        RED before the toggle: openHomeMenu() unconditionally re-ran doAction("viin_home_menu"), so
        the second click pushed a SECOND home menu and the original view never came back.
        RED again before D3, on the step this tour gained: the first click ran a full-page doAction,
        which UNMOUNTED the Settings view, so "the Settings view is still mounted underneath" could
        not match. GREEN after: the apps button renders the same home menu as a non-navigating
        overlay above the untouched controller."""
        self.start_tour("/odoo", "viin_apps_menu_toggle_tour", login="admin")

    def test_home_menu_overlay_does_not_block_the_view_underneath(self):
        """D3: the home menu is an overlay, not a blocker - the view underneath stays reachable.

        This is the property core's apps DROPDOWN has and that 57 core tours depend on: no backdrop,
        and an interaction outside the panel dismisses it instead of being swallowed. The tour opens
        the panel over Settings, clicks the Settings control panel UNDERNEATH it, and asserts the
        panel went away while the view stayed.

        RED before D3: the first apps click destroyed the Settings view, so its control panel did not
        exist to be clicked and the tour stalled."""
        self.start_tour("/odoo", "viin_apps_menu_overlay_dismiss_tour", login="admin")


@tagged("post_install", "-at_install")
class TestViinHomeReorder(HttpCase):
    """PR #658 item 7: a drag reorders two home-menu tiles AND the new order persists across a reload."""

    def test_home_tiles_reorder_by_drag_and_persist_across_reload(self):
        """Press-dragging one app tile onto another reorders the grid, and the new order survives a full
        page reload (the reloaded grid rebuilds from the SERVER-stored order). The tour asserts the
        client-side reorder + cross-reload persistence; here we add the server-side observable: the drop
        wrote the new order into res.users.viin_home_app_order. RED before item 7 (no drag, empty field);
        GREEN after."""
        admin = self.env.ref("base.user_admin")
        # Clean baseline so the assertion below cannot pass on stale state from a reused DB.
        admin.viin_home_app_order = False

        self.start_tour("/odoo", "viin_home_reorder_persist_tour", login="admin")

        # The drop persisted the reordered app xmlids to the per-user field (an observable ORM outcome).
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
class TestViinClickbotHomeMenu(HttpCaseWithUserDemo):
    """R1 (PR #658): core's clickbot walks apps via the theme home menu, not the removed dropdown."""

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        # Stub the odoofin dashboard request the Accounting app fires during the crawl (exactly as
        # core web:TestMenusDemoLight does) so a real external call cannot hang the walk's RPC-settle.
        if "proxy/v2/get_dashboard_institutions" in r.url:
            response = Response()
            response.status_code = 200
            response.json = list
            return response
        return super()._request_handler(s, r, **kw)

    def test_clickbot_walks_all_apps_via_theme_home_menu(self):
        """The core clickbot (light mode) opens EVERY app through the flat home menu and finishes with
        the success signal.

        RED before the theme wrapper: the clickbot community path clicks
        ``.o_navbar_apps_menu .dropdown-toggle`` - which the theme replaced with the home-menu button -
        and throws ``No element "apps menu toggle button" found``. GREEN after: the wrapper clicks
        ``.o_navbar_apps_menu button``, enumerates/clicks ``.o_viin_home_menu .o_app[data-menu-xmlid]``
        tiles, settles on pending RPCs + the OWL scheduler, and asserts no ``.o_error_dialog`` per app.
        Mirrors core web:TestMenusDemoLight.test_01_click_apps_menus_as_demo on the themed build."""
        if "tour_enabled" in self.env["res.users"]._fields:
            self.user_demo.tour_enabled = False
        # If website is present but the demo user is not a designer, landing on the website dashboard
        # redirects to ``/`` and crashes the crawl (same guard as core TestMenusDemoLight).
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
class TestViinDiscussOnboarding(HttpCase):
    """R2 (PR #658): the Discuss onboarding reaches Discuss from the flat home-menu landing."""

    def test_discuss_onboarding_reaches_discuss_from_themed_landing(self):
        """Core's ``discuss_channel_tour`` runs to completion under the themed ``/odoo`` landing.

        RED before the theme patch: ``/odoo`` lands on the flat home menu (not Discuss), so the tour's
        CE-active first step ``.o-mail-DiscussSearch-inputContainer`` never appears and the tour fails.
        GREEN after: the prepended step clicks the home-menu Discuss tile
        (``.o_viin_home_menu .o_app[data-menu-xmlid='mail.menu_root_discuss']``), opening Discuss before
        that step. This is core mail TestUi.test_01_mail_tour, guarded here at the theme level so a
        future landing change cannot silently re-break the onboarding."""
        self.start_tour("/odoo", "discuss_channel_tour", login="admin")
