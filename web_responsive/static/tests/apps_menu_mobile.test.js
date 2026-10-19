/** @odoo-module **/
/* Copyright 2026 Viindoo
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { Component, xml } from "@odoo/owl";
import { beforeEach, describe, expect, test } from "@odoo/hoot";
import { manuallyDispatchProgrammaticEvent as dispatch, queryAll, queryFirst } from "@odoo/hoot-dom";
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
import { config as transitionConfig } from "@web/core/transition";
import { WebClient } from "@web/webclient/webclient";
import { AppsMenuAction } from "@web_responsive/components/apps_menu/apps_menu_service";

// Importing AppsMenuAction pulls in apps_menu.esm.js, so the NavBar patch under test is loaded
// by this file's own import graph.

// web_responsive depends on `mail`, whose NavBar/systray patches need mail's mock models.
defineMailModels();

describe.current.tags("mobile");

// Sidebar, burger menu and backdrop are portalled to <body>, outside the mounted WebClient root.
const BODY = { root: document.body };
const inBody = (selector) => queryAll(selector, BODY);

const TARGET_ACTION_ID = 90601;
const TARGET_ACTION_TAG = "web_responsive_test__apps_menu_mobile_target_action";

// Private tag: core's shared test client-action tag collides at registration inside the shared
// web.assets_unit_tests bundle.
class MobileTargetAction extends Component {
    static template = xml`<div class="apps_menu_mobile_target_action" t-esc="props.action.params?.description"/>`;
    static props = ["*"];
}
registry.category("actions").add(TARGET_ACTION_TAG, MobileTargetAction);

defineActions([
    {
        id: TARGET_ACTION_ID,
        tag: TARGET_ACTION_TAG,
        target: "main",
        type: "ir.actions.client",
        params: { description: "MobileTargetApp" },
    },
]);

beforeEach(() => {
    defineMenus([
        { id: 0 }, // prevents auto-loading the first action
        {
            id: 1,
            name: "MobileTargetApp",
            xmlid: "menu_mobile_target_app",
            actionID: TARGET_ACTION_ID,
            appID: 1,
        },
        {
            id: 2,
            name: "OtherApp",
            xmlid: "menu_mobile_other_app",
            actionID: TARGET_ACTION_ID,
            appID: 2,
        },
    ]);
    patchWithCleanup(transitionConfig, { disabled: true });
});

/**
 * Mounts the client (optionally with a screen open behind) and taps the navbar toggle to open the
 * sidebar, spying on the apps_menu service so each test can tell how often the grid was asked to
 * open or close.
 */
async function openSidebar({ withScreen = false } = {}) {
    await mountWithCleanup(WebClient);
    if (withScreen) {
        await getService("action").doAction(TARGET_ACTION_ID);
    }
    const appsMenu = getService("apps_menu");
    patchWithCleanup(appsMenu, {
        toggleMenu(openState) {
            expect.step(`toggleMenu:${openState}`);
            return super.toggleMenu(openState);
        },
    });
    await contains(".o_main_navbar .o_menu_toggle").click();
    // Control: the sidebar is open before any further interaction, so a later "closed" assertion
    // cannot pass for free.
    expect(inBody(".o_app_menu_sidebar")).toHaveCount(1);
}

test("the mobile navbar shows a labelled apps grid icon in the menu toggle", async () => {
    await mountWithCleanup(WebClient);

    expect(".o_main_navbar .o_menu_toggle").toHaveCount(1);
    expect(".o_main_navbar .o_menu_toggle .fa-th-large").toHaveCount(1);
    expect(".o_main_navbar .o_menu_toggle .fa-bars").toHaveCount(0);
    // A control with no accessible name is unusable by screen readers and gives no hint on hover.
    const toggle = queryFirst(".o_main_navbar .o_menu_toggle");
    expect(toggle.getAttribute("aria-label")).toMatch(/\S/);
    expect(toggle.getAttribute("title")).toMatch(/\S/);
    // The desktop button must stay absent here: one control per action on a phone.
    expect(".o_grid_apps_menu__button").toHaveCount(0);
});

