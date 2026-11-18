/** @odoo-module **/

// The home-menu app tiles can be press-dragged to reorder, and the new order persists per user
// across a full reload (read back from res.users.viin_home_app_order). Driven by tests/test_tours.py,
// whose runner also asserts the server-side stored order.
//
// Dragging the second tile onto the first makes a different app first; after a same-session reload
// the grid is rebuilt from the server-stored order and that app is still first. The expected
// first-app xmlid is carried across the reload in sessionStorage, which survives a same-tab reload.
// `drag_and_drop(<target>)` drags the step's trigger element onto <target>.

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
                // The reorder re-renders on a following frame and fires an ORM write; the grid exposes
                // the acknowledged order as data-viin-saved-order. Poll (bounded) until a different
                // app is first and the server has acknowledged it, so the reload cannot race the write.
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
