/** @odoo-module **/
/* Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { Component, xml } from "@odoo/owl";
import { expect, test } from "@odoo/hoot";
import { press } from "@odoo/hoot-dom";
import { advanceTime, animationFrame } from "@odoo/hoot-mock";
import {
    contains,
    defineActions,
    defineMenus,
    getService,
    mountWithCleanup,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { WebClient } from "@web/webclient/webclient";
import { AppsMenuAction } from "@web_responsive/components/apps_menu/apps_menu_service";

// web_responsive depends on `mail`; mounting anything that pulls the patched NavBar/systray needs
// mail's mock models registered, or the mount aborts on `discuss.channel` before any assertion
// runs. Module-level call, matching core's own convention.
defineMailModels();

// Re-implementation of the QUnit suite retired by 8069ccc (apps_menu_search_tests.esm.js).
// Real transition: mount the actual fullscreen client action (never a hand-seeded DOM) and read the
// real rendered DOM. The template AppsMenuAction mounts always passes AppsMenu the `open="true"`
// prop directly (apps_menu.xml), so the container is open from AppsMenu's very first render -
// AppsMenuScreen's mounted-effect / APPS_MENU:TOGGLE bus round trip (apps_menu_service.js,
// apps_menu.esm.js) also fires on mount, but is redundant here since the prop already opened it.
test("the search input renders exactly once inside the fullscreen apps-menu container", async () => {
    defineMenus([{ id: 1, name: "App One" }]);

    await mountWithCleanup(AppsMenuAction, {
        props: {
            action: { id: 1, tag: "menu", target: "current", type: "ir.actions.client" },
            actionId: 1,
        },
        // env.config as the real action service would supply it to a mounted action
        // (action_service.js:828-829). Without it, AppsMenuAction.setup() throws reading
        // `this.env.config.breadcrumbs.length` (apps_menu_service.js:35) and Owl destroys the
        // root before this test's assertion ever runs. `componentEnv` is 18.0 core's own
        // mechanism for supplying env.config to a directly-mounted action-adjacent component -
        // see mountView()'s identical `componentEnv: { config: params.config }` in
        // view_test_helpers.js:228-232.
        componentEnv: { config: { breadcrumbs: [] } },
    });
    await animationFrame();

    expect(".app-menu-container .search-input").toHaveCount(1);
});

// Every test below protects one rule: picking a menu leaves the apps-menu overlay closed.
// Grounded in the real overlay path (apps_menu service -> AppsMenuOverlay), not the client-action
// props above - AppsMenuScreen.dismiss() is a no-op there; only AppsMenuOverlay.dismiss() removes it.

const SEARCH_TARGET_ACTION_ID = 90501;

// A single, highly-distinctive app name keeps every fuzzy/Fuse search below matching exactly this
// one menu, so a search finding nothing (or the wrong thing) signals a real defect rather than an
// ambiguous result set.
const SEARCH_TARGET_MENU = [
    {
        id: 90501,
        name: "AppsMenuSearchTarget",
        xmlid: "menu_apps_menu_search_target",
        actionID: SEARCH_TARGET_ACTION_ID,
        appID: 90501,
    },
];

// Private tag, not core's shared `useTestClientAction()` (`"__test__client__action__"`) - that
// tag already registers in menu_provider.test.js/burger_menu.test.js within the same
// web.assets_unit_tests bundle; reusing it collides at registry-registration time, taking the
// bundle down.
class AppsMenuSearchTargetAction extends Component {
    static template = xml`<div class="apps_menu_search_target_action" t-esc="props.action.params?.description"/>`;
    static props = ["*"];
}
const APPS_MENU_SEARCH_TARGET_ACTION_TAG = "web_responsive_test__apps_menu_search_target_action";
registry.category("actions").add(APPS_MENU_SEARCH_TARGET_ACTION_TAG, AppsMenuSearchTargetAction);

defineActions([
    {
        id: SEARCH_TARGET_ACTION_ID,
        tag: APPS_MENU_SEARCH_TARGET_ACTION_TAG,
        target: "main",
        type: "ir.actions.client",
        params: { description: "AppsMenuSearchTarget" },
    },
]);

/**
 * Mounts the real WebClient and opens the apps-menu OVERLAY the way a user actually does - through
 * the "apps_menu" service - never the client-action presentation used by the test above. `session`
 * must carry `search_type` before the mount: AppsMenuSearchBar reads it once, in setup()
 * (menu_searchbar/searchbar.esm.js), so patching it after the search bar has already mounted would
 * silently do nothing.
 *
 * @param {string} [searchType] "fuse" or "command_palette"; omit for the "canonical" default.
 */
