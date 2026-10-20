/** @odoo-module **/

import { animationFrame, describe, expect, mockDate, queryOne, test } from "@odoo/hoot";
import { registry } from "@web/core/registry";
import {
    contains,
    defineActions,
    defineMenus,
    defineModels,
    fields,
    getService,
    models,
    mountWebClient,
    mountWithCleanup,
    onRpc,
    patchWithCleanup,
    serverState,
} from "@web/../tests/web_test_helpers";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { browser } from "@web/core/browser/browser";
import { redirect } from "@web/core/utils/urls";
import { config as transitionConfig } from "@web/core/transition";

// Four defects of the flat home menu / apps button that predate the 18.0 forward-port:
//   1. the search box promised "apps, records, actions" but only ever matched app names, so typing a
//      menu item ("operation types") found nothing - on every screen size, since there is no other
//      path (the command palette is a separate, keyboard-only surface);
//   2. Back/Forward with the menu open over a screen changed the URL and the navbar but left the menu
//      on screen;
//   3. the date line followed the browser's locale, not the user's language;
//   4. the desktop apps button had no accessible name.
// Every assertion is on observable DOM, or on the menu service being asked to open something.

defineMailModels();

class FixGadget extends models.Model {
    _name = "home.fix.gadget";

    name = fields.Char({ string: "Name" });

    _records = [{ id: 1, name: "Gadget" }];

    _views = {
        list: `<list><field name="name"/></list>`,
        form: `<form><sheet><field name="name"/></sheet></form>`,
        search: `<search/>`,
    };
}

defineModels([FixGadget]);
defineActions([
    {
        id: 9501,
        xml_id: "home_fix_gadget_action",
        name: "Gadgets",
        type: "ir.actions.act_window",
        res_model: "home.fix.gadget",
        views: [
            [false, "list"],
            [false, "form"],
        ],
    },
]);
defineMenus([
    {
        id: 9502,
        appID: 9502,
        name: "Inventory",
        xmlid: "app.inventory",
        actionID: 9501,
        children: [
            {
                id: 9503,
                appID: 9502,
                name: "Configuration",
                children: [
                    { id: 9504, appID: 9502, name: "Operation Types", actionID: 9501 },
                    { id: 9505, appID: 9502, name: "Credit Notes", actionID: 9501 },
                ],
            },
        ],
    },
    { id: 9506, appID: 9506, name: "Sales", xmlid: "app.sales", actionID: 9501 },
]);

function stubHomeRpcs() {
    onRpc("mail.activity", "search_count", () => 0);
    onRpc("res.users", "read", () => [{ viin_home_app_order: false }]);
}

async function mountHomeMenu() {
    stubHomeRpcs();
    const ViinHomeMenu = registry.category("actions").get("viin_home_menu");
    await mountWithCleanup(ViinHomeMenu, { props: {} });
    await animationFrame();
}

async function mountOnScreen() {
    patchWithCleanup(transitionConfig, { disabled: true });
    stubHomeRpcs();
    redirect("/odoo/action-9501");
    await mountWebClient();
    await animationFrame();
    expect(".o_action_manager .o_list_view").toHaveCount(1);
}

