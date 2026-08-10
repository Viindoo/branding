/** @odoo-module **/
/* Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import {
    contains,
    defineMenus,
    getService,
    makeMockEnv,
    mockService,
    mountWithCleanup,
} from "@web/../tests/web_test_helpers";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { NavBar } from "@web/webclient/navbar/navbar";
import { WebClient } from "@web/webclient/webclient";
// Importing AppsMenuAction also runs apps_menu.esm.js's module-level side effects (the NavBar/
// BurgerMenu patches, AppMenuItem, AppsMenuSearchBar registration) because apps_menu_service.js
// imports apps_menu.esm.js itself - so this file's import graph alone is enough to exercise the
// real production wiring, independent of the shared Hoot bundle's own load order.
import { AppsMenuAction } from "@web_responsive/components/apps_menu/apps_menu_service";

// Re-implementation of the QUnit suite retired by 8069ccc (apps_menu_tests.esm.js): at 18.0 the
// apps menu is no longer a NavBar dropdown (.o-app-menu-list) but a fullscreen client action
// (AppsMenuAction) opened through the "apps_menu" service - apps_menu_service.js. Every test below
// drives the real production path (click the actual button, mount the actual action); none
// hand-seeds a terminal DOM state.
//
// THE TRAP (design doc §Q4.1). At 18.0 AppsMenuAction is registered under actions tag "menu", not
// "apps_menu" (apps_menu_service.js:100), and appsMenuService.toggleMenu() calls
// env.services.action.doAction("menu") with a BARE STRING, not an action object
// (apps_menu_service.js:88). A literal port of the 17.0 assertion
// `assert.step(`do-action:${action.tag}`)` would read `.tag` off a STRING, get `undefined`, and
// record "do-action:undefined" - a green test asserting nothing. The tests below step on the
// argument itself and expect the literal string "menu".

// web_responsive depends on `mail`, so mail patches NavBar (and the WebClient systray) with
// components that reach for mail's own server models. Without mail's mock models registered, the
// very first mount aborts with `Cannot find a definition for model "discuss.channel"` and every
// test in this file fails for a harness reason instead of a business one. Core's own convention
// for this is a module-level defineMailModels() call - see
// addons/base_automation/static/tests/kanban_header_patch.test.js and board/.../add_to_dashboard.test.js.
defineMailModels();

/**
 * `env.config` as the real action service would supply it to a mounted action
 * (action_service.js:828-829, `controller.config.breadcrumbs = reactive(...)`). A bare
 * `mountWithCleanup(AppsMenuAction, {props})` has no `env.config` at all, and
 * AppsMenuAction.setup() unconditionally reads `this.env.config.breadcrumbs.length`
 * (apps_menu_service.js:35), so mounting it directly without this crashes Owl's root on every
 * mount. `componentEnv` is 18.0 core's own mechanism for this exact situation - core's
 * `mountView()` test helper supplies `env.config` the identical way when mounting a View directly
 * instead of through the action service (view_test_helpers.js:228-232:
 * `componentEnv: { config: params.config }`).
 */
const APPS_MENU_ACTION_ENV = { config: { breadcrumbs: [] } };

/**
 * A fully-populated `standardActionServiceProps` object (@web/webclient/actions/action_service),
 * so AppsMenuAction is mounted exactly the way the real action service would mount it.
 */
function makeActionProps() {
    return {
        action: { id: 1, tag: "menu", target: "current", type: "ir.actions.client" },
        actionId: 1,
        className: "o_action_menu",
        globalState: {},
        state: {},
        resId: false,
        updateActionState: () => {},
    };
}

test.tags("desktop");
test("clicking the navbar apps button while the menu is closed opens the apps-menu client action", async () => {
    defineMenus([{ id: 1 }]);
    mockService("action", {
        doAction(action) {
            expect.step(action);
        },
    });

    await mountWithCleanup(NavBar);
    await contains("button.o_grid_apps_menu__button").click();

    expect.verifySteps(["menu"]);
});

test.tags("desktop");
test(
    "clicking the navbar apps button while the menu is open restores the previous controller " +
        "instead of opening it a second time",
    async () => {
        defineMenus([{ id: 1 }]);
        mockService("action", {
            doAction(action) {
                expect.step(action);
            },
            restore() {
                expect.step("restore");
            },
        });
        await makeMockEnv();
        // Drive the real "apps_menu" service into the open state exactly the way AppsMenuAction's
        // own setup() does on mount (apps_menu_service.js:29), rather than reaching into a private
        // flag.
        getService("apps_menu").setOpen(true);

        await mountWithCleanup(NavBar);
        await contains("button.o_grid_apps_menu__button").click();

        expect.verifySteps(["restore"]);
    }
);

test("mounting the apps menu flags exactly the current app as active, and no other app", async () => {
    defineMenus([
        { id: 1, name: "App One", xmlid: "menu_app_one" },
        { id: 2, name: "App Two", xmlid: "menu_app_two" },
    ]);
    await makeMockEnv();
    getService("menu").setCurrentMenu(1);

    await mountWithCleanup(AppsMenuAction, {
        props: makeActionProps(),
        componentEnv: APPS_MENU_ACTION_ENV,
    });
    await animationFrame();

    expect(".o-app-menu-item.active").toHaveCount(1);
    expect(".o-app-menu-item.active[data-menu-xmlid='menu_app_one']").toHaveCount(1);
});

test(
    "AppsMenuAction declares the full action-service props contract so the action service can " +
        "mount it",
    async () => {
        // The observable contract: 8069ccc added `static props = {...standardActionServiceProps}`
        // (apps_menu_service.js:21) so Owl's "component has no static props description" dev-mode
        // warning stops firing on every tour that opens the menu. Hoot's mount helper forces
        // `dev: false` (component_test_helpers.js), so a missing/narrowed schema would neither
        // throw nor warn here - asserting the declared schema itself is the only way to actually
        // protect the contract.
        expect(AppsMenuAction.props).toEqual(standardActionServiceProps);

        // Companion control: also prove the schema is not merely declared but actually mountable
        // with a fully-populated props object.
        defineMenus([{ id: 1 }]);
        await mountWithCleanup(AppsMenuAction, {
            props: makeActionProps(),
            componentEnv: APPS_MENU_ACTION_ENV,
        });
        await animationFrame();

        expect(".o_grid_apps_menu").toHaveCount(1);
    }
);

test("opening the apps menu pushes no breadcrumb", async () => {
    // web_responsive is the sole owner of the "menu" actions tag at 18.0 (a repo-wide grep for
    // `actions").add("menu"` over CE core is empty). Core's action service special-cases exactly
    // that tag: _getBreadcrumbs keeps only controllers whose action.tag !== "menu"
    // (action_service.js:449), so a controller stack containing only the apps-menu action yields
    // an empty breadcrumb trail. Go through the real action service, not a hand-seeded env.config -
    // unlike the two tests above, this one never touches APPS_MENU_ACTION_ENV: the breadcrumbs
    // array asserted below is the REAL one action_service.js computes from _getBreadcrumbs(), not
    // one this file supplied, so the assertion stays non-trivial.
    defineMenus([{ id: 1 }]);
    await mountWithCleanup(WebClient);
    await getService("action").doAction("menu");

    expect(getService("action").currentController.config.breadcrumbs).toEqual([]);
});