async function openAppsMenuOverlay(searchType) {
    if (searchType) {
        patchWithCleanup(session, { apps_menu: { search_type: searchType } });
    }
    await mountWithCleanup(WebClient);
    await getService("apps_menu").toggleMenu(true);
    await animationFrame();

    // Control: the overlay is actually open before any search interaction, so the "it closed"
    // assertion below cannot pass for free.
    expect(".app-menu-container").toHaveCount(1);
}

/**
 * Asserts the two outcomes a menu selection must always leave behind, regardless of which search
 * bar variant or input method reached it: the user is on the target screen, and the apps-menu
 * overlay that was covering it is gone.
 */
function expectNavigatedToTargetAndOverlayClosed() {
    // DOM-based first: a missing element fails this assertion cleanly, whereas reading
    // .action.id off a not-yet-set currentController would throw instead of failing - optional
    // chaining below keeps that check a clean failure too if navigation is ever somehow slower
    // than expected, rather than a broken (error, not red) measurement.
    expect(".apps_menu_search_target_action").toHaveText("AppsMenuSearchTarget");
    expect(getService("action").currentController?.action?.id).toBe(SEARCH_TARGET_ACTION_ID);
    expect(".app-menu-container").toHaveCount(0);
}

test.tags("desktop");
test("clicking a canonical search result dismisses the apps-menu overlay after navigating to it", async () => {
    defineMenus(SEARCH_TARGET_MENU);
    await openAppsMenuOverlay();

    await contains(".app-menu-container .search-input input").edit("AppsMenuSearchTarget", {
        confirm: false,
    });
    // _searchMenus is debounced 200ms (menu_canonical_searchbar/searchbar.esm.js) - the result
    // list only appears once that timer fires.
    await advanceTime(200);
    await animationFrame();

    expect(".app-menu-container .search-item__link").toHaveCount(1);

    await contains(".app-menu-container .search-item__link").click();
    // doAction's own controller swap needs a render cycle beyond the click's own animationFrame,
    // same as core's menu-selection tests (menu_provider.test.js).
    await animationFrame();
    await animationFrame();

    expectNavigatedToTargetAndOverlayClosed();
});

test.tags("desktop");
test(
    "pressing Enter on a highlighted canonical search result dismisses the apps-menu overlay " +
        "after navigating to it",
    async () => {
        defineMenus(SEARCH_TARGET_MENU);
        await openAppsMenuOverlay();

        await contains(".app-menu-container .search-input input").edit("AppsMenuSearchTarget", {
            confirm: false,
        });
        await advanceTime(200);
        await animationFrame();

        // The first (only) result is highlighted by default (state.offset starts at 0), which is
        // what _onKeyDown's "Enter" branch clicks via _selectHighlightedSearchItem.
        expect(".app-menu-container .search-item.highlight .search-item__link").toHaveCount(1);

        // _onKeyDown reads ev.code, not ev.key - hoot-dom's press() only sets .key, so the code
        // must be given explicitly or the handler's `code === "Enter"` branch is never reached.
        await press("Enter", { code: "Enter" });
        await animationFrame();
        await animationFrame();

        expectNavigatedToTargetAndOverlayClosed();
    }
);

test.tags("desktop");
test("clicking a fuse search result dismisses the apps-menu overlay after navigating to it", async () => {
    defineMenus(SEARCH_TARGET_MENU);
    await openAppsMenuOverlay("fuse");

    await contains(".app-menu-container .search-input input").edit("AppsMenuSearchTarget", {
        confirm: false,
    });
    await advanceTime(200);
    await animationFrame();

    expect(".app-menu-container .search-item__link").toHaveCount(1);

    await contains(".app-menu-container .search-item__link").click();
    await animationFrame();
    await animationFrame();

    expectNavigatedToTargetAndOverlayClosed();
});

