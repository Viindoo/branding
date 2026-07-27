/** @odoo-module **/

// PR #658 item 7 - the home-menu app tiles can be press-dragged to reorder, and the new order PERSISTS
// per-user across a full page reload (read back from res.users.viin_home_app_order). Driven by
// tests/test_tours.py, whose runner also asserts the SERVER-side observable (the stored order field).
//
// BEHAVIOUR PROTECTED (observable DOM state, never internals): dragging the second tile onto the first
// reorders the grid (a DIFFERENT app becomes first), and after a same-session reload - which rebuilds
// the grid from the SERVER-stored order via the home menu's onWillStart read - that reordered app is
// still first. The expected first-app xmlid is carried across the reload in sessionStorage (which
// survives a same-tab reload), so the post-reload step is a real end-to-end persistence assertion, not
// a trivially-true check. RED before item 7 (no drag, no stored order); GREEN after.
//
// GROUNDED (OSM 19.0 + core source): the home grid is .o_viin_home_grid and its tiles are
// .o_viin_home_app[data-menu-xmlid] (home_menu.xml). The `drag_and_drop(<target>)` run helper drags
// the step's trigger element onto <target> (web_tour tour_helpers_hoot.js); dragging a later element
// onto an earlier one to move it up mirrors core's im_livechat_chatbot_steps_sequence reorder tour.

import { registry } from "@web/core/registry";

const BEFORE_KEY = "viin_home_reorder_before";
const EXPECTED_KEY = "viin_home_reorder_expected";

registry.category("web_tour.tours").add("viin_home_reorder_persist_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "the flat home menu is the boot landing; wait for at least two app tiles",
            trigger: ".o_viin_home_grid .o_viin_home_app:nth-child(2)",
            run() {
                // Record the ORIGINAL first tile so the drag step can prove the order changed.
                const first = document.querySelector(".o_viin_home_grid .o_viin_home_app");
                sessionStorage.setItem(BEFORE_KEY, first.dataset.menuXmlid);
            },
        },
        {
            content:
                "press-drag the SECOND app tile onto the FIRST to move it up; a real drag sets the " +
                "sortable's preventClick so the dragged tile never launches its app",
            trigger: ".o_viin_home_grid .o_viin_home_app:nth-child(2)",
            run: "drag_and_drop(.o_viin_home_grid .o_viin_home_app:first-child)",
        },
        {
            content: "the drag reordered the grid AND the new order was persisted to the server",
            trigger: ".o_viin_home_grid .o_viin_home_app:first-child",
            async run() {
                const before = sessionStorage.getItem(BEFORE_KEY);
                // The reorder rewrites reactive state (re-render on a following frame) and fires an ORM
                // write; the grid exposes the server-ACKNOWLEDGED order as data-viin-saved-order once
                // the write resolves. Poll (bounded) until BOTH a different app is first AND the server
                // has acknowledged it - so the reload below cannot race an unsettled write.
                for (let attempt = 0; attempt < 60; attempt++) {
                    const grid = document.querySelector(".o_viin_home_grid");
                    const now = grid?.querySelector(".o_viin_home_app")?.dataset.menuXmlid;
                    const saved = grid?.dataset.viinSavedOrder;
                    if (now && now !== before && saved && saved.split(",")[0] === now) {
                        // Remember the reordered-first app so the post-reload step can prove it stuck.
                        sessionStorage.setItem(EXPECTED_KEY, now);
                        return;
                    }
                    await new Promise((resolve) => setTimeout(resolve, 50));
                }
                throw new Error(
                    "the drag did not reorder + persist the home tiles (the first tile never " +
                        "changed, or the server never acknowledged the new order)"
                );
            },
        },
        {
            content: "reload the page in the same session - the order must survive a full reload",
            trigger: ".o_viin_home_grid .o_viin_home_app:first-child",
            run: () => location.reload(),
            expectUnloadPage: true,
        },
        {
            content:
                "after the reload the grid rebuilds from the SERVER-stored order; the reordered app " +
                "is still first (persisted across the reload)",
            trigger: ".o_viin_home_grid .o_viin_home_app:nth-child(2)",
            run() {
                const expected = sessionStorage.getItem(EXPECTED_KEY);
                const now = document.querySelector(".o_viin_home_grid .o_viin_home_app").dataset
                    .menuXmlid;
                if (now !== expected) {
                    throw new Error(
                        "the reordered app order did not persist across the reload " +
                            "(expected " +
                            expected +
                            " first, got " +
                            now +
                            ")"
                    );
                }
            },
        },
    ],
});
