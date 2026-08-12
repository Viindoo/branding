/** @odoo-module **/

// Owner request 2026-08-03: the apps icon must TOGGLE.
// "khi đang ở một view nào đó, bấm vào app icon thì nó về icon dashboard. Tao kỳ vọng bấm app icon
//  lần nữa thì nó lại về lại view cũ."
//
// BEHAVIOUR PROTECTED (observable DOM state only - never an internal):
//   from a real view -> click the apps icon -> the flat home menu is shown
//                    -> click the apps icon AGAIN -> the ORIGINAL view is back.
// The round trip is what matters: asserting only "the home menu closed" would still pass if the
// second click dumped the user on a blank action manager or bounced them to the default app, which
// is exactly the failure mode this guards. So the last step asserts the SAME view marker the tour
// captured before opening the home menu, AND that the home menu is really gone.
//
// RED BEFORE / GREEN AFTER. Before the toggle, NavBar.openHomeMenu() unconditionally re-ran
// doAction("viin_home_menu"), so the second click pushed a SECOND home menu onto the controller
// stack: step "the original view is back" never matched (the home menu was still on screen) and the
// tour failed. GREEN once openHomeMenu() detects it is already on the home menu and restores the
// controller underneath (apps_menu_home.js).
//
// WHY SETTINGS IS THE VIEW. It is the one app guaranteed to exist in a minimal
// viin_brand_web + viin_brand_mail + viin_backend_theme install, and the sibling
// viin_home_menu_tour (static/tests/tours/viin_appearance_tour.js) already launches it the same way,
// so this tour adds no new install-scope assumption. Its form carries the stable core root class
// `.o_base_settings_view` (web/static/src/webclient/settings_form_view/settings_form_view.scss:9,39),
// which is a far stronger "this exact view came back" marker than a generic .o_form_view.
//
// GROUNDED (OSM 19.0 + core source): the apps trigger every core app-switch tour clicks is
// `.o_navbar_apps_menu button:enabled` (stepUtils.showAppsMenuItem); the theme home menu root is
// `.o_viin_home_menu` and its tiles are `.o_app[data-menu-xmlid]` (home_menu.xml). `:has` / `:not`
// triggers are the v19 hoot-dom forms.

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("viin_apps_menu_toggle_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "the flat home menu is the boot landing - launch a real view from it",
            trigger: ".o_viin_home_grid .o_viin_home_app[title='Settings']",
            run: "click",
        },
        {
            content: "the Settings view is open and the home menu is gone",
            trigger: ".o_action_manager .o_form_view.o_base_settings_view",
        },
        {
            content: "guard: the home menu really was replaced (not just overlaid)",
            trigger: "body:not(:has(.o_viin_home_menu))",
        },
        {
            content: "FIRST click on the apps icon - leaves the view for the home menu",
            trigger: ".o_navbar_apps_menu button:enabled",
            run: "click",
        },
        {
            content: "the flat home menu is shown",
            trigger: ".o_viin_home_menu .o_app[data-menu-xmlid]",
        },
        {
            content: "guard: the Settings view is no longer mounted",
            trigger: "body:not(:has(.o_base_settings_view))",
        },
        {
            content: "SECOND click on the same apps icon - this must go BACK, not re-open",
            trigger: ".o_navbar_apps_menu button:enabled",
            run: "click",
        },
        {
            content:
                "THE ASK: the ORIGINAL Settings view is back - the apps icon toggled the home " +
                "menu off and restored the controller the user came from",
            trigger: ".o_action_manager .o_form_view.o_base_settings_view",
        },
        {
            content: "...and the home menu is closed, not merely hidden behind the view",
            trigger: "body:not(:has(.o_viin_home_menu))",
        },
    ],
});
