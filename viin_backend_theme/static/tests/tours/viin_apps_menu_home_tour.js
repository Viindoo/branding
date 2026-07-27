/** @odoo-module **/

// PR #658 item 1 - the navbar apps icon is the SOLE app switcher: no desktop rail, no mobile
// bottom-nav, and clicking the apps icon opens the ONE flat home menu. Driven by tests/test_tours.py.
// Preserves the B1 assertion the deleted viin_rail_appnav_tour owned (tour-safe apps-menu repurpose).
//
// BEHAVIOURS PROTECTED (observable DOM state, never internals):
//   1. TOUR-SAFE APP SWITCHER. Core app-switch tours (mass_mailing, im_livechat, and every tour built
//      on stepUtils.showAppsMenuItem) FIRST click `.o_navbar_apps_menu button:enabled`, then click
//      `.o_app[data-menu-xmlid]`. The apps icon is REPURPOSED (apps_menu_home.xml): it stays visible +
//      enabled, but core's inner <Dropdown> second app list is replaced by a plain button that opens
//      the ONE theme home menu (ViinHomeMenu). The home-menu tiles expose `.o_app[data-menu-xmlid]`,
//      so the whole showAppsMenuItem -> `.o_app[data-menu-xmlid]` pattern still resolves. Hiding that
//      button broke core tours historically (runbot 223591); this repurpose keeps them green.
//   2. NEITHER OLD CHROME EXISTS. The desktop vertical rail (`.o_viin_rail`) and the mobile bottom nav
//      (`.o_viin_bottom_nav`) are removed - neither renders on any viewport, so their absence is a
//      lightweight regression guard that item 1's deletion stayed complete.
//
// GROUNDED (OSM 19.0 + core source): the core apps menu is web/static/src/webclient/navbar/navbar.xml
// `web.NavBar.AppsMenu` (div.o_navbar_apps_menu, its trigger button is what stepUtils.showAppsMenuItem
// clicks: `.o_navbar_apps_menu button:enabled`). The home menu root is .o_viin_home_menu and its tiles
// are .o_app[data-menu-xmlid] (home_menu.xml). `:has` / `:not` triggers are the v19 hoot-dom forms.

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("viin_apps_menu_home_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "no desktop vertical rail is rendered (item 1 removed it)",
            trigger: "body:not(:has(.o_viin_rail))",
        },
        {
            content: "no mobile bottom-nav is rendered (item 1 removed it)",
            trigger: "body:not(:has(.o_viin_bottom_nav))",
        },
        {
            content:
                "the navbar apps-menu button stays VISIBLE + enabled - the exact trigger " +
                "stepUtils.showAppsMenuItem() (and every core app-switch tour) clicks first",
            trigger: ".o_navbar_apps_menu button:enabled",
            run: "click",
        },
        {
            content:
                "clicking it opens the ONE flat home menu, whose app tiles expose the SAME " +
                ".o_app[data-menu-xmlid] selector core tours resolve at their second step",
            trigger: ".o_viin_home_menu .o_app[data-menu-xmlid]",
        },
        {
            content:
                "TOGGLE EDGE CASE (2026-08-03): on the BOOT landing there is no controller " +
                "underneath the home menu, so the apps icon must be a NO-OP - it may not blank " +
                "the action manager and it may not bounce to a default app. This is also what " +
                "keeps every core app-switch tour green: stepUtils.showAppsMenuItem() clicks " +
                "this button from /odoo (already on the home menu) and its next step still has " +
                "to resolve .o_app[data-menu-xmlid].",
            trigger: ".o_navbar_apps_menu button:enabled",
            run: "click",
        },
        {
            content: "the home menu is still there after the no-op toggle",
            trigger: ".o_viin_home_menu .o_app[data-menu-xmlid]",
        },
    ],
});
