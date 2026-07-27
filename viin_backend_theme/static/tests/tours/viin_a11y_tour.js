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
