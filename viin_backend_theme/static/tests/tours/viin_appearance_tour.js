// Tours for the appearance (dark scheme + density) and the home-menu behaviours, driven by
// tests/test_tours.py. They assert observable UI state only (an attribute on <html>, a rendered
// tile, the client action that loaded); each trigger is an implicit oracle, so a regression stalls
// the step and fails.
//
// Dark is a recompiled server bundle (web.assets_web_dark) that cannot swap without a reload, so
// choosing Dark persists the choice (res.users.viin_color_scheme + the color_scheme cookie) and
// reloads; the server then serves the dark bundle and boot-stamps data-bs-theme=dark. Density is an
// instant flip backed by a cookie, with no server field.

import { registry } from "@web/core/registry";

const tours = registry.category("web_tour.tours");

// Toggling Dark persists the choice and the effective cookie, then reloads; there is no in-place
// flip, so the click step expects the page to unload.
tours.add("viin_dark_toggle_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "open the appearance (moon) systray",
            trigger: ".o_viin_appearance_toggle",
            run: "click",
        },
        {
            content:
                "choose the Dark scheme - this persists the pref + cookie and reloads the page",
            trigger: ".o_viin_appearance_option:contains(Dark)",
            run: "click",
            // The choice reloads so the server can serve the recompiled dark bundle.
            expectUnloadPage: true,
        },
        {
            content:
                "after the reload the server serves the dark bundle and boot-stamps data-bs-theme=dark",
            trigger: "html[data-bs-theme='dark']",
        },
    ],
});

// A fresh /odoo load is boot-stamped dark server-side from the persisted user preference.
tours.add("viin_dark_persist_tour", {
    url: "/odoo",
    steps: () => [
        {
            content:
                "after a fresh load the server still boot-stamps dark from the stored preference",
            trigger: "html[data-bs-theme='dark']",
        },
    ],
});

// Choosing Compact stamps the density attribute on <html> instantly, and it survives a reload.
// Density is cookie-backed (no server field), so the reload must stay inside one browser session: a
// fresh start_tour spawns a Chrome that only re-injects the auth cookie, not viin_density.
tours.add("viin_density_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "open the appearance systray",
            trigger: ".o_viin_appearance_toggle",
            run: "click",
        },
        {
            content: "choose Compact density",
            trigger: ".o_viin_appearance_option:contains(Compact)",
            run: "click",
        },
        {
            content: "the density attribute flips to compact instantly (no reload)",
            trigger: "html[data-viin-density='compact']",
        },
        {
            content: "reload the page in the same session",
            trigger: "html[data-viin-density='compact']",
            run: () => location.reload(),
            expectUnloadPage: true,
        },
        {
            content:
                "compact density survives the reload (boot template re-reads the viin_density cookie)",
            trigger: "html[data-viin-density='compact']",
        },
    ],
});

// Home menu: land on the flat grid, fuzzy-search a partial app name, keyboard-navigate and launch,
// asserting that the app action loaded.
tours.add("viin_home_menu_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "the flat home menu is the default landing; type a partial app name",
            trigger: ".o_viin_home_menu .o_viin_home_search_input",
            run: "edit Settin",
        },
        {
            content: "fuzzy search surfaces the Settings app tile",
            trigger: ".o_viin_home_grid .o_viin_home_app[title='Settings']",
        },
        {
            content: "arrow-navigate to the first match",
            trigger: ".o_viin_home_search_input",
            run: "press ArrowDown",
        },
        {
            content: "the first match is highlighted",
            trigger: ".o_viin_home_app.o_viin_home_app_focus[title='Settings']",
        },
        {
            content: "Enter launches the highlighted app",
            trigger: ".o_viin_home_search_input",
            run: "press Enter",
        },
        {
            content: "an app action loaded - the home menu was replaced",
            trigger: "body:not(:has(.o_viin_home_menu))",
        },
    ],
});