describe("home menu search finds menu items", () => {
    test("typing a menu item name lists it under its app and opens it", async () => {
        await mountHomeMenu();
        patchWithCleanup(getService("menu"), {
            selectMenu: (menu) => expect.step(`opened:${menu.id}`),
        });

        await contains(".o_viin_home_search_input").edit("operation types", { confirm: false });
        await animationFrame();

        expect(".o_viin_home_grid a.o_app").toHaveCount(0, { message: "no app is called that" });
        expect(".o_viin_home_menu_item").toHaveCount(1);
        expect(".o_viin_home_menu_item").toHaveText(/Operation Types/);
        expect(".o_viin_home_menu_item_path").toHaveText("Inventory / Configuration");
        expect(".o_viin_home_empty").toHaveCount(0);

        await contains(".o_viin_home_menu_item").click();

        expect.verifySteps(["opened:9504"]);
    });

    test("Enter opens the first menu item when no app matches", async () => {
        await mountHomeMenu();
        patchWithCleanup(getService("menu"), {
            selectMenu: (menu) => expect.step(`opened:${menu.id}`),
        });

        await contains(".o_viin_home_search_input").edit("credit notes", { confirm: false });
        await animationFrame();
        await contains(".o_viin_home_search_input").press("Enter");

        expect.verifySteps(["opened:9505"]);
    });

    test("an app match still lists the app tile, and nothing matching shows the empty state", async () => {
        await mountHomeMenu();

        await contains(".o_viin_home_search_input").edit("sales", { confirm: false });
        await animationFrame();
        expect(".o_viin_home_grid a.o_app").toHaveCount(1);

        await contains(".o_viin_home_search_input").edit("zzzzqq", { confirm: false });
        await animationFrame();
        expect(".o_viin_home_grid a.o_app").toHaveCount(0);
        expect(".o_viin_home_menu_item").toHaveCount(0);
        expect(".o_viin_home_empty").toHaveCount(1);
    });

    test("words match the entry or its app path, never mere letters in order", async () => {
        await mountHomeMenu();

        // "inventory" is the APP of Operation Types; both words are typed, in any order.
        await contains(".o_viin_home_search_input").edit("types inventory", { confirm: false });
        await animationFrame();
        expect(".o_viin_home_menu_item").toHaveCount(1);
        expect(".o_viin_home_menu_item").toHaveText(/Operation Types/);

        // o-t-y occur in order inside "Operation Types" but are not a word of it.
        await contains(".o_viin_home_search_input").edit("oty", { confirm: false });
        await animationFrame();
        expect(".o_viin_home_menu_item").toHaveCount(0);
        expect(".o_viin_home_empty").toHaveCount(1);
    });

    test("the search box only promises what it does", async () => {
        await mountHomeMenu();

        const placeholder = queryOne(".o_viin_home_search_input").getAttribute("placeholder");
        expect(placeholder?.length > 0).toBe(true, { message: "the box has a placeholder" });
        expect(placeholder).not.toMatch(/records|actions/i, {
            message: "it must not promise what the search does not find",
        });
    });
});

describe("home menu overlay and the browser's Back button", () => {
    /** From the list, open the record: that pushes a history entry the Back button can return to. */
    async function openRecord() {
        await contains(".o_data_row .o_data_cell").click();
        await animationFrame();
        expect(".o_action_manager .o_form_view").toHaveCount(1);
    }

    test("Back from the home menu as a screen replaces it with the previous page", async () => {
        await mountOnScreen();
        await getService("action").doAction("viin_home_menu");
        await animationFrame();
        expect(".o_action_manager .o_viin_home_menu").toHaveCount(1);
        expect(".o_action_manager .o_list_view").toHaveCount(0);

        browser.history.back();
        await animationFrame();
        await animationFrame();

        expect(".o_viin_home_menu").toHaveCount(0);
        expect(".o_action_manager .o_list_view").toHaveCount(1, {
            message: "the page the URL went back to is on screen",
        });
    });

    test.tags("desktop");
    test("Back closes the menu opened over a screen and shows the previous page (desktop)", async () => {
        await mountOnScreen();
        await openRecord();
        await contains(".o_navbar_apps_menu .o_viin_apps_home").click();
        expect(".o_viin_home_overlay").toHaveCount(1);

        browser.history.back(); // the browser's Back button: popstate, answered by the router
        await animationFrame();
        await animationFrame();

        expect(".o_viin_home_menu").toHaveCount(0);
        expect(".o_action_manager .o_list_view").toHaveCount(1, {
            message: "the page the URL went back to is on screen",
        });
    });

    test.tags("mobile");
    test("Back closes the menu opened over a screen and shows the previous page (phone)", async () => {
        await mountOnScreen();
        await openRecord();
        await contains(".o_menu_toggle").click();
        await contains(".o_app_menu_sidebar a.btn-primary", { root: document.body }).click();
        await animationFrame();
        expect(".o_viin_home_overlay").toHaveCount(1);

        browser.history.back();
        await animationFrame();
        await animationFrame();

        expect(".o_viin_home_menu").toHaveCount(0);
        expect(".o_action_manager .o_list_view").toHaveCount(1);
    });
});

describe("home menu header", () => {
    test("the date line follows the user's language, not the browser's", async () => {
        mockDate("2026-10-20 10:00:00");
        // The user's language, as the localization service reads it at start-up, is what sets
        // luxon's default locale; the browser's own locale stays English.
        serverState.lang = "fr";
        await mountHomeMenu();
        expect(".o_viin_home_subtitle").toHaveText(/mardi 20 octobre/i);
    });
});

describe("desktop apps button", () => {
    test.tags("desktop");
    test("has an accessible name", async () => {
        await mountOnScreen();

        expect(".o_navbar_apps_menu .o_viin_apps_home").toHaveCount(1);
        expect(".o_navbar_apps_menu .o_viin_apps_home").toHaveAttribute("aria-label", "Apps");
        expect(".o_navbar_apps_menu .o_viin_apps_home").toHaveAttribute("title", "Apps", {
            message: "tooltip and accessible name are the same word",
        });
    });
});
