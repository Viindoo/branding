/** @odoo-module **/

import { animationFrame, describe, expect, test } from "@odoo/hoot";
import { Deferred } from "@odoo/hoot-mock";
import { queryAll } from "@odoo/hoot-dom";
import {
    contains,
    defineActions,
    defineMenus,
    defineModels,
    fields,
    getService,
    models,
    mountWebClient,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { redirect } from "@web/core/utils/urls";
import { config as transitionConfig } from "@web/core/transition";

// Business rule: on a phone a backend user reaches the full-screen app menu WITH SEARCH
// (ViinHomeMenu) from the apps sidebar, and the toggle that opens the sidebar is named for
// assistive technology. The toggle also puts the home menu away again when it covers a screen,
// and opens the sidebar - keeping the home menu - when the home menu IS the screen (boot landing).
//
// Forward-ported intent of 18.0 web_responsive 16b8087 ("make the mobile apps menu one-handed");
// web_responsive no longer exists at 19.0, so the target is the theme's own ViinHomeMenu.
//
// Every assertion is on observable DOM: which surfaces are present, the toggle's accessible name,
// and which app the menu service was asked to open - never on a component internal.

defineMailModels();

class MobileGadget extends models.Model {
    _name = "mobile.menu.gadget";

    name = fields.Char({ string: "Name" });

    _records = [{ id: 1, name: "Gadget" }];

    _views = {
        list: `<list><field name="name"/></list>`,
        form: `<form><sheet><field name="name"/></sheet></form>`,
        search: `<search/>`,
    };
}

defineModels([MobileGadget]);
defineActions([
    {
        id: 9401,
        xml_id: "mobile_menu_gadget_action",
        name: "Gadgets",
        type: "ir.actions.act_window",
        res_model: "mobile.menu.gadget",
        views: [[false, "list"]],
    },
]);
defineMenus([
    { id: 9402, appID: 9402, name: "Alpha Gadgets", xmlid: "app.alpha", actionID: 9401 },
    { id: 9403, appID: 9403, name: "Bravo Widgets", xmlid: "app.bravo", actionID: 9401 },
]);

const IN_BODY = { root: document.body };

/** Mount the webclient on the Gadgets screen (a real screen, nothing of the theme open). */
async function mountOnScreen() {
    patchWithCleanup(transitionConfig, { disabled: true });
    onRpc("mail.activity", "search_count", () => 0);
    onRpc("res.users", "read", () => [{ viin_home_app_order: false }]);
    redirect("/odoo/action-9401");
    await mountWebClient();
    await animationFrame();
    expect(".o_action_manager .o_list_view").toHaveCount(1, {
        message: "the test needs a real screen to stand on",
    });
}

/** Mount the webclient on the boot landing: no action in the URL -> the home menu IS the screen. */
async function mountOnBootLanding() {
    patchWithCleanup(transitionConfig, { disabled: true });
    onRpc("mail.activity", "search_count", () => 0);
    onRpc("res.users", "read", () => [{ viin_home_app_order: false }]);
    redirect("/odoo");
    await mountWebClient();
    await animationFrame();
    expect(".o_action_manager .o_viin_home_menu:not(.o_viin_home_overlay)").toHaveCount(1, {
        message: "the home menu must be the boot landing for this test to mean anything",
    });
}

async function tapAllApps() {
    await contains(".o_app_menu_sidebar a.btn-primary", IN_BODY).click();
    await animationFrame();
}

describe("mobile apps menu", () => {
    test.tags("mobile");
    test("the apps toggle is named for assistive technology and keeps its bars icon", async () => {
        await mountOnScreen();

        expect(".o_main_navbar .o_menu_toggle").toHaveCount(1);
        expect(".o_main_navbar .o_menu_toggle").toHaveAttribute("title", "Apps");
        expect(".o_main_navbar .o_menu_toggle").toHaveAttribute("aria-label", "Apps");
        expect(".o_main_navbar .o_menu_toggle i.fa-bars").toHaveCount(1);
    });

    test.tags("mobile");
    test("All Apps in the sidebar opens the full-screen app menu with search", async () => {
        await mountOnScreen();
        await contains(".o_menu_toggle").click();
        expect(queryAll(".o_app_menu_sidebar", IN_BODY)).toHaveCount(1);

        await tapAllApps();

        expect(queryAll(".o_app_menu_sidebar", IN_BODY)).toHaveCount(0, {
            message: "the sidebar steps aside",
        });
        expect(".o_viin_home_menu.o_viin_home_overlay .o_viin_home_search_input").toHaveCount(1);
        expect(".o_viin_home_overlay a.o_app[data-menu-xmlid='app.alpha']").toHaveCount(1);
        expect(".o_viin_home_overlay a.o_app[data-menu-xmlid='app.bravo']").toHaveCount(1);
        expect(".o_action_manager .o_list_view").toHaveCount(1, {
            message: "the screen the user was on stays mounted underneath",
        });
    });

    test.tags("mobile");
    test("typing in the app menu filters the apps and choosing one opens it and closes the menu", async () => {
        await mountOnScreen();
        await contains(".o_menu_toggle").click();
        await tapAllApps();
        patchWithCleanup(getService("menu"), {
            selectMenu: (menu) => expect.step(`opened:${menu.xmlid}`),
        });

        await contains(".o_viin_home_search_input").edit("bravo", { confirm: false });
        await animationFrame();
        expect(".o_viin_home_menu a.o_app").toHaveCount(1);
        expect(".o_viin_home_menu a.o_app").toHaveText(/Bravo Widgets/);

        await contains(".o_viin_home_menu a.o_app").click();

        expect.verifySteps(["opened:app.bravo"]);
        expect(".o_viin_home_menu").toHaveCount(0, { message: "choosing an app closes the menu" });
    });

    test.tags("mobile");
    test("the toggle closes the app menu and returns to the screen it covers", async () => {
        await mountOnScreen();
        await contains(".o_menu_toggle").click();
        await tapAllApps();
        expect(".o_viin_home_overlay").toHaveCount(1);

        await contains(".o_menu_toggle").click();
        await animationFrame();

        expect(".o_viin_home_menu").toHaveCount(0, { message: "the app menu is put away" });
        expect(queryAll(".o_app_menu_sidebar", IN_BODY)).toHaveCount(0, {
            message: "and no sidebar opens on top of the screen",
        });
        expect(".o_action_manager .o_list_view").toHaveCount(1);
    });

    test.tags("mobile");
    test("with the app menu as the boot screen the toggle opens the sidebar and keeps the menu", async () => {
        await mountOnBootLanding();

        await contains(".o_menu_toggle").click();
        await animationFrame();

        expect(queryAll(".o_app_menu_sidebar", IN_BODY)).toHaveCount(1, {
            message: "the sidebar opens",
        });
        expect(".o_viin_home_menu").toHaveCount(1, {
            message: "the app menu stays - no blank page behind the sidebar",
        });
        expect(".o_viin_home_search_input").toHaveCount(1);
    });

    test.tags("mobile");
    test("with the app menu reached over a screen the toggle returns to that screen", async () => {
        await mountOnScreen();
        await getService("action").doAction("viin_home_menu");
        await animationFrame();
        expect(".o_action_manager .o_viin_home_menu:not(.o_viin_home_overlay)").toHaveCount(1);
        expect(".o_action_manager .o_list_view").toHaveCount(0);

        await contains(".o_menu_toggle").click();
        await animationFrame();

        expect(".o_viin_home_menu").toHaveCount(0);
        expect(queryAll(".o_app_menu_sidebar", IN_BODY)).toHaveCount(0, {
            message: "something is behind the app menu, so no sidebar opens",
        });
        expect(".o_action_manager .o_list_view").toHaveCount(1);
    });

    test.tags("mobile");
    test("All Apps tapped while the boot app menu is still loading opens no overlay and the toggle keeps working", async () => {
        patchWithCleanup(transitionConfig, { disabled: true });
        const landingReady = new Deferred();
        onRpc("mail.activity", "search_count", async () => {
            await landingReady;
            return 0;
        });
        onRpc("res.users", "read", () => [{ viin_home_app_order: false }]);
        redirect("/odoo");
        await mountWebClient();
        patchWithCleanup(getService("overlay"), {
            add(component, ...args) {
                if (component.name === "ViinHomeMenu") {
                    expect.step("app menu panel requested");
                }
                return super.add(component, ...args);
            },
        });
        await contains(".o_menu_toggle").click();
        await tapAllApps();
        expect(queryAll(".o_app_menu_sidebar", IN_BODY)).toHaveCount(0);
        expect.verifySteps([]);
        expect(".o_viin_home_overlay").toHaveCount(0, {
            message: "no screen is behind the loading app menu, so nothing is opened over it",
        });

        landingReady.resolve();
        await animationFrame();
        await animationFrame();

        expect(".o_viin_home_overlay").toHaveCount(0);
        expect(".o_action_manager .o_viin_home_menu").toHaveCount(1);
        await contains(".o_menu_toggle").click();
        expect(queryAll(".o_app_menu_sidebar", IN_BODY)).toHaveCount(1, {
            message: "the next tap on the toggle opens the sidebar",
        });
    });

    test.tags("mobile");
    test("All Apps over the boot app menu closes the sidebar without stacking a second menu", async () => {
        await mountOnBootLanding();
        await contains(".o_menu_toggle").click();

        await tapAllApps();

        expect(queryAll(".o_app_menu_sidebar", IN_BODY)).toHaveCount(0);
        expect(".o_viin_home_menu").toHaveCount(1, {
            message: "still exactly one app menu: the boot screen, no overlay on top of it",
        });
        expect(".o_viin_home_overlay").toHaveCount(0);
    });

    test.tags("desktop");
    test("on a wide screen the apps button still opens the app menu and there is no mobile toggle", async () => {
        await mountOnScreen();

        expect(".o_menu_toggle").toHaveCount(0);
        await contains(".o_navbar_apps_menu .o_viin_apps_home").click();
        expect(".o_viin_home_menu.o_viin_home_overlay .o_viin_home_search_input").toHaveCount(1);

        await contains(".o_navbar_apps_menu .o_viin_apps_home").click();
        expect(".o_viin_home_menu").toHaveCount(0);
        expect(".o_action_manager .o_list_view").toHaveCount(1);
    });
});
