import { expect, test } from "@odoo/hoot";
import {
    defineModels,
    fields,
    getService,
    models,
    mountWithCleanup,
    webModels,
} from "@web/../tests/web_test_helpers";
import { WebClient } from "@web/webclient/webclient";

const { ResCompany, ResPartner, ResUsers } = webModels;

const DIALOG = "@web/core/dialog/dialog";
const ACTION_DIALOG = "@web/webclient/actions/action_dialog";
const BRAND_DIALOG = "@viin_brand_web/core/dialog/dialog";

class Shop extends models.Model {
    name = fields.Char();

    _views = {
        form: `<form><field name="name"/></form>`,
    };
}

defineModels([Shop, ResCompany, ResPartner, ResUsers]);

/**
 * Evaluates the given modules on a private copy of the module registry, one after the other, the
 * way the backend bundle does it: core's dialogs first, the brand file after them. The Hoot loader
 * orders modules by their dependencies and would run the brand file first, which hides the defect.
 *
 * @param {string[]} names
 * @returns {Map<string, object>} the freshly evaluated modules
 */
function evaluateInOrder(names) {
    const { factories, modules } = odoo.loader;
    const registry = new Map(modules);
    for (const name of [DIALOG, ACTION_DIALOG, BRAND_DIALOG]) {
        registry.delete(name);
    }
    const require = (name) => {
        if (!registry.has(name)) {
            registry.set(name, factories.get(name).fn(require));
        }
        return registry.get(name);
    };
    for (const name of names) {
        require(name);
    }
    return registry;
}

test("the action dialog default title is branded when core is evaluated first and the brand file after it", () => {
    const registry = evaluateInOrder([ACTION_DIALOG, BRAND_DIALOG]);

    expect(registry.get(ACTION_DIALOG).ActionDialog.defaultProps.title).toBe("Viindoo");
});

test("a dialog opened by an action without a name reads the Viindoo brand, not Odoo", async () => {
    await mountWithCleanup(WebClient);
    await getService("action").doAction({
        type: "ir.actions.act_window",
        res_model: "shop",
        target: "new",
        views: [[false, "form"]],
    });

    expect(".o_technical_modal .modal-title").toHaveText("Viindoo");
});
