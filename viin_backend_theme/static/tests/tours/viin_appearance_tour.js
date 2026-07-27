/** @odoo-module **/

// Durable HttpCase tours for the appearance (dark scheme + density) + D3 home-menu behaviors. Driven
// by tests/test_tours.py. Tours assert OBSERVABLE UI state only (an attribute on <html>, a rendered
// tile, the client action that loaded) - never internals. Each trigger is an implicit oracle: the
// step only advances once the UI reaches that state, so a regression stalls the step and fails.
//
// T-1 (PR #658 review-fix): the DARK toggle no longer instant-flips [data-bs-theme] with no reload.
// Dark is now a RECOMPILED server bundle (web.assets_web_dark), which cannot swap without a reload -
// so choosing Dark PERSISTS the choice (res.users.viin_color_scheme + the color_scheme cookie) and
// RELOADS, after which the server serves the dark bundle and boot-stamps data-bs-theme=dark. DENSITY
// stays instant + cookie-SSOT (no server field, no reload) - that tour is unchanged.
//
// GROUNDED (OSM 19.0 + core source): registry path web_tour.tours + {url, steps: () => [...]}; the
// run vocabulary ("click", "edit <text>", "press <Key>") and `expectUnloadPage: true` for a step
// whose action unloads the page are the v19 forms (web_tour tour_step / tour_automatic; core
// web/static/tests/tours/user_switch_tour.js uses expectUnloadPage on a reload/navigation click).

import { registry } from "@web/core/registry";

const tours = registry.category("web_tour.tours");

// D-DARK (T-1): toggling Dark PERSISTS the choice + effective cookie and RELOADS; after the reload
// the server serves the dark bundle and boot-stamps data-bs-theme=dark. There is NO instant, in-place
// flip. RED now: the current service instant-applies without reloading, so the click step below
// (expectUnloadPage) fails - the page never unloads within the timeout.
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
            // The choice reloads so the server can serve the recompiled dark bundle. Marking the step
            // as page-unloading is what distinguishes persist+reload from the retired instant flip.
            expectUnloadPage: true,
        },
        {
            content:
                "after the reload the server serves the dark bundle and boot-stamps data-bs-theme=dark",
            trigger: "html[data-bs-theme='dark']",
        },
    ],
});

// D-DARK persist: a FRESH /odoo load (new browser session) is boot-stamped dark server-side from the
// persisted user preference, proving the choice survives beyond the reloading session above.
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

// D-DENSITY: choosing Compact stamps the density attribute on <html> INSTANTLY, and it survives a
// reload. Density is cookie-SSOT by design (viin_density cookie, no server field), so the reload MUST
// happen inside ONE browser session: location.reload() keeps the cookie jar, whereas a fresh
// start_tour spawns a new Chrome that only re-injects the auth cookie (not viin_density). The
// post-reload assertion fails if the boot template stops re-reading the cookie (RED-on-removal).
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

// D3 HOME MENU: land on the flat home grid, fuzzy-search a partial app name, keyboard-navigate,
// and launch - asserting the app action actually loaded (F5 parity).
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
