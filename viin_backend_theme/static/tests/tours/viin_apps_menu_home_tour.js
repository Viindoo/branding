/** @odoo-module **/

// The navbar apps icon is the sole app switcher: no desktop rail, no mobile bottom-nav, and
// clicking the apps icon opens the one flat home menu. Driven by tests/test_tours.py.
//
// Protected behaviours (observable DOM state):
//   1. Tour-safe app switcher. Core app-switch tours (every tour built on
//      stepUtils.showAppsMenuItem) first click `.o_navbar_apps_menu button:enabled`, then
//      `a[data-menu-xmlid="<app>"]`. The apps button stays visible and enabled
//      (apps_menu_home.xml) and the home-menu tiles are anchors exposing
//      `a.o_app[data-menu-xmlid][href]`, the element shape core renders. Hiding the button, or
//      rendering the tiles as <button>, breaks those tours, so this tour pins the element shape and
//      not just the class.
//   2. The desktop vertical rail (`.o_viin_rail`) and the mobile bottom nav (`.o_viin_bottom_nav`)
//      render on no viewport.

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("viin_apps_menu_home_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "no desktop vertical rail is rendered",
            trigger: "body:not(:has(.o_viin_rail))",
        },
        {
            content: "no mobile bottom-nav is rendered",
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
                "the ONE flat home menu exposes its app tiles as ANCHORS carrying an href - the " +
                'exact `a[data-menu-xmlid="<app>"]` shape core renders (a DropdownItem with an ' +
                "href becomes an <a>, per its `t-tag` expression in dropdown_item.xml) and " +
                "that core tours click at their second step",
            trigger: ".o_viin_home_menu a.o_app[data-menu-xmlid][href]",
        },
        {
            content:
                "TOGGLE EDGE CASE: on the BOOT landing there is no controller underneath the " +
                "home menu, so the apps icon must be a NO-OP - it may not blank the action " +
                "manager and it may not bounce to a default app. This is also what keeps every " +
                "core app-switch tour green: stepUtils.showAppsMenuItem() clicks this button " +
                "from /odoo (already on the home menu) and its next step still has to resolve " +
                ".o_app[data-menu-xmlid].",
            trigger: ".o_navbar_apps_menu button:enabled",
            run: "click",
        },
        {
            content: "the home menu is still there after the no-op toggle",
            trigger: ".o_viin_home_menu a.o_app[data-menu-xmlid][href]",
        },
    ],
});
