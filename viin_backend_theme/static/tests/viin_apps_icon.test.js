import { animationFrame, describe, expect, test } from "@odoo/hoot";
import { queryOne } from "@odoo/hoot-dom";
import {
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

// Business rule: the control that opens the app menu is the same glyph at the same size on a desktop
// and on a phone: the `apps` glyph of the icon font at the `fs-2` step of core's font scale, big
// enough to read on the navbar. The size comes from the font-scale utility of the icon, not from a
// pixel rule, so it is asserted as a ratio to the root font size: core's own glyph (1em of the
// navbar entry) is about 1.05 times the root, the glyph must be clearly above it.

defineMailModels();

class IconGadget extends models.Model {
    _name = "icon.menu.gadget";

    name = fields.Char({ string: "Name" });

    _records = [{ id: 1, name: "Gadget" }];

    _views = {
        list: `<list><field name="name"/></list>`,
        form: `<form><sheet><field name="name"/></sheet></form>`,
        search: `<search/>`,
    };
}

defineModels([IconGadget]);
defineActions([
    {
        id: 9601,
        xml_id: "icon_menu_gadget_action",
        name: "Gadgets",
        type: "ir.actions.act_window",
        res_model: "icon.menu.gadget",
        views: [[false, "list"]],
    },
]);
defineMenus([{ id: 9602, appID: 9602, name: "Alpha Gadgets", xmlid: "app.alpha", actionID: 9601 }]);

async function mountOnScreen() {
    patchWithCleanup(transitionConfig, { disabled: true });
    onRpc("mail.activity", "search_count", () => 0);
    onRpc("res.users", "read", () => [{ viin_home_app_order: false }]);
    redirect("/odoo/action-9601");
    await mountWebClient();
    await animationFrame();
}

function expectGridGlyph(selector) {
    expect(`${selector} i.oi.fs-2[data-icon='apps']`).toHaveCount(1, {
        message: "the control shows the apps glyph through the fs-2 utility",
    });
    const icon = queryOne(`${selector} i.oi`);
    const ratio =
        parseFloat(getComputedStyle(icon).fontSize) /
        parseFloat(getComputedStyle(document.documentElement).fontSize);
    expect(ratio).toBeGreaterThan(1.25, {
        message: "the glyph is clearly larger than the former 1em glyph of the entry",
    });
}

describe("navbar apps control icon", () => {
    test.tags("desktop");
    test("the apps button shows the apps glyph at the fs-2 size", async () => {
        await mountOnScreen();

        expect(".o_main_navbar .o_navbar_apps_menu .o_viin_apps_home").toHaveCount(1);
        expectGridGlyph(".o_main_navbar .o_navbar_apps_menu .o_viin_apps_home");
    });

    test.tags("mobile");
    test("the small-screen toggle shows the same glyph at the same size", async () => {
        await mountOnScreen();

        expect(".o_main_navbar .o_menu_toggle").toHaveCount(1);
        expectGridGlyph(".o_main_navbar .o_menu_toggle");
        expect(".o_main_navbar .o_menu_toggle i.oi[data-icon='menu']").toHaveCount(0);
    });
});
