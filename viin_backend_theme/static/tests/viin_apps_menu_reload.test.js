/** @odoo-module **/

import { animationFrame, describe, expect, test } from "@odoo/hoot";
import { Deferred } from "@odoo/hoot-mock";
import {
    contains,
    defineActions,
    defineMenus,
    defineModels,
    fields,
    models,
    mountWebClient,
    onRpc,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import { defineMailModels } from "@mail/../tests/mail_test_helpers";
import { redirect } from "@web/core/utils/urls";
import { config as transitionConfig } from "@web/core/transition";

// Business rule: a user who opens the app menu from the navbar apps button gets the app menu with
// its tiles, whatever the screen behind it was still doing. Clicking the app brand reloads the
// current app; opening the apps button before that reload has finished must not make the reload's
// completion take the menu away - the tiles are there to pick the next app from.
//
// Assertions are on observable DOM only: whether the overlay and its app tiles are on screen.

defineMailModels();

class ReloadGadget extends models.Model {
    _name = "reload.menu.gadget";

    name = fields.Char({ string: "Name" });

    _records = [{ id: 1, name: "Gadget" }];

    _views = {
        list: `<list><field name="name"/></list>`,
        form: `<form><sheet><field name="name"/></sheet></form>`,
        search: `<search/>`,
    };
}

defineModels([ReloadGadget]);
defineActions([
    {
        id: 9501,
        xml_id: "reload_menu_gadget_action",
        name: "Gadgets",
        type: "ir.actions.act_window",
        res_model: "reload.menu.gadget",
        views: [[false, "list"]],
    },
]);
defineMenus([
    { id: 9502, appID: 9502, name: "Alpha Gadgets", xmlid: "app.alpha", actionID: 9501 },
    { id: 9503, appID: 9503, name: "Bravo Widgets", xmlid: "app.bravo", actionID: 9501 },
]);

describe("apps button while an app reloads", () => {
    test.tags("desktop");
    test("the app menu opened during an app reload stays open and shows the app tiles", async () => {
        patchWithCleanup(transitionConfig, { disabled: true });
        // A gate is awaited by the request it holds; `null` lets the request through at once.
        let listGate = null;
        let menuGate = null;
        onRpc("reload.menu.gadget", "web_search_read", async () => {
            await listGate;
        });
        onRpc("mail.activity", "search_count", async () => {
            await menuGate;
            return 0;
        });
        onRpc("res.users", "read", async () => {
            await menuGate;
            return [{ viin_home_app_order: false }];
        });
        redirect("/odoo/action-9501");
        await mountWebClient();
        await animationFrame();
        expect(".o_action_manager .o_list_view").toHaveCount(1, {
            message: "the test needs a real screen to stand on",
        });

        // The app starts reloading, and the user opens the app menu before it has finished.
        listGate = new Deferred();
        menuGate = new Deferred();
        await contains(".o_menu_brand").click();
        await contains(".o_navbar_apps_menu .o_viin_apps_home").click();
        // The reload finishes while the app menu is still loading its own data.
        listGate.resolve();
        await animationFrame();
        menuGate.resolve();
        await animationFrame();
        await animationFrame();

        expect(".o_viin_home_overlay").toHaveCount(1, {
            message: "the reload finishing must not close the app menu",
        });
        expect(".o_viin_home_overlay .o_app[data-menu-xmlid='app.alpha']").toHaveCount(1);
        expect(".o_viin_home_overlay .o_app[data-menu-xmlid='app.bravo']").toHaveCount(1);
    });
});
