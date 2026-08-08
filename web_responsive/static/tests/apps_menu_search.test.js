/** @odoo-module **/
/* Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import { defineMenus, mountWithCleanup } from "@web/../tests/web_test_helpers";
import { AppsMenuAction } from "@web_responsive/components/apps_menu/apps_menu_service";

// Re-implementation of the QUnit suite retired by 8069ccc (apps_menu_search_tests.esm.js).
// Real transition: mount the actual fullscreen client action (never a hand-seeded DOM) and let its
// own useEffect open the container (apps_menu_service.js:27-31 triggers "APPS_MENU:TOGGLE", which
// AppsMenu.setup() subscribes to - apps_menu.esm.js:43-45), then read the real rendered DOM.
test("the search input renders exactly once inside the fullscreen apps-menu container", async () => {
    defineMenus([{ id: 1, name: "App One" }]);

    await mountWithCleanup(AppsMenuAction, {
        props: {
            action: { id: 1, tag: "menu", target: "current", type: "ir.actions.client" },
            actionId: 1,
        },
    });
    await animationFrame();

    expect(".app-menu-container .search-input").toHaveCount(1);
});
