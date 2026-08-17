/** @odoo-module **/

// T-4 (PR #658 review-fix) - keyboard accessibility of the theme shell. Driven by tests/test_tours.py.
//
// BYPASS BLOCKS (WCAG 2.4.1). A "Skip to main content" link is the FIRST focusable element on the
// page: from a fresh load the very first Tab lands on it. Without the skip link the first Tab lands on
// some other chrome control -> `.o_viin_skip_link:focus` never appears -> RED.
//
// (The rail roving-tabindex contract that used to live here was removed with the vertical rail in
// PR #658 item 1 - the flat home menu is now the sole app switcher, so there is no rail to make one
// Tab stop. The skip-link-first contract is unchanged and still guards the shell's focus order.)
//
// GROUNDED (OSM 19.0 + core source): registry path web_tour.tours + {url, steps: () => [...]}; the
// run vocabulary ("press <Key>") and `:focus` triggers are the v19 forms (web_tour tour_step; core
// home-menu/user-switch tours use `run: "press <Key>"`).

import { registry } from "@web/core/registry";

const tours = registry.category("web_tour.tours");

tours.add("viin_a11y_skip_link_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "from a fresh load, move focus with the very first Tab",
            trigger: "body",
            run: "press Tab",
        },
        {
            content: "the FIRST focusable element is the skip-to-main-content link (WCAG 2.4.1)",
            trigger: ".o_viin_skip_link:focus",
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