test.tags("desktop");
test(
    "pressing Enter on a highlighted fuse search result dismisses the apps-menu overlay after " +
        "navigating to it",
    async () => {
        defineMenus(SEARCH_TARGET_MENU);
        await openAppsMenuOverlay("fuse");

        await contains(".app-menu-container .search-input input").edit("AppsMenuSearchTarget", {
            confirm: false,
        });
        await advanceTime(200);
        await animationFrame();

        expect(".app-menu-container .search-item.highlight .search-item__link").toHaveCount(1);

        // Same ev.code requirement as the canonical Enter test above - AppsMenuFuseSearchBar
        // inherits _onKeyDown unmodified from AppsMenuCanonicalSearchBar.
        await press("Enter", { code: "Enter" });
        await animationFrame();
        await animationFrame();

        expectNavigatedToTargetAndOverlayClosed();
    }
);

test.tags("desktop");
test(
    "selecting a menu from the command palette opened via the search bar dismisses the " +
        "apps-menu overlay after navigating to it",
    async () => {
        defineMenus(SEARCH_TARGET_MENU);
        await openAppsMenuOverlay("command_palette");

        // AppsMenuOdooSearchBar's own _onSearchInput clears its input on every 'input' event
        // (menu_odoo_searchbar/searchbar.esm.js), so a character-by-character edit() would leak
        // only its LAST character into the palette's search value. `instantly` pastes the whole
        // string as one 'input' event instead, matching what a real paste (or IME confirm) does.
        await contains(".app-menu-container .search-input input").edit("AppsMenuSearchTarget", {
            confirm: false,
            instantly: true,
        });
        await animationFrame();

        expect(".o_command_palette").toHaveCount(1);
        expect(".o_command").toHaveCount(1);

        await contains(".o_command").click();
        await animationFrame();
        await animationFrame();

        expect(".o_command_palette").toHaveCount(0);
        expectNavigatedToTargetAndOverlayClosed();
    }
);

test.tags("desktop");
test("escaping the command palette without selecting a menu leaves the apps-menu overlay open", async () => {
    // Core's command-service onClose fires unconditionally on every dialog close - selection,
    // Escape, and click-outside alike (command_service.js openPalette). A fix that dismisses the
    // overlay from that onClose without checking whether a selection actually happened would
    // wrongly close it here too, even though escaping the palette must leave the user exactly
    // where they were.
    defineMenus(SEARCH_TARGET_MENU);
    await openAppsMenuOverlay("command_palette");

    await contains(".app-menu-container .search-input input").edit("AppsMenuSearchTarget", {
        confirm: false,
        instantly: true,
    });
    await animationFrame();

    expect(".o_command_palette").toHaveCount(1);

    await press("escape");
    await animationFrame();

    expect(".o_command_palette").toHaveCount(0);
    // No selection was made: the apps menu must still be exactly where the user left it.
    expect(".app-menu-container").toHaveCount(1);
    expect(".app-menu-container .search-input input").toHaveCount(1);
});

test.tags("desktop");
test(
    "typing multiple characters into the command palette search registers the dismiss " +
        "callback only once per open-palette session",
    async () => {
        defineMenus(SEARCH_TARGET_MENU);
        await openAppsMenuOverlay("command_palette");

        const onCloseArgsPerCall = [];
        // Grounded at the command-service call boundary, not patch.js's private WeakMap - keeps
        // this a service-contract assertion, never an internals test.
        patchWithCleanup(getService("command"), {
            openMainPalette(config, onClose) {
                onCloseArgsPerCall.push(onClose);
                return super.openMainPalette(config, onClose);
            },
        });

        // Default edit() (no `instantly`) fires one 'input' event per character - the path the
        // two command_palette tests above deliberately bypass.
        await contains(".app-menu-container .search-input input").edit("Sal", {
            confirm: false,
        });
        await animationFrame();

        expect(onCloseArgsPerCall.length).toBe(3);
        expect(typeof onCloseArgsPerCall[0]).toBe("function");
        expect(onCloseArgsPerCall[1]).toBe(undefined);
        expect(onCloseArgsPerCall[2]).toBe(undefined);
    }
);
