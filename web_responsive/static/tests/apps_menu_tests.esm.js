/** @odoo-module **/
/* eslint init-declarations: "warn" */
/* Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { click, getFixture, mount, nextTick, patchWithCleanup } from "@web/../tests/helpers/utils";
import { makeTestEnv } from "@web/../tests/helpers/mock_env";
import { actionService } from "@web/webclient/actions/action_service";
import { browser } from "@web/core/browser/browser";
import { menuService } from "@web/webclient/menus/menu_service";
import { notificationService } from "@web/core/notifications/notification_service";
import { NavBar } from "@web/webclient/navbar/navbar";
import { registry } from "@web/core/registry";
import { hotkeyService } from "@web/core/hotkeys/hotkey_service";
import { uiService } from "@web/core/ui/ui_service";
import {
    AppsMenuAction,
    appsMenuService,
} from "@web_responsive/components/apps_menu/apps_menu_service";

const serviceRegistry = registry.category("services");

let baseConfig = {};
let target = "";

/**
 * The apps menu is no longer a dropdown living inside the NavBar: the navbar
 * button asks the apps_menu service to toggle a client action ("apps_menu",
 * AppsMenuAction) that renders the fullscreen menu. The tests therefore
 * exercise three seams:
 *  - the NavBar button provided by our web.NavBar.AppsMenu extension,
 *  - the apps_menu service toggling (doAction / restore),
 *  - the AppsMenuAction rendering (menu items, active app).
 */
QUnit.module("AppsMenu", {
    async beforeEach() {
        target = getFixture();
        serviceRegistry.add("menu", menuService);
        serviceRegistry.add("action", actionService);
        serviceRegistry.add("notification", notificationService);
        serviceRegistry.add("hotkey", hotkeyService);
        serviceRegistry.add("ui", uiService);
        serviceRegistry.add("apps_menu", appsMenuService);
        patchWithCleanup(browser, {
            setTimeout: (handler, delay, ...args) => handler(...args),
            clearTimeout: () => undefined,
        });
        const menus = {
            root: { id: "root", children: [1, 2], name: "root", appID: "root" },
            1: { id: 1, children: [], name: "App0", appID: 1, xmlid: "menu_1" },
            2: { id: 2, children: [], name: "App1", appID: 2, xmlid: "menu_2" },
        };
        const serverData = { menus };
        baseConfig = { serverData, config: { breadcrumbs: [] } };
    },
});

QUnit.test("can be rendered", async (assert) => {
    const env = await makeTestEnv(baseConfig);
    await mount(NavBar, target, { env });
    assert.containsOnce(target, "button.o_grid_apps_menu__button", "1 apps menu button present");
});

QUnit.test("can be opened and closed", async (assert) => {
    // The button toggles the fullscreen menu through the apps_menu service:
    // opening runs the "apps_menu" client action, closing restores the
    // previous controller. Track both through a mocked action service.
    serviceRegistry.add(
        "action",
        {
            start() {
                return {
                    doAction(action) {
                        assert.step(`do-action:${action.tag}`);
                        return Promise.resolve();
                    },
                    restore() {
                        assert.step("restore");
                        return Promise.resolve();
                    },
                };
            },
        },
        { force: true }
    );
    const env = await makeTestEnv(baseConfig);
    await mount(NavBar, target, { env });
    await click(target, "button.o_grid_apps_menu__button");
    await nextTick();
    assert.verifySteps(["do-action:apps_menu"], "first click opens the apps menu action");
    // Simulate the AppsMenuAction being mounted (it signals its open state).
    env.bus.trigger("APPS_MENU:ACT:TOGGLE", true);
    await click(target, "button.o_grid_apps_menu__button");
    await nextTick();
    assert.verifySteps(["restore"], "second click leaves the apps menu action");
});

QUnit.test("can be active", async (assert) => {
    const env = await makeTestEnv(baseConfig);
    // The AppsMenuAction is remounted every time the menu opens, so the
    // current app at mount time must be flagged as active.
    env.services.menu.setCurrentMenu(1);
    await mount(AppsMenuAction, target, {
        env,
        props: { action: {}, className: "" },
    });
    await nextTick();
    assert.containsOnce(target, '.o-app-menu-item.active[data-menu-xmlid="menu_1"]');
    assert.containsNone(target, '.o-app-menu-item.active[data-menu-xmlid="menu_2"]');
});
