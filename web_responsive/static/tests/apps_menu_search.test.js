/** @odoo-module **/
/* Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { defineMenus, mountWithCleanup } from "@web/../tests/web_test_helpers";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";
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
