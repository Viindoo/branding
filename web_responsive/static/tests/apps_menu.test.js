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
import { router } from "@web/core/browser/router";
import { session } from "@web/session";
import { AppsMenu } from "@web_responsive/components/apps_menu/apps_menu.esm";
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
test("the app grid is present in the same render cycle the menu reports itself open", async () => {
    // Root-cause regression test (apps_menu.esm.js AppsMenu.setup()/setOpenState): `state.open`
    // must be correct on the component's FIRST render, so `.app-menu-container` (t-if="state.open",
    // apps_menu.xml:52) appears in the same render cycle as `.o_grid_apps_menu` (the element
    // AppsMenu always renders, unconditionally, the moment it mounts). Deliberately NO extra
    // animationFrame() call after toggleMenu(true) resolves - inserting one would give the buggy
    // two-render-cycle path (mount closed, then a bus round trip flips it open) enough time to
    // finish and hide exactly the ~20ms empty-overlay flash this test exists to forbid.
    defineMenus([{ id: 1 }]);
    await mountWithCleanup(WebClient);

    expect(".o_grid_apps_menu").toHaveCount(0);
    expect(".app-menu-container").toHaveCount(0);

    await getService("apps_menu").toggleMenu(true);

    expect(".o_grid_apps_menu").toHaveCount(1);
    expect(".app-menu-container").toHaveCount(1);
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

test.tags("desktop");
test("clicking the navbar apps button dismisses the menu action too, not only the overlay", async () => {
    // AppsMenuAction is registered under the "menu" actions tag (apps_menu_service.js), so it can
    // be reached via doAction("menu") directly - a client-action URL, the boot fallback, or (proven
    // live) erponline-enterprise18/viin_customizer_web_responsive's bridge module, which patches
    // CustomizerViewStore._getPageAction to return {type: "ir.actions.client", tag: "menu"} and
    // dispatches it via its own isolated action service - WITHOUT ever going through
    // appsMenuService.openMenu() (the overlay path). AppsMenuScreen.setup()'s useEffect still
    // unconditionally calls appsMenu.setOpen(true) on mount regardless of which presentation
    // mounted it, so the toggle button must be able to dismiss THIS presentation too, not only the
    // overlay one - otherwise it goes silently dead (verified: clicks do nothing) the moment
    // anything mounts "menu" without going through toggleMenu()/openMenu() first.
    defineMenus([{ id: 1 }]);
    await mountWithCleanup(WebClient);
    await getService("action").doAction(1);

    expect(".o_list_view").toHaveCount(1);
    expect(".app-menu-container").toHaveCount(0);

    // Mount the "menu" action directly through the real action service - not through
    // getService("apps_menu").toggleMenu(true) - to land in exactly the buggy state
    // (isOpening=true, removeOverlay=null).
    await getService("action").doAction("menu");
    await animationFrame();
    expect(".app-menu-container").toHaveCount(1);

    await contains("button.o_grid_apps_menu__button").click();
    await animationFrame();

    // The button must actually dismiss the menu action and return the user to the screen they
    // were on before - not sit there as a dead no-op.
    expect(".app-menu-container").toHaveCount(0);
    expect(".o_list_view").toHaveCount(1);
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

    // ...and it is the ONLY apps control on a small screen. apps_menu.xml's own comment states
    // the intent as one-or-the-other ("Rebuild the anchor here, ON THE BRANCH THAT DOES
    // RENDER"), but the `<button class="o_grid_apps_menu__button">` is written as a SIBLING of
    // the `t-if`/`t-else` pair rather than inside the `t-else`, so it renders in BOTH branches
    // and a phone gets two controls for one action. This is not cosmetic: the extra button is
    // an unshrinkable (`flex-shrink:0`) child of a 375px navbar whose ONLY shrinkable sibling is
    // `.o_breadcrumb`, so every pixel the duplicate occupies is taken from the breadcrumb - the
    // element a tour's `:visible` filter must find. Measured live at 375x667 on
    // /odoo/action-mrp.mrp_bom_form_action/1: without this module 1 control and
    // `.o_last_breadcrumb_item.active` 149.9px wide (visible); with it 2 controls and that same
    // element 0px wide (NOT visible), which is what hangs the tour until its 20s watchdog fires.
    expect(".o_grid_apps_menu__button").toHaveCount(0);
});

test("on a wide screen the navbar offers the home-menu grid button instead of the mobile toggle", async () => {
    // The other half of the one-or-the-other contract, and the reason the assertion above cannot
    // be satisfied by simply deleting the button: on a wide screen the grid button IS the apps
    // control, and the `.o_menu_toggle` anchor - which core renders only in its small-screen
    // branch - must NOT be there. Without this test, moving the button inside the `t-else` and
    // moving it out of the template altogether look identical to the suite.
    defineMenus([{ id: 1 }]);
    await makeMockEnv();
    // Pinned explicitly rather than left to the ambient viewport, for the same reason the
    // small-screen test above pins it: this contract then holds in BOTH the desktop and the
    // mobile Hoot preset runs, instead of only in whichever one the runner happens to execute.
    patchWithCleanup(getService("ui"), { isSmall: false });

    await mountWithCleanup(NavBar);

    expect(".o_main_navbar .o_grid_apps_menu__button").toHaveCount(1);
    expect(".o_main_navbar .o_menu_toggle").toHaveCount(0);
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

test("the is_redirect_home branch never overrides the open prop AppsMenuScreen always passes", async () => {
    // migrations/18.0.1.0.8/post-migration.py backfills is_redirect_home=True for every upgraded
    // user with no action_id - the DOMINANT configuration on a real (upgraded) database, not an
    // edge case. AppsMenuScreen's template always passes open="true" to <AppsMenu> (apps_menu.xml,
    // the only instantiation site in this module), specifically so `.app-menu-container`
    // (t-if="state.open") appears in the SAME render cycle the screen mounts (66a6a7d65d) - no
    // waiting for AppsMenuScreen's mounted-effect to correct it a frame later over the
    // APPS_MENU:TOGGLE bus. THAT bus correction is exactly what would otherwise mask this test: it
    // fires unconditionally on every mount through AppsMenuScreen and overwrites state.open to true
    // regardless of what this branch computed, so mounting AppsMenu through its usual parent cannot
    // observe the branch's OWN construction-time value. Mount AppsMenu standalone instead - no
    // AppsMenuScreen wrapper, so nothing ever corrects it - and read the DOM AppsMenu itself commits
    // on construction, which is exactly what a real first paint would show.
    patchWithCleanup(session, {apps_menu: {is_redirect_home: true}});
    patchWithCleanup(router, {current: {menu_id: "5"}});

    await makeMockEnv();
    await mountWithCleanup(AppsMenu, {props: {open: true}});

    expect(".app-menu-container").toHaveCount(1);
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
