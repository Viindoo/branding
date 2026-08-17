/** @odoo-module **/

// Owner request 2026-08-03: the apps icon must TOGGLE.
// "khi đang ở một view nào đó, bấm vào app icon thì nó về icon dashboard. Tao kỳ vọng bấm app icon
//  lần nữa thì nó lại về lại view cũ."
//
// Owner decision D3, 2026-08-17: it must toggle WITHOUT LEAVING THE PAGE.
//
// BEHAVIOUR PROTECTED (observable DOM state only - never an internal):
//   from a real view -> click the apps icon -> the flat home menu is shown AND THE VIEW UNDERNEATH
//                       IS STILL MOUNTED
//                    -> click the apps icon AGAIN -> that same view is on screen again.
//
// ONE ASSERTION IN THIS FILE WAS INVERTED ON 2026-08-17, AND HERE IS EXACTLY WHY IT IS NOT A
// WEAKENING. The step below now reads
//     "the Settings view is STILL mounted underneath the home menu"   (.o_base_settings_view present)
// where it used to read
//     "guard: the Settings view is no longer mounted"                 (.o_base_settings_view absent).
// The old wording was a faithful description of the old MECHANISM - openHomeMenu() ran a full-page
// `doAction`, which unmounts the controller - and that unmount is precisely the defect the owner
// ruled on: core's contract for `.o_navbar_apps_menu button` is that it opens a list and does NOT
// navigate, and 57 core tour files depend on it (`stepUtils.showAppsMenuItem()`; two of them,
// test_base_automation's `test_01_base_automation_tour` and `test_base_automation_on_tag_added`,
// click that button as boilerplate and then keep working on the SAME kanban). So the old step
// asserted the bug. The new step asserts the contract, and it is STRICTLY STRONGER: "the view is
// gone" is satisfied by any number of wrong outcomes (a blank action manager, a bounce to the
// default app), whereas "this exact view is still mounted, and it is still there after the toggle"
// can only be satisfied by the intended one. Nothing was relaxed and no assertion was removed - the
// step count went UP.
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
// `.o_viin_home_menu`, its non-navigating arm adds `.o_viin_home_overlay`, and its tiles are
// `a.o_app[data-menu-xmlid]` (home_menu.xml). `:has` / `:not` triggers are the v19 hoot-dom forms.

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
            content: "guard: the boot home menu really was replaced (not just overlaid)",
            trigger: "body:not(:has(.o_viin_home_menu))",
        },
        {
            content: "FIRST click on the apps icon - shows the home menu OVER the current view",
            trigger: ".o_navbar_apps_menu button:enabled",
            run: "click",
        },
        {
            content:
                "the flat home menu is shown, as the non-navigating overlay arm " +
                "(.o_viin_home_overlay), with its app tiles present",
            trigger: ".o_viin_home_menu.o_viin_home_overlay a.o_app[data-menu-xmlid]",
        },
        {
            content:
                "THE D3 CONTRACT: the Settings view is STILL MOUNTED underneath. Core's apps " +
                "button opens a list without navigating, and 57 core tours rely on the view they " +
                "were working on surviving that click - this is the step that pins it.",
            trigger: ".o_action_manager .o_form_view.o_base_settings_view",
        },
        {
            content: "SECOND click on the same apps icon - this must put the panel away, not re-open",
            trigger: ".o_navbar_apps_menu button:enabled",
            run: "click",
        },
        {
            content:
                "THE ASK: the ORIGINAL Settings view is on screen again - the apps icon toggled the " +
                "home menu off and the user is back where they were",
            trigger: ".o_action_manager .o_form_view.o_base_settings_view",
        },
        {
            content: "...and the home menu is closed, not merely hidden behind the view",
            trigger: "body:not(:has(.o_viin_home_menu))",
        },
    ],
});

// D3 companion: the home menu is an OVERLAY, not a BLOCKER. Core's apps dropdown closes on an
// outside interaction and has no backdrop, so the page underneath stays reachable - that is what
// makes `stepUtils.showAppsMenuItem()` safe as a boilerplate step in core tours that then go on to
// click something in the view. This tour pins the same two properties for the theme's panel:
// interacting with the view underneath (a) dismisses the panel and (b) leaves the view standing.
//
// RED BEFORE: with the client-action mechanism the FIRST apps click destroyed the Settings view, so
// `.o_control_panel` inside it did not exist and this tour stalled at step 4.
registry.category("web_tour.tours").add("viin_apps_menu_overlay_dismiss_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "the flat home menu is the boot landing - launch a real view from it",
            trigger: ".o_viin_home_grid .o_viin_home_app[title='Settings']",
            run: "click",
        },
        {
            content: "the Settings view is open",
            trigger: ".o_action_manager .o_form_view.o_base_settings_view",
        },
        {
            content: "open the home menu over it",
            trigger: ".o_navbar_apps_menu button:enabled",
            run: "click",
        },
        {
            content: "the overlay is up",
            trigger: ".o_viin_home_menu.o_viin_home_overlay a.o_app[data-menu-xmlid]",
        },
        {
            content:
                "interact with the view UNDERNEATH - its control panel is still there to be " +
                "clicked, which is the whole point of not unmounting it",
            trigger: ".o_action_manager .o_base_settings_view .o_control_panel",
            run: "click",
        },
        {
            content: "the outside interaction dismissed the home menu (no backdrop swallowed it)",
            trigger: "body:not(:has(.o_viin_home_menu))",
        },
        {
            content: "and the Settings view is still the one on screen",
            trigger: ".o_action_manager .o_form_view.o_base_settings_view",
        },
        {
            content: "re-open the panel to check the keyboard escape route",
            trigger: ".o_navbar_apps_menu button:enabled",
            run: "click",
        },
        {
            content: "the overlay is up again",
            trigger: ".o_viin_home_menu.o_viin_home_overlay",
        },
        {
            content:
                "Escape dismisses it - a non-modal overlay a keyboard user cannot leave is a " +
                "WCAG 2.1.2 defect, and the full-page client action it replaced had no such exit",
            trigger: ".o_viin_home_menu.o_viin_home_overlay .o_viin_home_search_input",
            run: "press Escape",
        },
        {
            content: "the panel is gone...",
            trigger: "body:not(:has(.o_viin_home_menu))",
        },
        {
            content: "...and the view underneath was never disturbed",
            trigger: ".o_action_manager .o_form_view.o_base_settings_view",
        },
    ],
});
