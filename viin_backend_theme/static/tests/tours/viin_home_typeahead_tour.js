/** @odoo-module **/

// Type-to-search on the flat home menu, driven end-to-end on the BOOT-LANDING client-action
// render (a fresh /odoo load) - the shape the Hoot unit tests (viin_home_typeahead.test.js) cannot
// reach, since those mount the component directly rather than booting the real webclient. A user
// must be able to start typing the instant the screen is up, with no click on the search box
// first, and a keystroke that arrives after focus was briefly lost must APPEND to whatever the
// user had already typed rather than replace it.
//
// GROUNDED: `run: "press <key>"` invokes Odoo 19.0's own tour-automation keyboard helper,
// `TourHelpers.prototype.press`, which forwards to `hoot.press()` from `@odoo/hoot-dom` - the SAME
// `press()` the Hoot unit tests (`viin_home_typeahead.test.js`) already use, with the same real
// two-phase target resolution (once before, once after the keydown dispatch) and the same
// append-not-overwrite insertion semantics already validated there. A raw, untrusted synthetic
// `dispatchEvent` never triggers a real browser's native text-insertion default action, so this
// file does not construct one by hand.

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("viin_home_typeahead_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "the boot-landing home menu is up, search box present",
            trigger: ".o_viin_home_menu .o_viin_home_search_input",
        },
        {
            content:
                "typing a printable character with nothing clicked must reach the search box - " +
                "the user must never have to click it first",
            trigger: "body",
            run: "press a",
        },
        {
            content:
                "the search box now owns focus AND holds the typed character, with no click ever performed",
            trigger: ".o_viin_home_search_input:focus",
            run: function () {
                if (this.anchor.value !== "a") {
                    throw new Error(
                        `expected the search box to contain "a" after typing with nothing ` +
                            `focused, got "${this.anchor.value}"`
                    );
                }
            },
        },
        {
            content: "lose focus - simulate the user tabbing or clicking away from the search box",
            trigger: ".o_viin_home_search_input",
            run: () => {
                document.activeElement.blur();
            },
        },
        {
            content: "focus is genuinely gone before the next keystroke",
            trigger: ".o_viin_home_search_input:not(:focus)",
        },
        {
            content:
                "typing again after losing focus must APPEND to what was already there, never " +
                "overwrite it - the user must not lose the character they already typed",
            trigger: "body",
            run: "press b",
        },
        {
            content:
                "the search box regained focus and holds the ORIGINAL content plus the new " +
                "character, not just the new character alone",
            trigger: ".o_viin_home_search_input:focus",
            run: function () {
                if (this.anchor.value !== "ab") {
                    throw new Error(
                        `expected the search box to contain "ab" after a keystroke that lost and ` +
                            `regained focus, got "${this.anchor.value}"`
                    );
                }
            },
        },
    ],
});
