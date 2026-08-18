/** @odoo-module **/
/* Copyright 2023 Taras Shabaranskyi
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import { expect, test } from "@odoo/hoot";
import { animationFrame } from "@odoo/hoot-mock";
import {
    contains,
    defineActions,
    defineMenus,
    defineModels,
    getService,
    makeMockEnv,
    models,
    mountWithCleanup,
    onRpc,
    patchWithCleanup,
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
// "apps_menu" (apps_menu_service.js:100), and appsMenuService.toggleMenu() historically called
// env.services.action.doAction("menu") with a BARE STRING, not an action object. A literal port of
// the 17.0 assertion `assert.step(`do-action:${action.tag}`)` would read `.tag` off a STRING, get
// `undefined`, and record "do-action:undefined" - a green test asserting nothing.
//
// This suite no longer steps on the doAction argument at all. Stepping on it pinned the MECHANISM
// (an action-stack push) rather than the RULE, and that mechanism is itself the defect the
// "keeps the current view mounted" tests below exist to forbid: AppsMenuAction declares
// `static target = "current"`, so pushing it REPLACES the mounted controller and destroys the
// screen the user was looking at. Tests that pinned doAction would have had to be deleted to fix
// the bug - so they are re-expressed here against the observable outcome (the home menu is
// presented / dismissed) and now survive any correct implementation.

// web_responsive depends on `mail`, so mail patches NavBar (and the WebClient systray) with
// components that reach for mail's own server models. Without mail's mock models registered, the
// very first mount aborts with `Cannot find a definition for model "discuss.channel"` and every
// test in this file fails for a harness reason instead of a business one. Core's own convention
// for this is a module-level defineMailModels() call - see
// addons/base_automation/static/tests/kanban_header_patch.test.js and board/.../add_to_dashboard.test.js.
defineMailModels();

/**
 * A record + list view for the screen the home menu must NOT destroy. The "underlying view
 * survives" rule is only observable against a REAL mounted controller, so this suite opens a real
 * act_window action rather than asserting against a hand-seeded DOM. Shape copied from core's own
 * client_action.test.js fixture (addons/web/static/tests/webclient/actions/client_action.test.js).
 */
class AppsMenuUnderlying extends models.Model {
    _name = "apps.menu.underlying";
    _rec_name = "display_name";

    _records = [{ id: 1, display_name: "A record the home menu must not destroy" }];

    _views = {
        list: /* xml */ `
            <list>
                <field name="display_name"/>
            </list>
        `,
    };
}

defineModels([AppsMenuUnderlying]);

defineActions([
    {
        id: 1,
        xml_id: "action_apps_menu_underlying",
        name: "Underlying Screen",
        res_model: "apps.menu.underlying",
        views: [[false, "list"]],
    },
]);

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
test("clicking the navbar apps button presents the home menu", async () => {
    defineMenus([{ id: 1 }]);
    await mountWithCleanup(WebClient);

    // Control: the menu is not already on screen, so the assertion after the click cannot pass
    // for free.
    expect(".app-menu-container").toHaveCount(0);

    await contains("button.o_grid_apps_menu__button").click();

    // `.app-menu-container` is rendered under `t-if="state.open"` (apps_menu.xml:36), so it is
    // present only while the menu is actually open - not merely mounted.
    expect(".app-menu-container").toHaveCount(1);
});

test.tags("desktop");
test("clicking the navbar apps button while the home menu is open dismisses it", async () => {
    defineMenus([{ id: 1 }]);
    await mountWithCleanup(WebClient);
    await getService("action").doAction(1);

    await contains("button.o_grid_apps_menu__button").click();
    expect(".app-menu-container").toHaveCount(1);

    await contains("button.o_grid_apps_menu__button").click();

    // The second click closes the menu rather than presenting it a second time, and the screen the
    // user came from is what they are left looking at.
    expect(".app-menu-container").toHaveCount(0);
    expect(".o_list_view").toHaveCount(1);
});

test.tags("desktop");
test("opening the home menu keeps the current view mounted", async () => {
    defineMenus([{ id: 1 }]);
    await mountWithCleanup(WebClient);
    await getService("action").doAction(1);

    // The screen the user is on before touching the home menu.
    expect(".o_control_panel").toHaveCount(1);
    expect(".o_list_view").toHaveCount(1);

    await getService("apps_menu").toggleMenu(true);
    await animationFrame();

    // The menu is presented...
    expect(".app-menu-container").toHaveCount(1);
    // ...as an OVERLAY: the screen it opened over is still mounted underneath it. Opening a menu
    // must never destroy the user's current screen.
    expect(".o_control_panel").toHaveCount(1);
    expect(".o_list_view").toHaveCount(1);
});

