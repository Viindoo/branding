/** @odoo-module **/
/* eslint init-declarations: "warn" */
/* Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { getFixture, mount, nextTick, patchWithCleanup } from "@web/../tests/helpers/utils";
import { makeTestEnv } from "@web/../tests/helpers/mock_env";
import { actionService } from "@web/webclient/actions/action_service";
import { browser } from "@web/core/browser/browser";
import { menuService } from "@web/webclient/menus/menu_service";
import { notificationService } from "@web/core/notifications/notification_service";
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

QUnit.module("AppsMenu Search", {
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
    // The search bar lives inside the fullscreen apps menu client action
    // (the menu is no longer a NavBar dropdown).
    await mount(AppsMenuAction, target, {
        env,
        props: { action: {}, className: "" },
    });
    // The open state is signalled on the bus after mount; wait a tick for the
    // AppsMenu wrapper to render its container.
    await nextTick();
    assert.containsOnce(target, ".app-menu-container .search-input");
});
