/** @odoo-module **/

import { animationFrame, beforeEach, describe, expect, press, queryOne, test } from "@odoo/hoot";
import { registry } from "@web/core/registry";
import {
    defineMenus,
    defineModels,
    fields,
    getService,
    mountWithCleanup,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { mailModels } from "@mail/../tests/mail_test_helpers";

// Enter-to-launch on the flat home menu (ViinHomeMenu): onSearchKeydown's "Enter" case falls back to
// filteredApps[0] whenever nothing is explicitly highlighted. That is right once a query narrows the
// grid ("type then Enter" works without an extra keystroke) but wrong while nothing has been typed:
// with the pre-focused, still-empty search box (viin_home_typeahead.test.js) an Enter the user never
// meant as a selection would launch whatever app renders first. These tests pin the three rules that
// decide which side of that line Enter is on, asserting only whether, and which, app the "menu"
// service was asked to open: disabling Enter outright breaks "type then Enter", and gating on the
// query alone breaks the explicit-highlight rule, which must win independently of what was typed.

class ResUsers extends mailModels.ResUsers {
    viin_home_app_order = fields.Char();
}
defineModels({ ...mailModels, ResUsers });

/** @returns {HTMLInputElement} */
function searchInput() {
    return queryOne(".o_viin_home_search_input");
}

/**
 * Mount the real ViinHomeMenu client action (same registry lookup and onRpc stubs as
 * viin_home_typeahead.test.js's mountHomeMenu), then replace the "menu" service's selectMenu with an
 * expect.step spy. getService("menu") returns the object the component's own useService("menu")
 * holds, so the patch is visible to it regardless of patch-vs-mount order. A test then asserts via
 * expect.verifySteps which app (or none) a launch reached.
 */
async function mountHomeMenu(props = {}) {
    onRpc("mail.activity", "search_count", () => 0);
    onRpc("res.users", "read", () => [{ viin_home_app_order: false }]);
    const ViinHomeMenu = registry.category("actions").get("viin_home_menu");
    const component = await mountWithCleanup(ViinHomeMenu, { props });
    await animationFrame(); // let onWillStart's activity/order reads settle
    patchWithCleanup(getService("menu"), {
        selectMenu: (menu) => expect.step(menu ? `launched:${menu.xmlid}` : "launched:none"),
    });
    return component;
}

describe("ViinHomeMenu Enter-to-launch", () => {
    describe("nothing typed, nothing highlighted", () => {
        beforeEach(() => {
            defineMenus([{ id: 1, name: "Accounting", xmlid: "app.accounting" }]);
        });

        test("Enter with an empty search and no highlighted tile opens nothing", async () => {
            await mountHomeMenu();
            // onSearchKeydown is bound on the search input itself and "Enter" is not a single
            // printable character, so onWindowKeydown's recovery listener never routes it there:
            // without an explicit focus this Enter would land on <body>, the handler under test would
            // not run, and the test would pass for the wrong reason on any preset that skips the
            // touch-gated mount-time pre-focus.
            searchInput().focus();

            await press("Enter");
            await animationFrame();

            expect.verifySteps([], {
                message:
                    "with nothing typed and nothing highlighted, Enter must not ask the menu " +
                    "service to open any app - there is no selection to act on.",
            });
        });
    });

    describe("a query is typed, nothing explicitly highlighted", () => {
        beforeEach(() => {
            // "Sales" ranks ahead of "Wholesale" for the query "sale": fuzzyLookup scores an
            // earlier, more-consecutive match higher, and "sale" sits at the very start of
            // "Sales" but only after "Whole" in "Wholesale" - so filteredApps[0] is deterministic.
            defineMenus([
                { id: 1, name: "Sales", xmlid: "app.sales" },
                { id: 2, name: "Wholesale", xmlid: "app.wholesale" },
            ]);
        });

        test("Enter with a typed query and no highlight opens the best-matching app", async () => {
            await mountHomeMenu();

            await press("s");
            await press("a");
            await press("l");
            await press("e");
            await animationFrame();
            await press("Enter");
            await animationFrame();

            expect.verifySteps(["launched:app.sales"], {
                message:
                    "typing a query that matches results, then pressing Enter, must launch the " +
                    "best match - a fix that disables Enter whenever nothing is highlighted would " +
                    "silently break type-then-Enter, which is the feature this guards.",
            });
        });
    });

    describe("a tile is explicitly highlighted via arrow keys", () => {
        beforeEach(() => {
            defineMenus([
                { id: 1, name: "Accounting", xmlid: "app.accounting" },
                { id: 2, name: "Inventory", xmlid: "app.inventory" },
            ]);
        });

        test("Enter opens the arrow-highlighted tile, not the first one, even with nothing typed", async () => {
            await mountHomeMenu();
            // onSearchKeydown (ArrowRight/Enter) is bound on the search input itself and neither key
            // is a single printable character, so the input must already be focused, as after a user
            // taps the search box. Focus is set explicitly rather than relying on the touch-gated
            // mount-time pre-focus: the rule under test (an explicit highlight wins) is independent
            // of touch state.
            searchInput().focus();

            // Two ArrowRight presses move the highlight from "none" (-1) to index 0, then index 1:
            // the SECOND app, so a launch of the first app cannot be mistaken for the "nothing
            // highlighted" fallback the other tests guard against.
            await press("ArrowRight");
            await press("ArrowRight");
            await animationFrame();
            await press("Enter");
            await animationFrame();

            expect.verifySteps(["launched:app.inventory"], {
                message:
                    "an explicitly arrow-highlighted tile must open on Enter regardless of the " +
                    "search query - an empty query here proves a query-based guard on Enter " +
                    "cannot be the fix, since that would block this case too.",
            });
        });
    });
});
