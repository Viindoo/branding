/** @odoo-module **/

// T-4 (PR #658 review-fix), retargeted for the home-menu pre-focus product decision. Driven by
// tests/test_tours.py.
//
// BYPASS BLOCKS (WCAG 2.4.1) - narrowed guarantee. The "Skip to main content" link (webclient.xml)
// is NO LONGER the first Tab stop on a fresh `/odoo` load: ViinHomeMenu now pre-focuses its search
// input on mount, by deliberate product decision ("user lands on the screen, types, and the menu
// search starts immediately" wins over the old first-Tab-stop guarantee). That change withdrew ONLY
// the "first focusable element" claim - the skip link itself was not touched and still does its job.
// What remains true and is guarded here:
//   1. `.o_viin_skip_link` still exists in the DOM on every `/odoo` load.
//   2. it is still reachable by keyboard, backward, from the now-focused search input (Shift+Tab) -
//      it precedes the search input in DOM order (prepended before the NavBar/ActionContainer block),
//      so a bounded walk of repeated Shift+Tab presses must land on it. The walk is bounded rather
//      than a single hard-coded press because the exact number of NavBar stops in between is not
//      this test's concern - a future unrelated navbar change must not silently break this guard by
//      changing that count.
//   3. activating it (`skipToMainContent`, webclient_patch.js) still moves keyboard focus into the
//      main content region (`.o_action_manager`) - it still does its real job, not just exists.
//
// GROUNDED (OSM 19.0 + core source): registry path web_tour.tours + {url, steps: () => [...]};
// `TourHelpers.prototype.press` (web_tour tour_helpers_hoot.js) forwards to hoot-dom's `press()`,
// whose own `Tab`/`Shift+Tab` handling calls `getNextFocusableElement`/`getPreviousFocusableElement`
// to walk the REAL tab order - the same mechanism the previous version of this tour already relied on
// for its single `press Tab` step.

import { registry } from "@web/core/registry";

const tours = registry.category("web_tour.tours");

tours.add("viin_a11y_skip_link_keyboard_reachable_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "the skip-to-main-content link exists in the DOM on a fresh /odoo load (WCAG 2.4.1 bypass blocks)",
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
                            `.o_viin_skip_link within ${MAX_SHIFT_TABS} presses - it is no longer ` +
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

// APP TILES KEEP THEIR OWN ROLE (2026-08-17).
//
// An explicit `role` REPLACES an element's implicit role rather than adding to it. The home-menu
// tiles used to carry `role="listitem"`, so a screen reader announced "list item" where the user
// could in fact follow a link, and the tiles fell out of links navigation - the shortcut many
// screen-reader users rely on to move through a page of links. Since the tiles are now real
// anchors (home_menu.xml), the role that was being suppressed is an accurate and useful one, which
// makes the suppression a defect rather than a curiosity.
//
// The contract is therefore phrased as an ABSENCE plus the affordance that absence restores: every
// tile is an <a> WITH an href and WITHOUT a role attribute, so its `link` role survives. Written
// against the DOM the user's assistive technology actually reads - not against a source file - so
// it holds however the template is refactored.
//
// RED ON REVERT: putting `role="listitem"` back on the tile makes `a.o_app[href]:not([role])` match
// nothing and this step times out. It cannot pass vacuously either: the preceding step asserts the
// tiles exist at all, so an empty grid fails there first.
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
