// The apps icon toggles without leaving the page: from a real view, click the apps icon -> the
// flat home menu is shown and the view underneath is still mounted -> click the apps icon again ->
// that same view is on screen again. Only observable DOM state is asserted.
//
// Settings is the view because it exists in a minimal install and is launched from the home menu
// like the sibling viin_home_menu_tour (viin_appearance_tour.js). Its form carries the stable core
// root class `.o_base_settings_view`, a stronger "this exact view came back" marker than a generic
// .o_form_view. The apps trigger core app-switch tours click is `.o_navbar_apps_menu button:enabled`;
// the overlay arm of the home menu adds `.o_viin_home_overlay`.

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
                "opening the overlay via the apps icon (a deliberate user action) lands " +
                "focus in the search box, so the user never has to click it after opening.",
            trigger: ".o_viin_home_menu .o_viin_home_search_input:focus",
        },
        {
            content:
                "THE CONTRACT: the Settings view is STILL MOUNTED underneath. Core's apps " +
                "button opens a list without navigating, and core tours rely on the view they " +
                "were working on surviving that click - this is the step that pins it.",
            trigger: ".o_action_manager .o_form_view.o_base_settings_view",
        },
        {
            content:
                "SECOND click on the same apps icon - this must put the panel away, not re-open",
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

// The home menu is an overlay, not a blocker: core's apps dropdown closes on an outside
// interaction and has no backdrop, so the page underneath stays reachable, which keeps
// `stepUtils.showAppsMenuItem()` safe as a boilerplate step in core tours. Interacting with the
// view underneath (a) dismisses the panel and (b) leaves the view standing.
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
                "WCAG 2.1.2 defect",
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