test("with the grid closed, tapping the grid icon opens the sidebar", async () => {
    await openSidebar();

    // Opening the sidebar must not ask the app grid to do anything.
    expect(".app-menu-container").toHaveCount(0);
    expect.verifySteps([]);
});

test("tapping the grid icon while the apps grid is open closes the grid and does not open the sidebar", async () => {
    await openSidebar({ withScreen: true });
    await contains(".o_sidebar_topbar a.btn-primary", BODY).click();
    await animationFrame();
    // Control: the grid is open over the screen the user came from.
    expect(".app-menu-container").toHaveCount(1);
    expect(".apps_menu_mobile_target_action").toHaveCount(1);

    await contains(".o_main_navbar .o_menu_toggle").click();
    await animationFrame();

    expect(".app-menu-container").toHaveCount(0);
    expect(inBody(".o_app_menu_sidebar")).toHaveCount(0);
    // The user is back on the screen they came from.
    expect(".apps_menu_mobile_target_action").toHaveCount(1);
    expect(".o_main_navbar .o_menu_toggle").toHaveCount(1);

    // Once the grid is gone the icon is the sidebar toggle again.
    await contains(".o_main_navbar .o_menu_toggle").click();
    expect(inBody(".o_app_menu_sidebar")).toHaveCount(1);
    expect.verifySteps(["toggleMenu:true", "toggleMenu:undefined"]);
});

test("tapping the grid icon while the apps grid is the only screen opens the sidebar and keeps the grid", async () => {
    await mountWithCleanup(WebClient);
    // Nothing is mounted behind the grid, as when the menu is the boot screen.
    await getService("apps_menu").toggleMenu(true);
    await animationFrame();
    expect(".app-menu-container").toHaveCount(1);
    expect(".o_action").toHaveCount(0);
    patchWithCleanup(getService("apps_menu"), {
        toggleMenu(openState) {
            expect.step(`toggleMenu:${openState}`);
            return super.toggleMenu(openState);
        },
    });

    await contains(".o_main_navbar .o_menu_toggle").click();
    await animationFrame();

    // Closing it would leave a blank page: the sidebar opens over the grid instead.
    expect(inBody(".o_app_menu_sidebar")).toHaveCount(1);
    expect(".app-menu-container").toHaveCount(1);
    expect.verifySteps([]);
});

test("tapping the grid icon while the menu action is the only screen opens the sidebar and keeps the grid", async () => {
    await mountWithCleanup(WebClient);
    // The "menu" action mounted directly, with nothing under it on the action stack.
    await getService("action").doAction("menu");
    await animationFrame();
    expect(".app-menu-container").toHaveCount(1);
    expect(getService("action").currentController.config.breadcrumbs).toEqual([]);

    await contains(".o_main_navbar .o_menu_toggle").click();
    await animationFrame();

    expect(inBody(".o_app_menu_sidebar")).toHaveCount(1);
    expect(".app-menu-container").toHaveCount(1);
});

test("tapping All Apps in the sidebar closes it and opens the full-screen app grid with search", async () => {
    await openSidebar();

    await contains(".o_sidebar_topbar a.btn-primary", BODY).click();
    await animationFrame();

    expect(inBody(".o_app_menu_sidebar")).toHaveCount(0);
    expect(".app-menu-container").toHaveCount(1);
    expect(".app-menu-container .search-input input").toHaveCount(1);
    // Both apps are offered as tiles.
    expect(".app-menu-container .o-app-menu-item:contains(MobileTargetApp)").toHaveCount(1);
    expect(".app-menu-container .o-app-menu-item:contains(OtherApp)").toHaveCount(1);
    // One tap asks the grid to open exactly once.
    expect.verifySteps(["toggleMenu:true"]);
});

