/** @odoo-module **/

// Bypass blocks (WCAG 2.4.1) on the home-menu landing. Driven by tests/test_tours.py.
//
// ViinHomeMenu pre-focuses its search input on mount, so the "Skip to main content" link
// (webclient.xml) is not the first Tab stop on a fresh `/odoo` load. Guarded here:
//   1. `.o_viin_skip_link` exists in the DOM on every `/odoo` load.
//   2. It is reachable by keyboard, backward, from the focused search input (Shift+Tab): it precedes
//      the search input in DOM order, so a bounded walk of repeated Shift+Tab presses must land on
//      it. The walk is bounded because the number of NavBar stops in between is not this test's
//      concern.
//   3. Activating it (`skipToMainContent`, webclient_patch.js) moves keyboard focus into the main
//      content region (`.o_action_manager`).

import { registry } from "@web/core/registry";

const tours = registry.category("web_tour.tours");

tours.add("viin_a11y_skip_link_keyboard_reachable_tour", {
    url: "/odoo",
    steps: () => [
        {
            content:
                "the skip-to-main-content link exists in the DOM on a fresh /odoo load (WCAG 2.4.1 bypass blocks)",
            trigger: ".o_viin_skip_link",
        },
        {
            content:
                "the boot landing has already pre-focused the search input on mount (product " +
                "decision: land, type, search starts immediately) - that is where the backward " +
                "keyboard walk below starts from",
            trigger: ".o_viin_home_search_input:focus",
        },
        {
            content:
                "the skip link precedes the pre-focused search input in DOM order, so walking " +
                "Shift+Tab backward from it must still reach the skip link - bounded so an " +
                "unrelated future navbar change cannot silently disable this guard by changing how " +
                "many stops sit in between",
            trigger: "body",
            run: async (helpers) => {
                const MAX_SHIFT_TABS = 30;
                for (let i = 0; i < MAX_SHIFT_TABS; i++) {
                    if (document.activeElement?.matches?.(".o_viin_skip_link")) {
                        return;
                    }
                    await helpers.press("Shift+Tab");
                }
                if (!document.activeElement?.matches?.(".o_viin_skip_link")) {
                    throw new Error(
                        `Shift+Tab from the pre-focused search input did not reach ` +
                            `.o_viin_skip_link within ${MAX_SHIFT_TABS} presses - it is not ` +
                            `keyboard-reachable backward from the search input.`
                    );
                }
            },
        },
        {
            content: "the backward walk actually landed on the skip link",
            trigger: ".o_viin_skip_link:focus",
        },
        {
            content:
                "activating the skip link still does its real job: it moves keyboard focus into " +
                "the main content region, not just that the element exists and is reachable",
            trigger: ".o_viin_skip_link",
            run: "click",
        },
        {
            content: "focus landed on the main action region after activation (skipToMainContent)",
            trigger: ".o_action_manager:focus",
        },
    ],
});

// App tiles keep their own role. An explicit `role` replaces an element's implicit role, so a
// `role="listitem"` on a tile would hide its `link` role and drop it out of links navigation. Every
// tile is an <a> with an href and without a role attribute, asserted against the DOM that assistive
// technology reads. The preceding step asserts the tiles exist, so an empty grid cannot pass
// vacuously.
tours.add("viin_a11y_home_tile_semantics_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "the flat home menu is the boot landing and it has rendered its app tiles",
            trigger: ".o_viin_home_grid .o_viin_home_app",
        },
        {
            content:
                "every app tile is an ANCHOR carrying an href and NO role override, so assistive " +
                "technology announces it as a link and links navigation can reach it",
            trigger: ".o_viin_home_grid a.o_app[href]:not([role])",
        },
        {
            content:
                "and no tile anywhere in the grid still overrides its own role - a single " +
                "leftover would be announced as the wrong kind of thing",
            trigger: ".o_viin_home_grid:not(:has(.o_viin_home_app[role]))",
        },
    ],
});