test.tags("desktop");
test("closing the home menu returns to the same screen without refetching it", async () => {
    onRpc("web_search_read", () => {
        expect.step("web_search_read");
    });
    defineMenus([{ id: 1 }]);
    await mountWithCleanup(WebClient);
    await getService("action").doAction(1);

    // Loading the screen the first time legitimately reads its records.
    expect.verifySteps(["web_search_read"]);

    await getService("apps_menu").toggleMenu(true);
    await animationFrame();
    await getService("apps_menu").toggleMenu(false);
    await animationFrame();

    expect(".app-menu-container").toHaveCount(0);
    expect(".o_list_view").toHaveCount(1);
    // The view was never torn down, so coming back to it costs no round trip. A refetch here is
    // the signature of the controller having been destroyed and rebuilt.
    expect.verifySteps([]);
});

test("the navbar keeps the menu-toggle anchor that core tours click", async () => {
    defineMenus([{ id: 1 }]);
    await makeMockEnv();
    // Core renders `<a class="o_menu_toggle">` only inside the small-screen branch of
    // web.NavBar.AppsMenu (web/static/src/webclient/navbar/navbar.xml:77). `ui.isSmall` is a plain
    // reactive property (web/static/src/core/ui/ui_service.js:213), so forcing it here pins the
    // small-screen contract without depending on which Hoot preset the runner happens to execute -
    // this test protects the mobile contract even in the desktop run.
    patchWithCleanup(getService("ui"), { isSmall: true });

    await mountWithCleanup(NavBar);

    // The trigger core's own mobile tours reach for - `main_flow_tour` clicks
    // `.o_main_navbar .o_menu_toggle` at step 1 of 311. An inherit that removes it from the DOM
    // silently breaks every such tour at its first step.
    expect(".o_main_navbar .o_menu_toggle").toHaveCount(1);
});

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

test.tags("desktop");
test("a module that patches the apps menu reaches the menu the user actually opens", async () => {
    // Real, shipped shape of the third-party pattern this test protects
    // (erponline-enterprise/viin_customizer_web_responsive): a module imports AppsMenuAction and
    // patches its prototype with an overridden setup() that calls super.setup(), the same way it
    // patches getAppCreatorItem()/openAppCreator() to back a template it also extends:
    //     import { AppsMenuAction } from "@web_responsive/components/apps_menu/apps_menu_service";
    //     patch(AppsMenuAction.prototype, {
    //         setup() { super.setup(); this.isCustomizer = odoo.customizer; },
    //         getAppCreatorItem() { ... },
    //     });
    // setup() is used as the marker here (instead of a bespoke method the template never calls)
    // because Owl guarantees it runs exactly once, synchronously, for ANY instance that mounts -
    // so recording a step from it observes the prototype surface of whatever actually renders the
    // screen, without this test asserting anything about that class's name or its place in the
    // prototype graph (no `instanceof`, no class-shape assertion).
    patchWithCleanup(AppsMenuAction.prototype, {
        setup() {
            super.setup();
            expect.step("apps-menu-action-patch-reached-the-mounted-screen");
        },
    });

    defineMenus([{ id: 1 }]);
    await mountWithCleanup(WebClient);

    // Control: the menu is not already on screen and the patch has not fired yet, so the
    // assertions after opening it cannot pass for free.
    expect(".app-menu-container").toHaveCount(0);
    expect.verifySteps([]);

    // Drive the exact path a user takes to open the menu - the "apps_menu" service, not a direct
    // instantiation of any class - because the regression this protects is precisely that this
    // path can reach a class the patch never touched.
    await getService("apps_menu").toggleMenu(true);
    await animationFrame();

    // The menu really did open...
    expect(".app-menu-container").toHaveCount(1);
    // ...and the screen the user is looking at carries the same prototype surface a third party
    // patches onto AppsMenuAction. A module that extends web_responsive.AppsMenuAction's template
    // to call a method it added via this exact patch pattern must find that method on whatever
    // renders the template for the user - not only on one of several presentations of it.
    expect.verifySteps(["apps-menu-action-patch-reached-the-mounted-screen"]);
});