test("typing in the app grid search filters to matching apps and choosing a result opens it", async () => {
    await openSidebar();
    await contains(".o_sidebar_topbar a.btn-primary", BODY).click();
    await animationFrame();

    await contains(".app-menu-container .search-input input").edit("MobileTarget", {
        confirm: false,
    });
    // _searchMenus is debounced 200ms (menu_canonical_searchbar/searchbar.esm.js).
    await advanceTime(200);
    await animationFrame();

    // Only the app matching the query is offered, not the other one.
    expect(".app-menu-container .search-item__link").toHaveCount(1);
    expect(".app-menu-container .search-item__link").toHaveText("MobileTargetApp");

    await contains(".app-menu-container .search-item__link").click();
    await animationFrame();
    await animationFrame();

    expect(".apps_menu_mobile_target_action").toHaveText("MobileTargetApp");
    expect(".app-menu-container").toHaveCount(0);
    expect.verifySteps(["toggleMenu:true"]);
});

test("choosing an app tile in the grid opened from the sidebar opens it and closes the grid", async () => {
    await openSidebar();
    await contains(".o_sidebar_topbar a.btn-primary", BODY).click();
    await animationFrame();
    expect(".app-menu-container").toHaveCount(1);

    await contains(".app-menu-container .o-app-menu-item:contains(MobileTargetApp)").click();
    await animationFrame();
    await animationFrame();

    expect(".apps_menu_mobile_target_action").toHaveText("MobileTargetApp");
    expect(".app-menu-container").toHaveCount(0);
    expect.verifySteps(["toggleMenu:true"]);
});

test("the grid opened from the sidebar is the screen third-party patches of AppsMenuAction reach", async () => {
    patchWithCleanup(AppsMenuAction.prototype, {
        setup() {
            super.setup();
            expect.step("apps-menu-action-patch-reached-the-mounted-screen");
        },
    });
    await openSidebar();

    await contains(".o_sidebar_topbar a.btn-primary", BODY).click();
    await animationFrame();

    expect(".app-menu-container").toHaveCount(1);
    expect.verifySteps([
        "toggleMenu:true",
        "apps-menu-action-patch-reached-the-mounted-screen",
    ]);
});

test("the apps sidebar slides in from the left edge and a left swipe closes it", async () => {
    await openSidebar();

    // Core anchors a left-sliding sidebar with `end-100` (translated into view from the left);
    // `start-100` would anchor it to the right edge.
    const sidebar = queryFirst(".o_app_menu_sidebar", BODY);
    expect(sidebar).toHaveClass("end-100");
    expect(sidebar).not.toHaveClass("start-100");

    const touch = (clientX) =>
        new Touch({ identifier: 0, target: sidebar, clientX, clientY: 100 });

    // A right swipe moves away from the left edge: the sidebar stays.
    await dispatch(sidebar, "touchstart", { changedTouches: [touch(100)] });
    await dispatch(sidebar, "touchend", { changedTouches: [touch(250)] });
    await animationFrame();
    expect(inBody(".o_app_menu_sidebar")).toHaveCount(1);

    // A left swipe of at least 100px dismisses it.
    await dispatch(sidebar, "touchstart", { changedTouches: [touch(300)] });
    await dispatch(sidebar, "touchend", { changedTouches: [touch(150)] });
    await animationFrame();
    expect(inBody(".o_app_menu_sidebar")).toHaveCount(0);
});

test("the user (burger) menu has no extra apps sidebar button", async () => {
    await mountWithCleanup(WebClient);

    // Only core's own avatar toggle remains in the systray.
    expect(inBody(".o_mobile_menu_toggle")).toHaveCount(1);
    expect(inBody(".oi-panel-right")).toHaveCount(0);

    await contains(".o_mobile_menu_toggle", BODY).click();
    await animationFrame();

    expect(inBody(".o_burger_menu")).toHaveCount(1);
    expect(inBody(".oi-panel-right")).toHaveCount(0);
});
